# subset-b-005606 Research

Grouped research for Linux binary-format loader and Btrfs support files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_elf_fdpic.c -->
# sources/distributed-fs/ceph-client/fs/binfmt_elf_fdpic.c

## Purpose
Implements the Linux binary-format handler for FDPIC ELF executables and interpreters, including NOMMU support and optional ELF core dump generation. It is derived from the regular ELF loader but emits FDPIC load maps so position-independent executables and dynamic linkers can discover the actual per-segment load addresses selected by the kernel.

## Important APIs, Types, And Functions
The file registers `elf_fdpic_format` with `register_binfmt()` at `core_initcall()` time and unregisters it at module exit. Its primary entry point is `load_elf_fdpic_binary(struct linux_binprm *bprm)`. Validation is split across `is_elf()`, architecture hooks such as `elf_check_arch()`, `elf_check_fdpic()`, and `elf_check_const_displacement()`, and program-header parsing in `elf_fdpic_fetch_phdrs()`.

Mapping is performed by `elf_fdpic_map_file()`, which builds an `elf_fdpic_loadmap` and delegates to `elf_fdpic_map_file_by_direct_mmap()` or, for NOMMU constant-displacement cases, `elf_fdpic_map_file_constdisp_on_uclinux()`. `create_elf_fdpic_tables()` builds the initial userspace stack, including `argv`, `envp`, `auxv`, platform strings, and executable/interpreter load maps. When `CONFIG_ELF_CORE` is enabled, `elf_fdpic_core_dump()` and helpers such as `fill_prstatus()`, `elf_dump_thread_status()`, and `elf_fdpic_dump_segments()` emit FDPIC-aware core files with load-map addresses in `elf_prstatus_fdpic`.

## Control Flow
`load_elf_fdpic_binary()` copies the ELF header from `bprm->buf`, rejects non-ELF, wrong-architecture, non-mmapable, or unsupported executable types, then reads program headers. It scans `PT_INTERP`; if present, it reads the interpreter path from the executable, opens it with `open_exec()`, applies `would_dump()` so unreadable executables affect dumpability, and reads the interpreter ELF header and program headers.

After deriving stack-executability policy from `PT_GNU_STACK`, it calls `begin_new_exec()` and switches personality flags, including `PER_LINUX_FDPIC` and `READ_IMPLIES_EXEC` when applicable. MMU builds lay out the address space with `elf_fdpic_arch_lay_out_mm()` and `setup_arg_pages()`; NOMMU builds allocate stack/brk memory explicitly. The executable and optional interpreter are mapped through `elf_fdpic_map_file()`, stack/auxiliary tables are created, architecture FDPIC register setup may run through `ELF_FDPIC_PLAT_INIT`, and `start_thread()` transfers control to the interpreter entry if one exists, otherwise to the executable entry.

`elf_fdpic_map_file()` counts `PT_LOAD` headers, allocates the load map, maps the segments, then resolves the runtime entry address, program-header address, and dynamic-section address by matching ELF virtual addresses against load-map entries. It also validates that a `PT_DYNAMIC` section has an integral `Elf_Dyn` array ending with a null tag. On MMU systems, adjacent load-map entries are coalesced when they have matching virtual and actual displacement.

The core dump path first gathers thread status notes, `PRPSINFO`, and `AUXV`, calculates ELF/program-header/note/data offsets, emits one `PT_NOTE` and one `PT_LOAD` header per dumpable VMA plus architecture extras, writes notes, dumps VMA ranges, and writes extended numbering metadata if the segment count exceeds `PN_XNUM`.

## State And Persistence
Runtime state is stored in the new process `mm_struct`: code/data/brk/stack ranges, `mm->saved_auxv`, and `mm->context.exec_fdpic_loadmap`/`interp_fdpic_loadmap`. The load maps are copied onto the userspace stack and referenced by both aux/register setup and core dumps. The loader changes process personality, binfmt ownership through `set_binfmt()`, interpreter file lifetime, and executable write-denial state. Persistent output only occurs when core dumping writes an ELF core file.

## Dependencies And Integration Points
The file sits in the generic `linux_binfmt` exec chain and depends on the VFS exec helpers, memory-management APIs (`vm_mmap()`, `setup_arg_pages()`, `clear_user()`), credentials for auxv UID/GID entries, coredump APIs, ELF architecture macros, and FDPIC ABI structures from `<linux/elf-fdpic.h>`. It integrates with interpreters via `PT_INTERP`, with security through `open_exec()`, `would_dump()`, and dumpability controls, and with debuggers through FDPIC-specific `NT_PRSTATUS` data in core files.

## Risks
Segment mapping is security-sensitive: wrong address arithmetic, BSS clearing, `MAP_FIXED` placement, or dynamic-section validation can corrupt the new image or expose stale memory. NOMMU paths rely on direct reads and anonymous allocations with different sharing assumptions from MMU Linux. The loader must free interpreter files, program headers, and load maps on all pre-commit error paths, while after `begin_new_exec()` failures occur after the old image is gone. Core dumps risk malformed offsets or missing FDPIC load-map data, which would break debuggers even when the crashing program ran correctly.

## Test Signals
Useful signals include successful execution of FDPIC binaries with and without `PT_INTERP`, NOMMU ET_DYN cases, `PT_GNU_STACK` executable/non-executable stack behavior, large or malformed program headers, invalid `PT_DYNAMIC` tables, BSS zeroing across partial pages, and interpreter dumpability transitions. Core dump tests should verify GDB can relocate FDPIC images using the emitted load-map addresses and that extended program-header numbering works for many VMAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_elf_fdpic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_flat.c -->
# sources/distributed-fs/ceph-client/fs/binfmt_flat.c

## Purpose
Implements the Linux `bFLT`/FLAT executable loader, primarily for embedded and NOMMU systems. It supports direct ROM text mappings, fully copied RAM mappings, optional compressed FLAT images, architecture-specific relocation formats, GOT relocation, and initial userspace stack construction.

## Important APIs, Types, And Functions
The file registers `flat_format` with the exec subsystem through `register_binfmt()`. `load_flat_binary()` is the binary-format entry point; it prepares argument-stack sizing, calls `load_flat_file()`, fills shared-library data pointers, sets the active binfmt, builds argument tables, finalizes exec, and calls `start_thread()`.

`struct lib_info` tracks the loaded program/library segments: `start_code`, `start_data`, `start_brk`, `text_len`, entry address, build date, and loaded state. `create_flat_tables()` builds `argc`, optional `argvp`/`envp`, `argv[]`, and `envp[]`. Optional `CONFIG_BINFMT_ZFLAT` adds `decompress_exec()` for gzip-wrapped text/data. `calc_reloc()` translates FLAT-relative offsets into runtime addresses, while `old_reloc()`, `skip_got_header()`, `flat_get_addr_from_rp()`, and `flat_put_addr_at_rp()` handle relocation variants.

## Control Flow
`load_flat_binary()` computes extra stack space for argument strings and pointer arrays, then delegates to `load_flat_file()`. `load_flat_file()` parses the `struct flat_hdr` from `bprm->buf`, validates magic, version, field sizes, compression flags, and `RLIMIT_DATA`, then calls `begin_new_exec()`. After that point it sets `PER_LINUX_32BIT`, runs `setup_new_exec()`, calculates mapping sizes, and chooses either a split text/data mapping or one combined RAM mapping.

For NOMMU non-RAM non-gzip images, text is mapped from the executable file and data/BSS/relocation space is allocated anonymously. Otherwise, text and data are copied or decompressed into an anonymous region, with MMU builds using kernel buffers for decompression copy-back. The loader fills `mm->start_code`, `end_code`, data bounds, `start_brk`, `brk`, and NOMMU `context.end_brk`.

Relocation then proceeds in two phases. GOTPIC entries at the start of the data segment are relocated in place until a `0xffffffff` terminator, with RISC-V GOT PLT headers skipped. Explicit relocation table entries are read, translated to pointer locations, the pointer value is fetched with architecture helpers, and nonzero values are relocated back into place. Old format builds use `old_reloc()`. Finally instruction cache is flushed, BSS/brk/stack slack is zeroed, arguments are installed via `setup_arg_pages()` or `transfer_args_to_stack()`, and execution starts at the relocated entry.

## State And Persistence
The loader constructs an entirely new process image and persists state in `current->mm` ranges plus the relocated text/data memory. It mutates user memory during data loading, relocation, BSS zeroing, and stack-table construction. `lib_info` is transient per exec. The only durable state is the running process image; no filesystem metadata is written.

## Dependencies And Integration Points
It depends on the generic exec path, `linux/flat.h` on-disk format, architecture hooks from `asm/flat.h`, VFS `read_code()` and `vm_mmap()`, zlib when compressed FLAT support is enabled, RLIMIT enforcement, cache flushing, and NOMMU `mm->context.end_brk`. Kconfig options change ABI details such as old format support, compressed image support, data-start-offset handling, and whether `argvp`/`envp` are placed on stack.

## Risks
The highest-risk areas are relocation validation, user-memory access, and size arithmetic. Corrupt headers can try to overflow mapping calculations, relocation offsets can target outside text/data, and compressed images can exercise less common copy paths. The code calls `begin_new_exec()` before mapping and relocation are complete, so late failures occur after the previous program image is committed away. The relocation path also sends `SIGSEGV` on invalid offsets, so tests must distinguish loader rejection from process kill semantics.

## Test Signals
Coverage should include valid uncompressed FLAT binaries, RAM and split text/data mappings, NOMMU argument-heavy executions, GOTPIC relocation, zero-valued relocation entries, RISC-V GOT header skipping, old format images when enabled, and zflat images with full-image and data-only compression. Negative tests should cover bad magic, unsupported revisions, oversized header fields, invalid relocation offsets, insufficient data limit, truncated compressed input, and BSS/stack zeroing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_flat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_misc.c -->
# sources/distributed-fs/ceph-client/fs/binfmt_misc.c

## Purpose
Implements `binfmt_misc`, a pseudo-filesystem and binary-format handler that lets users register interpreter rules matched by filename extension or file magic. It supports per-user-namespace handler instances, global fallback to ancestor namespaces, handler enable/disable/delete operations, and flags controlling argv preservation, opened binary fd passing, credential behavior, and interpreter-file pinning.

## Important APIs, Types, And Functions
The central type is `Node`, representing one registered handler. It stores list linkage, flags, magic or extension data, mask, interpreter path, entry name, dentry, optional pinned interpreter file, and a refcount protecting concurrent exec against removal.

Exec integration is through `misc_format.load_binary = load_misc_binary`. Handler lookup uses `load_binfmt_misc()`, `get_binfmt_handler()`, and `search_binfmt_handler()`. Registration and control are exposed through the `binfmt_misc` filesystem: `/register` via `bm_register_write()`, `/status` via `bm_status_read()`/`bm_status_write()`, and per-entry files via `bm_entry_read()`/`bm_entry_write()`. Parsing helpers include `create_entry()`, `scanarg()`, `check_special_flags()`, and `parse_command()`. Filesystem lifecycle is implemented by `bm_fill_super()`, `bm_get_tree()`, `bm_init_fs_context()`, `bm_evict_inode()`, and `bm_put_super()`.

## Control Flow
At initialization, `init_misc_binfmt()` registers the `binfmt_misc` filesystem and inserts the binfmt handler. Mounting the filesystem lazily allocates `struct binfmt_misc` for the current user namespace, initializes its entries list and lock, publishes it with release semantics to `user_ns->binfmt_misc`, resets `enabled`, and creates `status` and `register` files.

Writing to `/register` passes a delimited string of the form `:name:type:offset:magic:mask:interpreter:flags` to `create_entry()`. Magic rules parse a decimal offset, escaped magic, optional escaped mask, decode hex escapes in place, and validate the match range against `BINPRM_BUF_SIZE`. Extension rules validate the extension field. Flags `P`, `O`, `C`, and `F` set preserve-argv0, open-binary, credentials, and pinned-interpreter behavior. `F` opens the interpreter at registration time using the register file's credentials. `add_entry()` creates a persistent dentry and adds the node to the namespace handler list.

During exec, `load_misc_binary()` finds the applicable namespace instance by walking from current user namespace to ancestors. If enabled, it refcounts the first matching enabled handler under `entries_lock`. It rejects path-inaccessible binaries, optionally removes the original argv0, sets `have_execfd` for open-binary mode, pushes the original binary path and interpreter as arguments, changes `bprm->interp`, opens or clones the interpreter file, sets `bprm->interpreter`, optionally marks `execfd_creds`, and drops the handler reference.

Writes of `0`, `1`, and `-1` disable, enable, or delete entries/global state. Deletion removes list entries under the root inode lock and `entries_lock`, then uses recursive dentry removal. Inode eviction finally drops the node reference and closes pinned interpreter files when the last exec user releases it.

## State And Persistence
Handler state lives in memory under each user namespace's `binfmt_misc` object and is represented as pseudo-files in the mounted filesystem. It is not persisted across reboot or namespace teardown. Per-entry `Enabled` bits and global `misc->enabled` affect future execs. `MISC_FMT_OPEN_FILE` pins an interpreter `struct file`, so registration captures a specific opened executable until the handler is deleted and all users finish.

## Dependencies And Integration Points
The code integrates with the exec subsystem, user namespaces, VFS simple filesystem helpers, dcache persistent dentries, file opening and write-denial APIs, memory barriers for namespace publication, and `string_unescape_inplace()`/`bin2hex()` for user-visible rule encoding. It also depends on `BINPRM_BUF_SIZE` because magic matching only sees the initial exec buffer.

## Risks
Rule parsing is exposed to userspace and must reject malformed delimiters, names, escapes, offsets, and masks without leaking memory. Concurrency between exec and handler deletion is subtle: list locking, inode locking, refcounts, and dentry eviction must cooperate so a handler is neither used after free nor leaked. The `F` flag changes semantics by pinning an interpreter opened under registration credentials; mistakes here can cause stale interpreter execution or unexpected credential boundaries. Namespace fallback means handlers in an ancestor namespace can affect descendants unless a child mounts its own instance.

## Test Signals
Useful tests include registering extension and magic handlers; matching with and without masks; invalid register strings; enable, disable, and delete commands on entries and global status; concurrent exec while deleting a handler; user-namespace mounts and ancestor fallback; `P`, `O`, `C`, and `F` flag combinations; path-inaccessible binaries; and verifying `/status` and per-entry reads emit the expected state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_script.c -->
# sources/distributed-fs/ceph-client/fs/binfmt_script.c

## Purpose
Implements kernel support for scripts beginning with `#!`. It parses the shebang line, rewrites the exec argument vector so the interpreter runs with the script path and optional interpreter argument, and restarts exec with the interpreter file.

## Important APIs, Types, And Functions
The binary-format entry point is `load_script(struct linux_binprm *bprm)`, registered through `script_format` at `core_initcall()`. Small helpers `spacetab()`, `next_non_spacetab()`, and `next_terminator()` parse spaces, tabs, NULs, and the bounded `bprm->buf` shebang region.

## Control Flow
`load_script()` first rejects files whose first two bytes are not `#!`. It searches the initial exec buffer for a newline; when none exists, it allows truncated optional arguments but rejects a potentially truncated interpreter path by requiring a later space, tab, or NUL after the path. It trims trailing spaces/tabs, skips leading spaces/tabs after `#!`, identifies the interpreter path, and optionally identifies one interpreter argument.

If the original script path will be inaccessible after exec, it returns `-ENOENT` before opening the interpreter. It removes the script's original argv0, pushes the script path, optional interpreter argument, and interpreter name in reverse stack order, updates `bprm->interp` through `bprm_change_interp()`, opens the interpreter with `open_exec()`, and stores it in `bprm->interpreter` so the exec loop restarts on that file.

## State And Persistence
The function mutates only the in-flight `linux_binprm`: argument count, copied argument strings, interpreter path, and interpreter file. It deliberately writes temporary NUL bytes into `bprm->buf` to delimit parsed strings. No persistent filesystem state is changed.

## Dependencies And Integration Points
It depends on the generic exec argument stack helpers (`remove_arg_zero()`, `copy_string_kernel()`, `bprm_change_interp()`), VFS executable opening, and the exec loop's convention that setting `bprm->interpreter` restarts format probing. It also cooperates with `binfmt_misc`, which may update `bprm->interp` before the script handler sees an interpreter.

## Risks
The main risk is accepting a truncated interpreter path from a too-long shebang line. The code intentionally rejects that case while allowing truncated interpreter arguments. Another risk is path-inaccessible scripts, where interpreters would fail or behave differently after fd close-on-exec; the explicit `BINPRM_FLAGS_PATH_INACCESSIBLE` check prevents that. Argument order is subtle because exec argument strings are stored backward.

## Test Signals
Tests should cover normal shebangs, leading whitespace after `#!`, optional interpreter arguments, trailing spaces, no newline within `BINPRM_BUF_SIZE`, truncated interpreter path rejection, long optional argument truncation acceptance, inaccessible `/dev/fd` style script paths, and interpreter open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/binfmt_script.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bpf_fs_kfuncs.c -->
# sources/distributed-fs/ceph-client/fs/bpf_fs_kfuncs.c

## Purpose
Registers filesystem-related BPF kfuncs for BPF LSM programs. The file exposes controlled helpers for executable-file references, path resolution, extended attribute reads/writes/removals, cgroup xattr reads, and hook-specific lock-state discovery.

## Important APIs, Types, And Functions
Public kfuncs include `bpf_get_task_exe_file()` with acquire semantics, `bpf_put_file()` with release semantics, `bpf_path_d_path()`, `bpf_get_dentry_xattr()`, `bpf_get_file_xattr()`, `bpf_set_dentry_xattr()`, `bpf_remove_dentry_xattr()`, and, under `CONFIG_CGROUPS`, `bpf_cgroup_read_xattr()`. Internal locked variants `bpf_set_dentry_xattr_locked()` and `bpf_remove_dentry_xattr_locked()` are intended for LSM hooks where `d_inode` is already locked.

Permission helpers `bpf_xattr_read_permission()` and `bpf_xattr_write_permission()` constrain xattr namespaces. Registration uses `BTF_KFUNCS_START(bpf_fs_kfunc_set_ids)`, per-function flags such as `KF_ACQUIRE`, `KF_RELEASE`, `KF_RET_NULL`, and `KF_SLEEPABLE`, and `register_btf_kfunc_id_set()` in `bpf_fs_kfuncs_init()`. `bpf_fs_kfuncs_filter()` limits the set to BPF LSM programs. `bpf_lsm_has_d_inode_locked()` consults a BTF id set of hooks that already hold inode locks.

## Control Flow
The executable-file kfunc directly calls `get_task_exe_file()` and requires BPF verifier-enforced release through `bpf_put_file()`. Path resolution calls `d_path()`, then moves the returned pathname down to the beginning of the supplied BPF buffer. Xattr reads validate a dynptr buffer, require `user.` or `security.bpf.` prefixes, check read permission with `inode_permission()`, and call `__vfs_getxattr()`.

Xattr writes/removals are stricter: only `security.bpf.` names are allowed and write permission is checked. Unlocked variants lock `d_inode`, call the locked helper, and unlock. Locked helpers call `__vfs_setxattr()` or `__vfs_removexattr()`, then notify with `fsnotify_xattr()` on success. They intentionally avoid calling LSM post-setxattr/post-removexattr hooks because these changes are initiated from BPF LSM and recursive callbacks could deadlock. Cgroup xattr reads only allow `user.` names and call `kernfs_xattr_get()` on the cgroup kernfs node.

## State And Persistence
`bpf_get_task_exe_file()` acquires a live `struct file` reference that must be released. Xattr set/remove kfuncs persist metadata changes to the target filesystem object and emit fsnotify notifications. Reads and path resolution do not persist data. Registration creates a kernel-global BTF kfunc id set available after late init.

## Dependencies And Integration Points
The file integrates BPF verifier kfunc metadata, BPF LSM program type filtering, VFS path and xattr APIs, dynptr internals, inode permission checks, fsnotify, cgroup kernfs xattrs, and BTF IDs for LSM hook names. It depends on BPF verifier enforcement for reference lifetime and sleepable-kfunc placement.

## Risks
The security boundary is intentionally narrow. Prefix checks must remain correct because broader xattr access would let BPF LSM programs read or mutate unrelated metadata. Lock selection is subtle: calling an unlocked helper from an already-locked hook can deadlock, while calling a locked helper without the lock can race. Avoiding post-xattr LSM callbacks prevents recursion but also means observers relying only on those hooks will not see these BPF-originated changes. Dynptr size/data validation is required to avoid invalid kernel memory access.

## Test Signals
Verifier tests should confirm acquire/release pairing, LSM-only access, sleepable restrictions, and locked-vs-unlocked helper availability by hook. Runtime tests should cover reading `user.` and `security.bpf.` xattrs, rejecting other prefixes, setting/removing `security.bpf.` xattrs with fsnotify visibility, permission failures, zero-size path buffers, path resolution truncation behavior, cgroup `user.` xattr reads, and recursion/deadlock resistance in LSM hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/bpf_fs_kfuncs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/btrfs/Kconfig

## Purpose
Defines Kconfig options controlling Btrfs filesystem availability and feature gates. It exposes the main `BTRFS_FS` tristate, optional POSIX ACLs, module-load sanity tests, debug instrumentation, runtime assertions, and experimental features.

## Important APIs, Types, And Functions
This is declarative Kconfig rather than C code. The main symbols are `BTRFS_FS`, `BTRFS_FS_POSIX_ACL`, `BTRFS_FS_RUN_SANITY_TESTS`, `BTRFS_DEBUG`, `BTRFS_ASSERT`, and `BTRFS_EXPERIMENTAL`. `BTRFS_FS` selects required libraries and subsystems including cgroup bio punt support, CRC32, BLAKE2b, SHA256, zlib, LZO, Zstd, iomap, RAID6 parity, XOR blocks, and xxhash. It depends on `PAGE_SIZE_LESS_THAN_256KB`.

## Control Flow
The kernel configuration system evaluates dependencies and selects. Enabling `BTRFS_FS` allows building the filesystem built-in or as module. Enabling ACL support selects `FS_POSIX_ACL`; enabling sanity tests compiles test objects that run on module load; enabling debug or assert symbols compiles additional checking paths in other Btrfs files. `BTRFS_EXPERIMENTAL` gates unstable features listed in the help text rather than implementing them locally.

## State And Persistence
The file produces build-time configuration state. It does not run at runtime, but selected symbols determine which object files are built and which runtime features or checks are available. User-visible persistence is indirect through the generated kernel `.config` and built module/kernel image.

## Dependencies And Integration Points
The options feed `fs/btrfs/Makefile` object selection and many `#ifdef CONFIG_BTRFS_*` blocks across Btrfs. The selected compression, checksum, RAID, and iomap dependencies correspond to core filesystem capabilities. `BTRFS_FS_POSIX_ACL` directly controls whether `acl.o` is compiled and whether `acl.h` exports real ACL methods or stubs.

## Risks
Incorrect dependencies can allow invalid builds or silently omit required libraries. Debug, assertion, sanity-test, and experimental options trade coverage for runtime cost and stability. The page-size dependency is critical for supported metadata block constraints; relaxing it without matching code changes could mount unsupported configurations.

## Test Signals
Build tests should cover built-in, module, and disabled Btrfs; ACL enabled/disabled; debug/assert builds; sanity-test module-load execution; and experimental-feature build combinations. Kconfig dependency checks should verify that all selected libraries and page-size constraints appear in generated configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/btrfs/Makefile

## Purpose
Defines how the monolithic `btrfs.o` object is built, including warning policy, core source membership, and conditional feature/test objects. It is the build-system map from Kconfig symbols to Btrfs compilation units.

## Important APIs, Types, And Functions
The file uses kbuild variables. `subdir-ccflags-y` enables a subset of `W=1` warnings and disables several noisy `-Wextra` diagnostics. `obj-$(CONFIG_BTRFS_FS) := btrfs.o` makes Btrfs conditional on the main Kconfig symbol. `btrfs-y` lists core objects such as `super.o`, `ctree.o`, `accessors.o`, `xattr.o`, `async-thread.o`, `inode.o`, `volumes.o`, `send.o`, `qgroup.o`, and many more. Conditional additions include `acl.o`, `ref-verify.o`, `zoned.o`, `verity.o`, and multiple `tests/*.o` objects.

## Control Flow
During kbuild, enabled Kconfig symbols expand the object lists. Core `btrfs-y` objects are linked into `btrfs.o` whenever `CONFIG_BTRFS_FS` is enabled. Feature symbols append their specific objects. If both `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` and `CONFIG_BLK_DEV_ZONED=y` are set, `tests/zoned-tests.o` is added as well.

## State And Persistence
This file has no runtime state, but it persists build policy through compiler flags and link membership. The produced state is a kernel built-in or module containing exactly the selected objects.

## Dependencies And Integration Points
It integrates Kconfig with Btrfs source files. It directly ties `CONFIG_BTRFS_FS_POSIX_ACL` to `acl.o`, `CONFIG_BTRFS_DEBUG` to `ref-verify.o`, `CONFIG_BLK_DEV_ZONED` to zoned support, `CONFIG_FS_VERITY` to verity support, and `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` to developer regression test objects.

## Risks
Missing an object from `btrfs-y` can create link errors or, worse, omit runtime functionality. Overly aggressive warnings can break builds on some compilers, while disabled warnings may hide real issues. Conditional test objects must match the feature symbols they exercise or module-load sanity tests can become incomplete.

## Test Signals
Useful signals are allmodconfig/allyesconfig builds, minimal Btrfs module builds, ACL/debug/zoned/verity combinations, and sanity-test builds. Compiler-warning CI should confirm the selected warning subset remains supported across GCC and Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/accessors.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/accessors.c

## Purpose
Provides out-of-line Btrfs extent-buffer set/get primitives for 8-, 16-, 32-, and 64-bit little-endian fields, plus a node-key reader. These functions are the low-level implementation behind many typed metadata accessors declared in `accessors.h`.

## Important APIs, Types, And Functions
The macro `DEFINE_BTRFS_SETGET_BITS(bits)` generates `btrfs_get_8/16/32/64()` and `btrfs_set_8/16/32/64()`. `report_setget_bounds()` emits a Btrfs warning when a requested metadata member exceeds the extent-buffer length. `memcpy_split_src()` copies a value that spans two folios. `btrfs_node_key()` reads a `struct btrfs_disk_key` from a node pointer slot.

## Control Flow
Each generated getter computes `member_offset = (unsigned long)ptr + off`, maps that logical extent-buffer offset to a folio index and offset-in-folio, checks bounds against `eb->len`, then either reads the value directly with `get_unaligned_le*()` or assembles bytes from the current and next folio when the field crosses a folio boundary. Setters perform the same offset and bounds logic, then write directly with `put_unaligned_le*()` or split bytes across adjacent folios.

`btrfs_node_key()` uses `btrfs_node_key_ptr_offset()` from the header to find the node pointer slot and `read_eb_member()` to copy the embedded disk key out of the extent buffer.

## State And Persistence
Getters are read-only. Setters mutate in-memory extent-buffer folios; those changes become persistent only when higher-level Btrfs writeback commits the metadata block. Bounds failures are reported through kernel warnings and return zero/no-op rather than crashing directly.

## Dependencies And Integration Points
This file depends on `extent_io.h` for `struct extent_buffer`, folio layout helpers, and read/write semantics; `fs.h` for filesystem information such as `fs_info`; `messages.h` for `btrfs_warn()`; and `accessors.h` for declarations and higher-level offset macros. It is compiled into Btrfs through the Makefile core object list.

## Risks
These helpers sit on a critical metadata boundary. Bad offset arithmetic, incorrect folio-boundary handling, or missing bounds checks could corrupt on-disk metadata or read stale memory. Returning zero on out-of-bounds reads can mask an upstream corruption path, so warning visibility matters. The split-field path is especially important for metadata block sizes larger than page/folio size.

## Test Signals
Tests should exercise 1-, 2-, 4-, and 8-byte fields at normal offsets, exactly at folio boundaries, and spanning folio boundaries; out-of-bounds reads/writes; little-endian conversion; and node-key extraction. Btrfs extent-buffer KUnit/sanity tests and tree-checker failures are strong signals for regressions here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/accessors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/accessors.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/accessors.h

## Purpose
Defines the typed accessor API for Btrfs on-disk metadata structures. It centralizes little-endian conversion, unaligned access, extent-buffer member reads/writes, stack-structure reads/writes, header access, key conversion, item pointer arithmetic, and field-specific helpers for a broad set of Btrfs tree items.

## Important APIs, Types, And Functions
The foundational macros are `read_eb_member()`, `write_eb_member()`, `DECLARE_BTRFS_SETGET_BITS()`, `BTRFS_SETGET_FUNCS()`, `BTRFS_SETGET_HEADER_FUNCS()`, and `BTRFS_SETGET_STACK_FUNCS()`. They generate type-checked helpers using `static_assert()` and `sizeof_field()`.

Generated or hand-written accessor families cover device items, chunks and stripes, block group items including v2/remap fields, free-space records, inode refs and inode items, timespecs, RAID stride records, device extents, extent refs and inline-ref sizing, node pointers, leaf items, directory/root refs, free-space headers, disk-key conversions, tree headers, root items/backups, balance items, superblock fields, file extents, qgroup status/info/limits, device replace state, fs-verity descriptor items, and remap items. `btrfs_item_ptr()` and `btrfs_item_ptr_offset()` convert leaf slots to item data offsets.

## Control Flow
Most helpers are inline field translations. Extent-buffer helpers pass an offset-like cast pointer plus a field offset into the out-of-line `btrfs_get_*()`/`btrfs_set_*()` functions implemented in `accessors.c`. Stack helpers operate on in-memory structs with unaligned little-endian loads/stores. Header helpers assume the tree header is in the first folio at `offset_in_page(eb->start)`. Key conversion helpers are optimized to `memcpy()` on little-endian builds and perform explicit `le64_to_cpu()`/`cpu_to_le64()` conversions on big-endian builds.

Special helpers add semantics beyond raw field access. `btrfs_set_device_total_bytes()` warns if the value is not sector-size aligned. `btrfs_extent_inline_ref_size()` maps inline-ref key types to their record sizes. Header flag helpers set, clear, and decode backref revision bits. Item helpers compute slot offsets and item data extents.

## State And Persistence
Header and extent-buffer setters mutate Btrfs metadata buffers; stack setters mutate temporary in-memory copies. Persistence is controlled by the surrounding transaction and extent-buffer writeback code, not by this header. The header also encodes invariants: field sizes must match expected integer widths at compile time, and all on-disk multi-byte fields are treated as little-endian.

## Dependencies And Integration Points
The header depends on UAPI Btrfs tree structure definitions, `struct extent_buffer` and folio layout from `extent_io.h`, filesystem state from `fs.h`, Linux unaligned access helpers, and endian macros. It is widely included across Btrfs tree manipulation, mount, transaction, scrub, qgroup, send, balance, device replace, and tree-checker code.

## Risks
This is a high-blast-radius header. A wrong field width, offset, endian conversion, or pointer calculation can corrupt filesystem metadata across many call sites. Header helpers assuming the first folio must remain consistent with extent-buffer allocation. The little-endian fast path relies on `struct btrfs_key` and `struct btrfs_disk_key` layout compatibility. Adding on-disk fields without accessor updates can lead to ad hoc access and missed validation.

## Test Signals
Signals include compiler `static_assert()` failures, sparse/endian warnings, Btrfs KUnit or module-load sanity tests over extent buffers and tree items, cross-endian build coverage, filesystem mount and scrub of metadata-heavy images, tree-checker validation, and tests that exercise leaf item pointer arithmetic, inline refs, qgroups, device replace, and superblock parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/accessors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/acl.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/acl.c

## Purpose
Implements Btrfs POSIX ACL get/set operations on top of Btrfs xattrs. It translates VFS ACL requests into `system.posix_acl_access` and `system.posix_acl_default` xattr reads/writes and keeps the inode ACL cache consistent.

## Important APIs, Types, And Functions
`btrfs_get_acl(struct inode *inode, int type, bool rcu)` implements ACL retrieval. `__btrfs_set_acl(struct btrfs_trans_handle *trans, struct inode *inode, struct posix_acl *acl, int type)` writes or removes an ACL xattr, optionally within an existing transaction. `btrfs_set_acl(struct mnt_idmap *idmap, struct dentry *dentry, struct posix_acl *acl, int type)` is the VFS-facing setter that also updates inode mode for access ACLs.

## Control Flow
`btrfs_get_acl()` rejects RCU mode with `-ECHILD`, maps ACL type to the correct xattr name, queries xattr size, allocates a buffer when data exists, fetches the xattr value, and converts it through `posix_acl_from_xattr()`. Missing or zero-length ACLs return `NULL`; other negative xattr errors are propagated.

`__btrfs_set_acl()` validates type, rejects default ACLs on non-directories unless clearing, converts a non-null ACL to xattr bytes using `posix_acl_to_xattr()` under a NOFS allocation context when a transaction handle is held, and writes through `btrfs_setxattr()` or `btrfs_setxattr_trans()`. On success it calls `set_cached_acl()`.

`btrfs_set_acl()` updates `inode->i_mode` for access ACLs via `posix_acl_update_mode()`, calls the internal setter without an existing transaction, and restores the old mode if xattr writing fails.

## State And Persistence
ACLs are persisted as Btrfs xattrs. Successful writes update the in-memory ACL cache. Access ACL updates may change `inode->i_mode`; failures restore it. The NOFS allocation scope prevents transaction-held memory reclaim from re-entering filesystem paths.

## Dependencies And Integration Points
The file depends on POSIX ACL core helpers, xattr conversion helpers, Btrfs xattr APIs, Btrfs transactions, inode/dentry VFS structures, and `init_user_ns` for ACL xattr serialization. It is compiled only when `CONFIG_BTRFS_FS_POSIX_ACL` adds `acl.o`.

## Risks
ACL serialization occurs while transactions may be active, so allocation context matters. Mode update and xattr persistence must stay atomic from the VFS caller's perspective; otherwise inode permissions can diverge from stored ACLs. Default ACL handling must reject non-directories to avoid invalid metadata. RCU get support is intentionally absent and must return `-ECHILD` so VFS retries in sleepable context.

## Test Signals
Tests should create, read, replace, and remove access and default ACLs; verify mode changes from `posix_acl_update_mode()`; reject default ACLs on regular files; exercise missing ACL xattrs; inject xattr write failures to confirm mode rollback; and run ACL operations during transaction-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/acl.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/acl.h

## Purpose
Declares the Btrfs ACL API and provides compile-time stubs when POSIX ACL support is disabled. It lets the rest of Btrfs reference ACL hooks without scattering feature-conditionals through call sites.

## Important APIs, Types, And Functions
When `CONFIG_BTRFS_FS_POSIX_ACL` is enabled, it declares `btrfs_get_acl()`, `btrfs_set_acl()`, and `__btrfs_set_acl()`, with forward declarations for `struct posix_acl`, `struct inode`, `struct btrfs_trans_handle`, `struct mnt_idmap`, and `struct dentry`. When disabled, `btrfs_get_acl` and `btrfs_set_acl` are defined as `NULL`, and `__btrfs_set_acl()` is an inline stub returning `-EOPNOTSUPP`.

## Control Flow
This header has no runtime control flow beyond the disabled inline stub. Compile-time configuration decides whether inode operation tables receive real ACL functions or NULL hooks.

## State And Persistence
The header itself has no state. With ACL support disabled, attempts to set ACLs through internal paths fail without persisting xattrs. With support enabled, state behavior is defined by `acl.c`.

## Dependencies And Integration Points
It connects Kconfig, the Makefile's conditional `acl.o`, Btrfs inode operations, and internal transaction code that may need `__btrfs_set_acl()`. The disabled stubs keep builds valid when `CONFIG_BTRFS_FS_POSIX_ACL=n`.

## Risks
The main risk is mismatched expectations between call sites and configuration. Callers that require ACL persistence must handle `-EOPNOTSUPP` when disabled. Defining VFS hooks as NULL must remain acceptable to the inode operation setup code.

## Test Signals
Build coverage should include ACL enabled and disabled configurations. Runtime tests in disabled builds should confirm ACL syscalls fail with unsupported-operation behavior and do not create ACL xattrs, while enabled builds should use the real implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/async-thread.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/async-thread.c

## Purpose
Implements Btrfs-specific workqueue wrappers for asynchronous work, ordered completion callbacks, per-filesystem ownership tracing, congestion checks, and adaptive concurrency thresholding.

## Important APIs, Types, And Functions
`struct btrfs_workqueue` wraps a kernel `workqueue_struct`, the owning `btrfs_fs_info`, an ordered-work list and lock, pending count, active worker limits, threshold state, and threshold lock. Exported functions include `btrfs_alloc_workqueue()`, `btrfs_alloc_ordered_workqueue()`, `btrfs_init_work()`, `btrfs_queue_work()`, `btrfs_destroy_workqueue()`, `btrfs_workqueue_set_max()`, `btrfs_flush_workqueue()`, `btrfs_workqueue_owner()`, `btrfs_work_owner()`, and `btrfs_workqueue_normal_congested()`.

Internal helpers include `thresh_queue_hook()`, `thresh_exec_hook()`, `run_ordered_work()`, and `btrfs_work_helper()`. Work flags `WORK_DONE_BIT` and `WORK_ORDER_DONE_BIT` coordinate ordinary and ordered phases.

## Control Flow
Allocation initializes ownership, pending state, ordered list, and locks. Regular workqueues may start with `current_active = 1` and grow toward `limit_active` when a threshold is configured; low or disabled thresholds use `NO_THRESHOLD`. Ordered workqueues are allocated through `alloc_ordered_workqueue()` and fixed at one active worker.

`btrfs_queue_work()` assigns the workqueue pointer, increments pending threshold state, appends ordered work to `ordered_list` under `list_lock` when needed, traces the queue event, and queues the kernel work item. `btrfs_work_helper()` runs in worker context, applies threshold execution adjustment, calls the work function, and either traces completion directly or marks `WORK_DONE_BIT` with a memory barrier and calls `run_ordered_work()`.

`run_ordered_work()` walks the ordered list from the head and only runs ordered callbacks for work items whose normal work has completed. It leaves the current item on the list as a barrier while its ordered function runs, then removes it and calls the ordered free callback outside the lock. If the completed item is the currently executing work, freeing is deferred until after traversal to avoid recycling the work item while kernel workqueue non-reentrancy assumptions still depend on its address.

Thresholding increments pending in queue context, decrements in worker context, and periodically adjusts `workqueue_set_max_active()` based on pending load under `thres_lock`. Congestion reports true when pending is more than twice the threshold.

## State And Persistence
All state is in memory. Workqueue state includes pending count, current/limit active counts, ordered list membership, per-work flags, and ownership pointers. Work callbacks can mutate filesystem state, but this wrapper only coordinates execution and completion ordering. Destroying the workqueue drains kernel workqueue resources and frees the wrapper.

## Dependencies And Integration Points
It depends on Linux workqueues, spinlocks, atomics, memory barriers, tracepoints from `trace/events/btrfs.h`, and the Btrfs `struct btrfs_work` declared in `async-thread.h`. It is used by Btrfs subsystems needing asynchronous execution with optional ordered completion, such as delayed work, compression, endio, or transaction-adjacent tasks.

## Risks
The ordered-work logic is concurrency-sensitive. Missing barriers could allow ordered callbacks to see stale writes from normal work. Freeing or reusing work items too early can deadlock with kernel workqueue non-reentrancy behavior, especially across filesystems or loop-device dependencies. Threshold adjustment has a likely bug-prone condition around `wq->count %= (wq->thresh / 4)` and when adjustment is skipped, so changes need careful load testing. Updating `limit_active` does not immediately call `workqueue_set_max_active()`; it only constrains future threshold changes.

## Test Signals
Tests should queue ordered and unordered work, verify ordered callbacks run in submission order even when normal work finishes out of order, confirm free callbacks are not called under list lock, stress queue/destroy/flush races, exercise threshold growth/shrink under pending load, and check tracepoints/congestion reporting. Memory-ordering bugs are best exposed with stress tests on weakly ordered architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/async-thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/async-thread.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/async-thread.h

## Purpose
Declares the Btrfs asynchronous workqueue interface and the per-work item structure used by `async-thread.c`. It gives Btrfs subsystems a common way to queue normal work with an optional ordered completion/free phase.

## Important APIs, Types, And Functions
The header forward-declares `struct btrfs_fs_info`, `struct btrfs_workqueue`, and `struct btrfs_work`. It defines callback types `btrfs_func_t(struct btrfs_work *)` and `btrfs_ordered_func_t(struct btrfs_work *, bool)`. `struct btrfs_work` contains the normal callback, optional ordered callback, embedded `work_struct`, ordered-list node, owning workqueue pointer, and private flags.

Declared functions cover allocation of regular and ordered workqueues, work initialization and queueing, destruction, max-active adjustment, owner lookup, congestion query, and flushing.

## Control Flow
Callers embed or allocate a `struct btrfs_work`, initialize it with `btrfs_init_work()`, and enqueue it through `btrfs_queue_work()`. The normal callback runs first. If an ordered callback was supplied, the implementation later calls it with `false` for ordered completion and `true` for final/free handling.

## State And Persistence
The header defines in-memory state only. The comment "Don't touch things below" marks fields owned by the async framework after initialization. Persistence of filesystem changes is the responsibility of caller callbacks and surrounding Btrfs transaction code.

## Dependencies And Integration Points
It depends on Linux `workqueue.h`, `list.h`, compiler annotations, and the implementation in `async-thread.c`. Many Btrfs modules can include it without depending on the private layout of `struct btrfs_workqueue`.

## Risks
Callers must respect object lifetime: work items must remain alive until the async framework invokes the appropriate final callback or completion path. Ordered callbacks must interpret the boolean phase consistently. Direct mutation of internal fields after queueing can break list ordering, workqueue ownership, and flag synchronization.

## Test Signals
Build coverage checks API consistency. Runtime signals come from async-thread tests or Btrfs stress workloads that initialize, queue, flush, and destroy workqueues while validating callback ordering and object lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/async-thread.h -->
