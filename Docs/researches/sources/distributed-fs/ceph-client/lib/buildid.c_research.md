# sources/distributed-fs/ceph-client/lib/buildid.c

## Purpose

`sources/distributed-fs/ceph-client/lib/buildid.c` parses GNU build IDs from ELF files, VMAs, raw note buffers, and the running kernel note section. It supports both faultable and no-fault contexts through a small reader abstraction.

## Important APIs, Types, and Functions

Important exported or visible APIs are `freader_init_from_file`, `freader_init_from_mem`, `freader_fetch`, `freader_cleanup`, `build_id_parse_nofault`, `build_id_parse`, `build_id_parse_file`, `build_id_parse_buf`, `vmlinux_build_id`, and `init_vmlinux_build_id`. Internal helpers include `freader_get_folio`, `freader_put_folio`, `parse_build_id`, `get_build_id_32`, `get_build_id_64`, and `__build_id_parse`.

## Control Flow

File readers either use `__kernel_read()` when faults are allowed or page-cache folio lookup and `kmap_local_folio()` when no faults are allowed. Memory readers return direct pointers after bounds checks. ELF parsing first fetches enough of the ELF header to validate magic and executable/shared-object type, dispatches by ELF class, caps program header iteration at `MAX_PHDR_CNT`, then scans `PT_NOTE` segments. Note parsing walks aligned `Elf32_Nhdr` records, checks for name `GNU`, type `NT_GNU_BUILD_ID` value 3, nonzero descriptor length within `BUILD_ID_SIZE_MAX`, copies the descriptor, and zero-fills the remainder.

## State and Persistence Behavior

`struct freader` owns transient mapping state for one parse operation and must release mapped folios with `freader_cleanup()`. The only persistent kernel state is optional `vmlinux_build_id` under `CONFIG_STACKTRACE_BUILD_ID` or `CONFIG_VMCORE_INFO`, initialized from linker note bounds during init.

## Dependencies and Integration Points

Dependencies include ELF headers, VFS files, page cache folios, local kmap, secretmem rejection, overflow helpers, and kernel note linker symbols. Users include perf, stacktrace, vmcore, BPF, or diagnostics code that needs build IDs without necessarily faulting pages in.

## Risks and Edge Cases

No-fault parsing fails if relevant file pages are absent or not uptodate. Secretmem mappings are intentionally rejected. Pointer results from `freader_fetch()` are invalidated by later fetches, so fields are copied with `READ_ONCE`. Arithmetic overflow in offsets, note bounds, and program header ranges must be rejected. Endianness conversion is not performed here; it assumes native ELF headers in the contexts using it.

## Test Signals

Tests should cover 32-bit and 64-bit ELF build IDs, missing notes, non-ELF buffers, unsupported file types, malformed note sizes, overlong descriptors, page-boundary fetches, no-fault cache-miss failure, faultable file parsing success, secretmem rejection, and `init_vmlinux_build_id()` on builds with note sections.

## Read Coverage

Source read size: 407 lines, 10657 bytes.
