# sources/distributed-fs/lustre-release/lustre/llite/llite_mmap.c

## Purpose

`llite_mmap.c` implements llite's VFS mmap integration. It installs Lustre-specific `vm_operations_struct` callbacks for page faults, page-mkwrite, VMA open, and VMA close; translates VM ranges into Lustre LDLM extent policies; initializes CLIO fault operations; cooperates with the persistent client cache; updates mmap/fault/write statistics; and handles races among page faults, truncation, page invalidation, lock cancellation, and dirty-page writeback.

The file is the entry point for memory-mapped reads and writes on Lustre files. It must preserve Linux VM semantics while acquiring Lustre locks and coordinating object-client I/O.

## Important APIs, Types, And Functions

- `policy_from_vma()`: converts a virtual address and byte count inside a VMA into an LDLM extent policy based on `vm_start` and `vm_pgoff`.
- `our_vma()`: scans VMAs under the caller-held mmap lock for a shared VMA using llite's `ll_file_vm_ops`.
- `ll_fault_io_init()`: creates and initializes a CLIO `CIT_FAULT` operation for a page index. It rejects nolock files, binds the fault to the inode CL object, records mmap read pattern flags, marks lock requirements mandatory, and stores `ll_file_data` in the VVP IO state.
- `__ll_page_mkwrite()`: CLIO-backed implementation for making an mmap page writable. It blocks all signals except `SIGKILL`/`SIGTERM`, runs the fault write operation, locks the page, detects truncation or dirty/writeback races, marks data modified, retries when needed, and delays after `-ENODATA` to reduce contention livelock.
- `to_fault_error()`: maps internal negative errors to `VM_FAULT_*` values.
- `ll_filemap_fault()`: wrapper around `filemap_fault()` that retries a SIGBUS result when `lli_page_inv_lock` changed during the fault.
- `__ll_fault()`: main read fault implementation. It tries fast page-cache fault when `LL_SBI_FAST_READ` is enabled, falls back to CLIO mandatory-lock fault, tracks CL mmap context, and propagates VM fault flags and pages.
- `ll_fault()`: public `.fault` callback. It gives PCC first chance, blocks nonfatal signals, bounds offsets by `MAX_LFS_FILESIZE`, retries pages invalidated under heavy contention, updates read/fault stats, and logs trace data.
- `ll_page_mkwrite()`: public `.page_mkwrite` callback. It gives PCC first chance, updates file time, loops over retryable write faults, maps errors to VM fault codes, and tallies write/mkwrite stats.
- `ll_vm_open()` and `ll_vm_close()`: VMA lifecycle callbacks. They increment/decrement `vvp_object::vob_mmap_cnt` for normal Lustre mappings or delegate to PCC VMA handlers for cached mappings.
- `ll_file_mmap()`: VFS `.mmap` implementation. It rejects nolock files, asks PCC to map cached files, calls `generic_file_mmap()`, installs llite VM ops, opens the VMA, glimpses size for non-PCC mappings, and tallies mmap latency.

## Control Flow

`ll_file_mmap()` is called when a file is mapped. It first rejects files opened with lock-ignoring semantics, then asks PCC whether the mapping should be served from a local cache copy. After `generic_file_mmap()` succeeds, it replaces `vma->vm_ops` with llite's operations, calls the open callback to track mmap count or PCC state, and performs a glimpse-size update for non-PCC mappings.

On read fault, `ll_fault()` delegates to PCC if the VMA is PCC-backed. Otherwise it blocks nonfatal signals and checks the page offset against the Lustre maximum file size. `__ll_fault()` then attempts a fast path when fast read is enabled: it temporarily forces retry-nowait semantics, adds an `LCC_MMAP` context without a CLIO operation, and calls `ll_filemap_fault()`. If the page cache cannot satisfy the fault cleanly, it initializes a CLIO `CIT_FAULT` operation, attaches VVP fault state, adds a mmap CL context, runs `cl_io_loop()`, removes the context, and returns the resulting page or fault flags. The wrapper verifies that a returned page is still mapped and has Lustre private state, retrying and eventually warning under persistent contention.

On write fault, `ll_page_mkwrite()` gives PCC first chance, updates file timestamps, and loops on `__ll_page_mkwrite()` while it reports a retry race. The internal function creates a write fault CLIO operation, blocks nonfatal signals, runs CLIO, locks the VM page, handles pages truncated out from under the fault, detects pages cleaned by ptlrpcd between unlock and mkwrite, and sets `LLIF_DATA_MODIFIED` on success. Public error mapping returns `VM_FAULT_LOCKED`, `VM_FAULT_NOPAGE`, `VM_FAULT_OOM`, `VM_FAULT_RETRY`, or `VM_FAULT_SIGBUS`.

VMA open and close maintain `vob_mmap_cnt` so lock cancellation and cache-pressure logic can account for active mmaps. PCC-backed VMAs use `vm_private_data` and are delegated to PCC callbacks.

## State And Persistence Behavior

The file does not persist data itself, but mmap writes modify page-cache and CL object state that is later flushed to OSTs. It updates inode flags (`LLIF_DATA_MODIFIED`), VVP object mmap counters, file timestamps through `file_update_time()`, VFS page state, CLIO page associations, PCC VMA state, and llite read/write/fault/mmap statistics.

Fault paths rely on `lli_page_inv_lock` to detect invalidation racing with filemap faults and on page private state to reject pages invalidated or truncated during the fault. The mmap count helps retain or avoid cancelling locks covering mapped ranges.

## Dependencies And Integration Points

`llite_mmap.c` integrates Linux VM fault APIs, mmap locking compatibility, filemap fault handling, page locking, signal masks, generic file mmap, and VMA iterators with Lustre CLIO (`cl_io_init`, `cl_io_loop`, `cl_io_fini`), VVP environment state, LDLM lock policy, PCC mmap/fault/mkwrite hooks, llite file-private data, inode feature flags, and lprocfs/rw statistics.

It depends on `ll_file_nolock()`, `ll_i2info()`, `ll_i2sbi()`, `ll_glimpse_size()`, `ll_cl_add()`, `ll_cl_remove()`, `ll_rw_stats_tally()`, and `ll_stats_ops_tally()` from the broader llite layer.

## Risks And Edge Cases

- Fault handling must never return an unlocked page as `VM_FAULT_LOCKED`; assertions check this but race coverage matters.
- The fast fault path temporarily mutates `vmf->flags`; it must restore caller-visible retry flags correctly.
- Page invalidation during `filemap_fault()` can otherwise produce a false SIGBUS, hence the seqlock retry wrapper.
- `page_mkwrite` races with truncation, ptlrpcd cleaning, and lock cancellation. It uses retry and `-ENODATA` delay to avoid tight livelock.
- Signal masking intentionally allows only administrative termination signals during fault/mkwrite.
- PCC-backed and normal mappings split behavior through `vm_private_data`; incorrect state can misroute VMA open/close or fault handling.
- `our_vma()` depends on caller-held mmap lock and compatibility iterator semantics.

## Test Signals

Useful tests include mmap read faults satisfied from page cache and CLIO, fast-read fallback on retry/error, mmap write faults under concurrent writeback, truncate racing with read and write faults, page invalidation producing SIGBUS retry instead of user-visible failure, PCC-backed mmap/fault/mkwrite, nolock files returning `-EOPNOTSUPP`, max-file-size SIGBUS, VMA open/close mmap count balance, heavy contention warning paths, and stats increments for mmap, fault, and mkwrite.
