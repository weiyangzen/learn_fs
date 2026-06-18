# subset-b-009344 research

Grouped research report for strace decoder and xlat sources. Each section preserves the exact source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/udmabuf.c -->
# sources/test-tools/strace/src/udmabuf.c

Purpose: udmabuf ioctl decoder for `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST`; it prints memfd-backed buffer creation structures, flags, offsets, sizes, and list entries.

Important APIs/types/functions:
- Helper functions include `print_udmabuf_create`, `print_udmabuf_create_item`, `print_udmabuf_create_list`, `udmabuf_ioctl`
- Direct includes: `"defs.h"`, `<linux/udmabuf.h>`, `"xlat/udmabuf_flags.h"`
- Xlat tables consumed: `udmabuf_flags`

Control flow:
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `UDMABUF_CREATE`, `UDMABUF_CREATE_LIST`
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/udmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/uid.c -->
# sources/test-tools/strace/src/uid.c

Purpose: strace syscall decoder implementation for `getuid`, `setfsuid`, `setuid`, `getresuid`, `setreuid`, `setresuid`, `chown`, `fchown`...; it prints syscall arguments/results using strace formatting helpers.

Important APIs/types/functions:
- SYS_FUNC handlers: `getuid`, `setfsuid`, `setuid`, `getresuid`, `setreuid`, `setresuid`, `chown`, `fchown`, `setgroups`, `getgroups`
- Helper functions include `get_print_uid`, `printuid`, `print_gid`, `print_groups`
- Direct includes: `"defs.h"`
- Local/exported macros: `SIZEIFY`, `SIZEIFY_`, `SIZEIFY__`, `printuid`, `sys_chown`, `sys_fchown`, `sys_getgroups`, `sys_getresuid`, `sys_getuid`, `sys_setfsuid`, `sys_setgroups`, `sys_setresuid`...

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/uid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/uid16.c -->
# sources/test-tools/strace/src/uid16.c

Purpose: 16-bit UID/GID compatibility decoder wrapper; it defines `STRACE_UID_SIZE 16` and includes `uid.c` so legacy uid16 syscall variants reuse the generic UID decoder with 16-bit element widths.

Important APIs/types/functions:
- Direct includes: `"uid.c"`
- Local/exported macros: `STRACE_UID_SIZE`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/uid16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/umask.c -->
# sources/test-tools/strace/src/umask.c

Purpose: Decoder for `umask`, printing the new file-mode creation mask in numeric/octal mode and tagging the syscall return as octal.

Important APIs/types/functions:
- SYS_FUNC handlers: `umask`
- Direct includes: `"defs.h"`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/umask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/umount.c -->
# sources/test-tools/strace/src/umount.c

Purpose: Decoder for `umount2`, printing the target path and symbolic mount-detach/force/expire/no-follow flags.

Important APIs/types/functions:
- SYS_FUNC handlers: `umount2`
- Direct includes: `"defs.h"`, `"xlat/umount_flags.h"`
- Xlat tables consumed: `umount_flags`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/umount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/uname.c -->
# sources/test-tools/strace/src/uname.c

Purpose: Exit-side decoder for `uname`, fetching `struct utsname` and printing system, node, release, version, machine, and optional domain fields with abbreviated-mode support.

Important APIs/types/functions:
- SYS_FUNC handlers: `uname`
- Direct includes: `"defs.h"`, `<sys/utsname.h>`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover verbose versus abbreviated output modes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/uname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libdw.c -->
# sources/test-tools/strace/src/unwind-libdw.c

Purpose: elfutils libdwfl unwinder backend that attaches DWARF state to tracees, refreshes mapping reports on mmap generation changes, caches frame metadata, and emits symbol/source frames.

Important APIs/types/functions:
- Helper functions include `update_mapping_generation`, `init`, `tcb_init`, `tcb_fin`, `flush_cache_maybe`, `frame_callback`, `tcb_walk`
- Direct includes: `"defs.h"`, `"unwind.h"`, `"mmap_notify.h"`, `"static_assert.h"`, `<elfutils/libdwfl.h>`
- Local/exported macros: `STRACE_UW_CACHE_SIZE`, `STRACE_UW_CACHE_ASSOC`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written
- tracks mmap generation changes to invalidate stale unwind symbol mappings

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- requires elfutils libdwfl support at build/run time

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- kernel/userspace structure layout drift is guarded by build-time assertions but still needs architecture coverage

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libunwind.c -->
# sources/test-tools/strace/src/unwind-libunwind.c

Purpose: libunwind-ptrace backend that creates a remote address space, consults the mmap cache for executable mappings, resolves symbols, and walks tracee frames.

Important APIs/types/functions:
- Helper functions include `init`, `tcb_init`, `tcb_fin`, `get_symbol_name`, `print_stack_frame`, `walk`, `tcb_walk`
- Direct includes: `"defs.h"`, `"unwind.h"`, `"mmap_cache.h"`, `<libunwind-ptrace.h>`

Control flow:
- dispatches switch cases such as `MMAP_CACHE_REBUILD_RENEWED`, `MMAP_CACHE_REBUILD_READY`

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates with ptrace tracee access
- requires libunwind-ptrace support and mmap cache integration

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind.c -->
# sources/test-tools/strace/src/unwind.c

Purpose: Common stack-unwind orchestration layer: initializes backend hooks, manages per-tcb queued stack frames, formats/demangles entries, and captures/prints/discards call stacks.

Important APIs/types/functions:
- Helper functions include `unwind_init`, `unwind_tcb_init`, `unwind_tcb_fin`, `print_call_cb`, `print_error_cb`, `sprint_call_or_error`, `queue_put`, `queue_put_call`, `queue_put_error`, `queue_drain`, `unwind_tcb_print`, `unwind_tcb_discard`, `unwind_tcb_capture`
- Direct includes: `"defs.h"`, `"unwind.h"`, `<demangle.h>`, `<libiberty/demangle.h>`
- Local/exported macros: `LIBIBERTY_H`, `STACK_ENTRY_SYMBOL_WITH_SRCINFO_FMT`, `STACK_ENTRY_SYMBOL_FMT`, `STACK_ENTRY_NOSYMBOL_FMT`, `STACK_ENTRY_BUG_FMT`, `STACK_ENTRY_ERROR_WITH_OFFSET_FMT`, `STACK_ENTRY_ERROR_FMT`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- cover native and compat personality builds where available
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/unwind.h -->
# sources/test-tools/strace/src/unwind.h

Purpose: Backend interface contract for stack unwinding, defining callback signatures and the `struct unwind_unwinder_t` vtable implemented by libdwfl/libunwind backends.

Important APIs/types/functions:
- Direct includes: `"defs.h"`
- Local/exported macros: `STRACE_UNWIND_H`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- requires libunwind-ptrace support and mmap cache integration

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/upeek.c -->
# sources/test-tools/strace/src/upeek.c

Purpose: Low-level ptrace helper that reads a word from the tracee user area with `PTRACE_PEEKUSER` and reports non-ESRCH failures.

Important APIs/types/functions:
- Helper functions include `upeek`
- Direct includes: `"defs.h"`, `"ptrace.h"`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates with ptrace tracee access

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/upeek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/upoke.c -->
# sources/test-tools/strace/src/upoke.c

Purpose: Low-level ptrace helper that writes a word to the tracee user area through `ptrace_pokeuser` and reports non-ESRCH failures.

Important APIs/types/functions:
- Helper functions include `upoke`
- Direct includes: `"defs.h"`, `"ptrace.h"`, `"ptrace_pokeuser.c"`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates with ptrace tracee access

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/upoke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/userfaultfd.c -->
# sources/test-tools/strace/src/userfaultfd.c

Purpose: Decoder for the `userfaultfd` syscall and its ioctl protocol, including API negotiation, range operations, copy/zeropage/continue/poison results, and write-protect/register flags.

Important APIs/types/functions:
- SYS_FUNC handlers: `userfaultfd`
- Helper functions include `tprintf_uffdio_range`, `uffdio_ioctl`
- Direct includes: `"defs.h"`, `"kernel_fcntl.h"`, `<linux/ioctl.h>`, `<linux/userfaultfd.h>`, `"xlat/uffd_flags.h"`, `"xlat/uffd_api_features.h"`, `"xlat/uffd_api_flags.h"`, `"xlat/uffd_continue_mode_flags.h"`, `"xlat/uffd_copy_flags.h"`, `"xlat/uffd_poison_mode_flags.h"`, `"xlat/uffd_register_ioctl_flags.h"`, `"xlat/uffd_register_mode_flags.h"`, `"xlat/uffd_writeprotect_mode_flags.h"`, `"xlat/uffd_zeropage_flags.h"`
- Xlat tables consumed: `uffd_flags`, `uffd_api_features`, `uffd_api_flags`, `uffd_continue_mode_flags`, `uffd_copy_flags`, `uffd_poison_mode_flags`, `uffd_register_ioctl_flags`, `uffd_register_mode_flags`, `uffd_writeprotect_mode_flags`, `uffd_zeropage_flags`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `UFFDIO_API`, `UFFDIO_COPY`, `UFFDIO_REGISTER`, `UFFDIO_UNREGISTER`, `UFFDIO_WAKE`, `UFFDIO_ZEROPAGE`, `UFFDIO_WRITEPROTECT`, `UFFDIO_CONTINUE`, `UFFDIO_POISON`
- stores entry-side values in per-tcb private data so exit-side decoding can show kernel-mutated fields

State and persistence behavior:
- per-syscall transient state is held on `struct tcb` private data between entry and exit
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/userfaultfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/ustat.c -->
# sources/test-tools/strace/src/ustat.c

Purpose: Decoder for legacy `ustat`, printing the device argument and, when headers are available, exit-side free block/inode counts from `struct ustat`.

Important APIs/types/functions:
- SYS_FUNC handlers: `ustat`
- Direct includes: `"defs.h"`, `DEF_MPERS_TYPE(struct_ustat)`, `<ustat.h>`, `MPERS_DEFS`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- participates in strace multi-personality builds for ABI-specific structures

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover native and compat personality builds where available
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/ustat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/util.c -->
# sources/test-tools/strace/src/util.c

Purpose: Core utility layer for strace formatting, tracee-memory fetching, path/string/number printing, SELinux context helpers, timestamp math, iovec decoding, and process-control support used by many syscall decoders.

Important APIs/types/functions:
- Helper functions include `find_xlat_val_ex`, `find_arg_val_`, `str2timescale_ex`, `ts_nz`, `ts_cmp`, `ts_float`, `ts_add`, `ts_sub`, `ts_div`, `ts_min`, `ts_max`, `parse_ts`, `ilog10`, `print_ticks`, `print_ticks_d`, `print_clock_t`, `stpcpy`, `next_set_bit`...
- Direct includes: `"defs.h"`, `<limits.h>`, `<fcntl.h>`, `<stdarg.h>`, `<sys/stat.h>`, `<sys/sysmacros.h>`, `<sys/xattr.h>`, `<sys/uio.h>`, `"largefile_wrappers.h"`, `"number_set.h"`, `"print_fields.h"`, `"print_utils.h"`, `"secontext.h"`, `"static_assert.h"`, `"string_to_uint.h"`, `"xlat.h"`...
- Local/exported macros: `ILOG10_ITER_`, `DEF_PRINTNUM`, `DEF_PRINTNUM_ADDR`, `DEF_PRINTPAIR`, `ALLOCA_CUTOFF`, `use_alloca`, `iov`, `sizeof_iov`, `iov_iov_base`, `iov_iov_len`, `sizeof_iov`, `iov_iov_base`...

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `S_IFBLK`, `S_IFCHR`, `FINFO_DEV_BLK`, `FINFO_DEV_CHR`
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- kernel/userspace structure layout drift is guarded by build-time assertions but still needs architecture coverage
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover verbose versus abbreviated output modes
- cover raw, abbrev, and verbose xlat styles
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/utime.c -->
# sources/test-tools/strace/src/utime.c

Purpose: Decoder for `utime`, printing pathname and `struct utimbuf` access/modification times with human-readable comments.

Important APIs/types/functions:
- SYS_FUNC handlers: `utime`
- Direct includes: `"defs.h"`, `DEF_MPERS_TYPE(utimbuf_t)`, `<utime.h>`, `MPERS_DEFS`

Control flow:
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- participates in strace multi-personality builds for ABI-specific structures

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover native and compat personality builds where available
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/utime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/utimes.c -->
# sources/test-tools/strace/src/utimes.c

Purpose: Decoder family for `utimes`, `futimesat`, and `utimensat` time32/time64 variants, including dirfd/path/timestamp pairs and `AT_*` flags.

Important APIs/types/functions:
- SYS_FUNC handlers: `utimes`, `futimesat`, `utimensat_time32`, `utimensat_time64`, `osf_utimes`
- Helper functions include `do_utimensat`
- Direct includes: `"defs.h"`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/utimes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/v4l2.c -->
# sources/test-tools/strace/src/v4l2.c

Purpose: Video4Linux2 ioctl decoder covering capability, format, buffer, stream parameters, standards, inputs, controls, tuners, crop, frame-size/interval, and buffer-creation structures.

Important APIs/types/functions:
- MPERS printer entry points: `v4l2_ioctl`
- Helper functions include `print_v4l2_rect`, `print_pixelformat`, `print_v4l2_capability`, `print_v4l2_fmtdesc`, `print_v4l2_clip`, `DECL_print_v4l2_format_fmt`, `print_v4l2_plane_pix_format_array_member`, `print_v4l2_format_fmt`, `tprint_struct_end_value_changed_struct_begin`, `print_v4l2_format`, `print_v4l2_requestbuffers`, `print_v4l2_exportbuffer`, `print_v4l2_buffer_flags`, `print_v4l2_timeval`, `print_v4l2_buffer_contents`, `print_v4l2_buffer`, `print_v4l2_buffer_time32_contents`, `print_v4l2_buffer_time32`...
- Direct includes: `"defs.h"`, `DEF_MPERS_TYPE(kernel_v4l2_buffer_t)`, `DEF_MPERS_TYPE(kernel_v4l2_buffer_time32_t)`, `DEF_MPERS_TYPE(kernel_v4l2_event_t)`, `DEF_MPERS_TYPE(kernel_v4l2_timeval_t)`, `DEF_MPERS_TYPE(struct_v4l2_clip)`, `DEF_MPERS_TYPE(struct_v4l2_create_buffers)`, `DEF_MPERS_TYPE(struct_v4l2_ext_control)`, `DEF_MPERS_TYPE(struct_v4l2_ext_controls)`, `DEF_MPERS_TYPE(struct_v4l2_format)`, `DEF_MPERS_TYPE(struct_v4l2_framebuffer)`, `DEF_MPERS_TYPE(struct_v4l2_input)`, `DEF_MPERS_TYPE(struct_v4l2_standard)`, `DEF_MPERS_TYPE(struct_v4l2_window)`, `"kernel_v4l2_types.h"`, `MPERS_DEFS`...
- Xlat tables consumed: `v4l2_meta_fmts`, `v4l2_pix_fmts`, `v4l2_sdr_fmts`, `v4l2_device_capabilities_flags`, `v4l2_buf_types`, `v4l2_format_description_flags`, `v4l2_fields`, `v4l2_colorspaces`, `v4l2_vbi_flags`, `v4l2_sliced_flags`, `v4l2_memories`, `v4l2_buf_flags`, `v4l2_buf_flags_ts_type`, `v4l2_buf_flags_ts_src`, `v4l2_streaming_capabilities`, `v4l2_capture_modes`, `v4l2_input_capabilities_flags`, `v4l2_input_status_flags`, `v4l2_input_types`, `v4l2_std_ids`...
- Local/exported macros: `PRINT_FIELD_FRACT`, `PRINT_FIELD_PIXFMT`, `DECL_print_v4l2_format_fmt`, `PRINT_FIELD_V4L2_FORMAT_FMT`, `PRINT_FIELD_V4L2_BUFFER_FLAGS`, `PRINT_FIELD_V4L2_TIMEVAL`, `PRINT_FIELD_V4L2_STREAMPARM_PARM`, `PRINT_FIELD_V4L2_CID`, `PRINT_FIELD_V4L2_FRMSIZE_TYPE`, `PRINT_FIELD_V4L2_FRMIVAL_STEPWISE`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `V4L2_BUF_TYPE_VIDEO_CAPTURE`, `V4L2_BUF_TYPE_VIDEO_OUTPUT`, `V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE`, `V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE`, `V4L2_BUF_TYPE_VIDEO_OUTPUT_OVERLAY`, `V4L2_BUF_TYPE_VIDEO_OVERLAY`, `V4L2_BUF_TYPE_VBI_CAPTURE`, `V4L2_BUF_TYPE_VBI_OUTPUT`, `V4L2_BUF_TYPE_SLICED_VBI_CAPTURE`, `V4L2_BUF_TYPE_SLICED_VBI_OUTPUT`, `V4L2_BUF_TYPE_SDR_OUTPUT`, `V4L2_BUF_TYPE_SDR_CAPTURE`, `V4L2_BUF_TYPE_META_OUTPUT`, `V4L2_BUF_TYPE_META_CAPTURE`, `V4L2_BUF_TYPE_VIDEO_CAPTURE`, `V4L2_BUF_TYPE_VIDEO_OUTPUT`, `V4L2_FRMSIZE_TYPE_DISCRETE`, `V4L2_FRMSIZE_TYPE_STEPWISE`...
- iterates user-provided arrays with bounded element fetch callbacks
- stores entry-side values in per-tcb private data so exit-side decoding can show kernel-mutated fields

State and persistence behavior:
- per-syscall transient state is held on `struct tcb` private data between entry and exit
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants
- participates in strace multi-personality builds for ABI-specific structures

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- kernel/userspace structure layout drift is guarded by build-time assertions but still needs architecture coverage
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover verbose versus abbreviated output modes
- cover raw, abbrev, and verbose xlat styles
- cover native and compat personality builds where available
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/wait.c -->
# sources/test-tools/strace/src/wait.c

Purpose: Wait-family decoders for `waitpid`, `wait4`, and `waitid`; formats wait status bitfields, ptrace events, ids, options, siginfo, and rusage.

Important APIs/types/functions:
- SYS_FUNC handlers: `waitpid`, `wait4`, `osf_wait4`, `waitid`
- Helper functions include `print_wait_status`, `printwaitn`
- Direct includes: `"defs.h"`, `"ptrace.h"`, `"wait.h"`, `"xlat/wait4_options.h"`, `"xlat/ptrace_events.h"`, `"xlat/waitid_types.h"`
- Xlat tables consumed: `wait4_options`, `ptrace_events`, `waitid_types`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `P_PID`, `P_PIDFD`, `P_PGID`

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants
- integrates with ptrace tracee access

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/wait.h -->
# sources/test-tools/strace/src/wait.h

Purpose: Wait-status compatibility header defining/fixing `WCOREFLAG`, `WCOREDUMP`, `W_STOPCODE`, `W_EXITCODE`, and `W_CONTINUED` for portable wait status decoding.

Important APIs/types/functions:
- Direct includes: `"defs.h"`, `<sys/wait.h>`, `"static_assert.h"`
- Local/exported macros: `STRACE_WAIT_H`, `WCOREFLAG`, `WCOREDUMP`, `W_STOPCODE`, `W_EXITCODE`, `W_CONTINUED`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- kernel/userspace structure layout drift is guarded by build-time assertions but still needs architecture coverage

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/watchdog_ioctl.c -->
# sources/test-tools/strace/src/watchdog_ioctl.c

Purpose: Watchdog ioctl decoder for support/status/timeout/pretimeout/timeleft/setoptions/keepalive commands, including `watchdog_info` and option flag tables.

Important APIs/types/functions:
- Helper functions include `watchdog_ioctl`
- Direct includes: `"defs.h"`, `<linux/watchdog.h>`, `"xlat/watchdog_ioctl_flags.h"`, `"xlat/watchdog_ioctl_setoptions.h"`, `"xlat/watchdog_ioctl_cmds.h"`
- Xlat tables consumed: `watchdog_ioctl_flags`, `watchdog_ioctl_setoptions`, `watchdog_ioctl_cmds`
- Local/exported macros: `XLAT_MACROS_ONLY`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `WDIOC_GETSUPPORT`, `WDIOC_GETSTATUS`, `WDIOC_GETBOOTSTATUS`, `WDIOC_GETTEMP`, `WDIOC_GETTIMEOUT`, `WDIOC_GETPRETIMEOUT`, `WDIOC_GETTIMELEFT`, `WDIOC_SETTIMEOUT`, `WDIOC_SETPRETIMEOUT`, `WDIOC_SETOPTIONS`, `WDIOC_KEEPALIVE`

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover verbose versus abbreviated output modes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/watchdog_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xattr.c -->
# sources/test-tools/strace/src/xattr.c

Purpose: Extended-attribute syscall decoder for path, fd, and modern `*xattrat` variants; prints names, values, list buffers, flags, and `struct xattr_args` payloads.

Important APIs/types/functions:
- SYS_FUNC handlers: `setxattr`, `fsetxattr`, `getxattr`, `fgetxattr`, `listxattr`, `flistxattr`, `removexattr`, `fremovexattr`, `setxattrat`, `getxattrat`, `listxattrat`, `removexattrat`
- Helper functions include `print_xattr_val`, `decode_setxattr_without_path`, `decode_getxattr_without_path`, `print_xattr_list`, `decode_dirfd_pathname_flags`, `decode_dirfd_pathname_flags_name`, `umove_xattr_args_or_printaddr`, `print_xattr_args`
- Direct includes: `"defs.h"`, `<linux/fcntl.h>`, `<linux/xattr.h>`, `"xlat/xattrflags.h"`, `"xlat/xattrat_flags.h"`
- Xlat tables consumed: `xattrflags`, `xattrat_flags`
- Local/exported macros: `XATTR_SIZE_MAX`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- stores entry-side values in per-tcb private data so exit-side decoding can show kernel-mutated fields

State and persistence behavior:
- per-syscall transient state is held on `struct tcb` private data between entry and exit
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.c -->
# sources/test-tools/strace/src/xgetdents.c

Purpose: Shared decoder for `getdents`-style variable-length directory entry buffers, with callback hooks for entry head and tail layouts.

Important APIs/types/functions:
- Helper functions include `decode_dents`, `xgetdents`
- Direct includes: `"xgetdents.h"`, `"kernel_dirent.h"`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- cover verbose versus abbreviated output modes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.h -->
# sources/test-tools/strace/src/xgetdents.h

Purpose: Header declaring getdents callback types and the shared `xgetdents` decoder entry point.

Important APIs/types/functions:
- Direct includes: `"defs.h"`
- Local/exported macros: `STRACE_XGETDENTS_H`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xgetdents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat.c -->
# sources/test-tools/strace/src/xlat.c

Purpose: Runtime implementation of xlat lookup and printing, including table search, reverse lookup, eq-or-less lookup, raw/abbrev/verbose formatting, and flag decomposition.

Important APIs/types/functions:
- Helper functions include `get_xlat_style`, `sprint_xlat_val`, `print_xlat_val`, `tprints_xlat_const`, `xlat_bsearch_compare`, `xlookup`, `xrlookup`, `xlat_search_eq_or_less`, `xlookup_le`, `printxvals_ex`, `sprintxval_ex`, `sprintflags_ex`, `printflags_ex`, `print_xlat_ex`
- Direct includes: `"defs.h"`, `"color.h"`, `"xstring.h"`, `<stdarg.h>`

Control flow:
- dispatches switch cases such as `XLAT_STYLE_FMT_D`, `XLAT_STYLE_FMT_U`, `XLAT_STYLE_FMT_X`, `XT_NORMAL`, `XT_SORTED`, `XT_INDEXED`, `XT_SORTED`, `XT_NORMAL`, `XT_INDEXED`, `XLAT_STYLE_ABBREV`, `XLAT_STYLE_RAW`, `XLAT_STYLE_VERBOSE`

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover raw, abbrev, and verbose xlat styles
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat.h -->
# sources/test-tools/strace/src/xlat.h

Purpose: Public xlat table ABI: table kinds, style/format flags, `struct xlat_data`, `struct xlat`, and initializer macros for generated tables.

Important APIs/types/functions:
- Direct includes: `<stdint.h>`
- Local/exported macros: `STRACE_XLAT_H`, `XLAT_STYLE_FORMAT_SHIFT`, `XLAT_STYLE_VERBOSITY_MASK`, `XLAT_STYLE_FORMAT_MASK`, `XLAT_STYLE_SPEC_BITS`, `XLAT_STYLE_MASK`, `XLAT`, `XLAT_PAIR`, `XLAT_TYPE`, `XLAT_TYPE_PAIR`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/access_modes.in -->
# sources/test-tools/strace/src/xlat/access_modes.in

Purpose: Declarative xlat input table `access_modes` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `F_OK 0`
- Representative constants: `F_OK`, `R_OK`, `W_OK`, `X_OK`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/access_modes.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/addrfams.in -->
# sources/test-tools/strace/src/xlat/addrfams.in

Purpose: Declarative xlat input table `addrfams` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 46 constant rows, including `AF_UNSPEC	0`
- Representative constants: `AF_UNSPEC`, `AF_UNIX`, `AF_INET`, `AF_AX25`, `AF_IPX`, `AF_APPLETALK`, `AF_NETROM`, `AF_BRIDGE`, `AF_ATMPVC`, `AF_X25`...
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/linux/socket.h`, `#From include/uapi/linux/if_pppox.h`, `#From include/uapi/linux/tipc.h`, `#Prefix AF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/addrfams.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/adjtimex_modes.in -->
# sources/test-tools/strace/src/xlat/adjtimex_modes.in

Purpose: Declarative xlat input table `adjtimex_modes` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 13 constant rows, including `ADJ_OFFSET_SS_READ	0xa001`
- Representative constants: `ADJ_OFFSET_SS_READ`, `ADJ_OFFSET_SINGLESHOT`, `ADJ_OFFSET`, `ADJ_FREQUENCY`, `ADJ_MAXERROR`, `ADJ_ESTERROR`, `ADJ_STATUS`, `ADJ_TIMECONST`, `ADJ_TAI`, `ADJ_SETOFFSET`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/timex.h`, `#Prefix ADJ_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/adjtimex_modes.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/adjtimex_state.in -->
# sources/test-tools/strace/src/xlat/adjtimex_state.in

Purpose: Declarative xlat input table `adjtimex_state` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `TIME_OK		0`
- Representative constants: `TIME_OK`, `TIME_INS`, `TIME_DEL`, `TIME_OOP`, `TIME_WAIT`, `TIME_ERROR`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/timex.h`, `#Prefix TIME_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/adjtimex_state.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/adjtimex_status.in -->
# sources/test-tools/strace/src/xlat/adjtimex_status.in

Purpose: Declarative xlat input table `adjtimex_status` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 16 constant rows, including `STA_PLL		0x0001`
- Representative constants: `STA_PLL`, `STA_PPSFREQ`, `STA_PPSTIME`, `STA_FLL`, `STA_INS`, `STA_DEL`, `STA_UNSYNC`, `STA_FREQHOLD`, `STA_PPSSIGNAL`, `STA_PPSJITTER`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/timex.h`, `#Prefix STA_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/adjtimex_status.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/advise.in -->
# sources/test-tools/strace/src/xlat/advise.in

Purpose: Declarative xlat input table `advise` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `POSIX_FADV_NORMAL	0`
- Representative constants: `POSIX_FADV_NORMAL`, `POSIX_FADV_RANDOM`, `POSIX_FADV_SEQUENTIAL`, `POSIX_FADV_WILLNEED`, `POSIX_FADV_DONTNEED`, `POSIX_FADV_NOREUSE`, `POSIX_FADV_DONTNEED`, `POSIX_FADV_NOREUSE`
- Generator directives/preprocessor guards: `#From include/uapi/linux/fadvise.h`, `#Prefix POSIX_FADV_`, `#if defined __s390x__`, `#else`, `#endif`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/advise.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_packet_types.in -->
# sources/test-tools/strace/src/xlat/af_packet_types.in

Purpose: Declarative xlat input table `af_packet_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `PACKET_HOST		0`
- Representative constants: `PACKET_HOST`, `PACKET_BROADCAST`, `PACKET_MULTICAST`, `PACKET_OTHERHOST`, `PACKET_OUTGOING`, `PACKET_LOOPBACK`, `PACKET_USER`, `PACKET_KERNEL`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/if_packet.h`, `#Prefix PACKET_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_packet_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_packet_versions.in -->
# sources/test-tools/strace/src/xlat/af_packet_versions.in

Purpose: Declarative xlat input table `af_packet_versions` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `TPACKET_V1	0`
- Representative constants: `TPACKET_V1`, `TPACKET_V2`, `TPACKET_V3`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/if_packet.h`, `#Prefix TPACKET_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_packet_versions.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_flags.in -->
# sources/test-tools/strace/src/xlat/af_tipc_flags.in

Purpose: Declarative xlat input table `af_tipc_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `TIPC_GROUP_LOOPBACK`
- Representative constants: `TIPC_GROUP_LOOPBACK`, `TIPC_GROUP_MEMBER_EVTS`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/tipc.h`, `#Prefix TIPC_GROUP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_importance.in -->
# sources/test-tools/strace/src/xlat/af_tipc_importance.in

Purpose: Declarative xlat input table `af_tipc_importance` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `TIPC_LOW_IMPORTANCE`
- Representative constants: `TIPC_LOW_IMPORTANCE`, `TIPC_MEDIUM_IMPORTANCE`, `TIPC_HIGH_IMPORTANCE`, `TIPC_CRITICAL_IMPORTANCE`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/tipc.h`, `#Pattern TIPC_.*_IMPORTANCE`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_importance.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_scope.in -->
# sources/test-tools/strace/src/xlat/af_tipc_scope.in

Purpose: Declarative xlat input table `af_tipc_scope` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `TIPC_CLUSTER_SCOPE`
- Representative constants: `TIPC_CLUSTER_SCOPE`, `TIPC_NODE_SCOPE`
- Generator directives/preprocessor guards: `#Generated by maint/enum2xlat.sh from "enum tipc_scope" in bundled/linux/include/uapi/linux/tipc.h; do not edit.`, `#unconditional`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_scope.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_types.in -->
# sources/test-tools/strace/src/xlat/af_tipc_types.in

Purpose: Declarative xlat input table `af_tipc_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `TIPC_SERVICE_RANGE`
- Representative constants: `TIPC_SERVICE_RANGE`, `TIPC_SERVICE_ADDR`, `TIPC_SOCKET_ADDR`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/tipc.h`, `#Prefix TIPC_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/af_tipc_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/aio_cmds.in -->
# sources/test-tools/strace/src/xlat/aio_cmds.in

Purpose: Declarative xlat input table `aio_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `IOCB_CMD_PREAD		0`
- Representative constants: `IOCB_CMD_PREAD`, `IOCB_CMD_PWRITE`, `IOCB_CMD_FSYNC`, `IOCB_CMD_FDSYNC`, `IOCB_CMD_PREADX`, `IOCB_CMD_POLL`, `IOCB_CMD_NOOP`, `IOCB_CMD_PREADV`, `IOCB_CMD_PWRITEV`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/aio_abi.h`, `#Prefix IOCB_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/aio_cmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/aio_iocb_flags.in -->
# sources/test-tools/strace/src/xlat/aio_iocb_flags.in

Purpose: Declarative xlat input table `aio_iocb_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `IOCB_FLAG_RESFD		1`
- Representative constants: `IOCB_FLAG_RESFD`, `IOCB_FLAG_IOPRIO`
- Generator directives/preprocessor guards: `#From include/uapi/linux/aio_abi.h`, `#Prefix IOCB_FLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/aio_iocb_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/alg_sockaddr_flags.in -->
# sources/test-tools/strace/src/xlat/alg_sockaddr_flags.in

Purpose: Declarative xlat input table `alg_sockaddr_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `CRYPTO_ALG_KERN_DRIVER_ONLY	0x1000`
- Generator directives/preprocessor guards: `#From include/linux/crypto.h`, `#Prefix CRYPTO_ALG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/alg_sockaddr_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/alpha_trap_codes.in -->
# sources/test-tools/strace/src/xlat/alpha_trap_codes.in

Purpose: Declarative xlat input table `alpha_trap_codes` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 25 constant rows, including `GEN_INTOVF	-1`
- Representative constants: `GEN_INTOVF`, `GEN_INTDIV`, `GEN_FLTOVF`, `GEN_FLTDIV`, `GEN_FLTUND`, `GEN_FLTINV`, `GEN_FLTINE`, `GEN_DECOVF`, `GEN_DECDIV`, `GEN_DECINV`...
- Generator directives/preprocessor guards: `#From arch/alpha/include/uapi/asm/gentrap.h`, `#Prefix GEN_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/alpha_trap_codes.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/archvals.in -->
# sources/test-tools/strace/src/xlat/archvals.in

Purpose: Declarative xlat input table `archvals` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 23 constant rows, including `ARCH_SET_GS			0x1001`
- Representative constants: `ARCH_SET_GS`, `ARCH_SET_FS`, `ARCH_GET_FS`, `ARCH_GET_GS`, `ARCH_GET_CPUID`, `ARCH_SET_CPUID`, `ARCH_GET_XCOMP_SUPP`, `ARCH_GET_XCOMP_PERM`, `ARCH_REQ_XCOMP_PERM`, `ARCH_GET_XCOMP_GUEST_PERM`...
- Generator directives/preprocessor guards: `#sorted`, `#From arch/x86/include/uapi/asm/prctl.h`, `#Prefix ARCH_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/archvals.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/arp_hardware_types.in -->
# sources/test-tools/strace/src/xlat/arp_hardware_types.in

Purpose: Declarative xlat input table `arp_hardware_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 67 constant rows, including `ARPHRD_NETROM			0`
- Representative constants: `ARPHRD_NETROM`, `ARPHRD_ETHER`, `ARPHRD_EETHER`, `ARPHRD_AX25`, `ARPHRD_PRONET`, `ARPHRD_CHAOS`, `ARPHRD_IEEE802`, `ARPHRD_ARCNET`, `ARPHRD_APPLETLK`, `ARPHRD_DLCI`...
- Generator directives/preprocessor guards: `#sorted sort -k2,2g`, `#From include/uapi/linux/if_arp.h`, `#Prefix ARPHRD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/arp_hardware_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/at_flags.in -->
# sources/test-tools/strace/src/xlat/at_flags.in

Purpose: Declarative xlat input table `at_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `AT_SYMLINK_NOFOLLOW`
- Representative constants: `AT_SYMLINK_NOFOLLOW`, `AT_REMOVEDIR`, `AT_SYMLINK_FOLLOW`, `AT_NO_AUTOMOUNT`, `AT_EMPTY_PATH`, `AT_RECURSIVE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fcntl.h`, `#Prefix AT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/at_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/at_statx_sync_types.in -->
# sources/test-tools/strace/src/xlat/at_statx_sync_types.in

Purpose: Declarative xlat input table `at_statx_sync_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `AT_STATX_SYNC_AS_STAT	0x0000`
- Representative constants: `AT_STATX_SYNC_AS_STAT`, `AT_STATX_FORCE_SYNC`, `AT_STATX_DONT_SYNC`, `AT_STATX_SYNC_TYPE`
- Generator directives/preprocessor guards: `#From include/uapi/linux/fcntl.h`, `#Prefix AT_STATX_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/at_statx_sync_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/atomic_ops.in -->
# sources/test-tools/strace/src/xlat/atomic_ops.in

Purpose: Declarative xlat input table `atomic_ops` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 0 constant rows

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/atomic_ops.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/audit_arch.in -->
# sources/test-tools/strace/src/xlat/audit_arch.in

Purpose: Declarative xlat input table `audit_arch` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 54 constant rows, including `AUDIT_ARCH_AARCH64	(EM_AARCH64|__AUDIT_ARCH_64BIT|__AUDIT_ARCH_LE)`
- Representative constants: `AUDIT_ARCH_AARCH64`, `AUDIT_ARCH_ALPHA`, `AUDIT_ARCH_ARCOMPACT`, `AUDIT_ARCH_ARCOMPACTBE`, `AUDIT_ARCH_ARCV2`, `AUDIT_ARCH_ARCV2BE`, `AUDIT_ARCH_ARM`, `AUDIT_ARCH_ARMEB`, `AUDIT_ARCH_C6X`, `AUDIT_ARCH_C6XBE`...
- Generator directives/preprocessor guards: `#ifndef __AUDIT_ARCH_CONVENTION_MIPS64_N32`, `# define __AUDIT_ARCH_CONVENTION_MIPS64_N32	0x20000000`, `#endif`, `#ifndef __AUDIT_ARCH_64BIT`, `# define __AUDIT_ARCH_64BIT	0x80000000`, `#endif`, `#ifndef __AUDIT_ARCH_LE`, `# define __AUDIT_ARCH_LE	0x40000000`...

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/audit_arch.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ax25_protocols.in -->
# sources/test-tools/strace/src/xlat/ax25_protocols.in

Purpose: Declarative xlat input table `ax25_protocols` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: These constants should be part of UAPI Van Jacobsen (RFC 1144)

Important APIs/types/functions:
- Contains 13 constant rows, including `AX25_P_ROSE		0x01`
- Representative constants: `AX25_P_ROSE`, `AX25_P_VJCOMP`, `AX25_P_VJUNCOMP`, `AX25_P_SEGMENT`, `AX25_P_TEXNET`, `AX25_P_LQ`, `AX25_P_ATALK`, `AX25_P_ATALK_ARP`, `AX25_P_IP`, `AX25_P_ARP`...
- Generator directives/preprocessor guards: `#sorted`, `#From include/net/ax25.h`, `#Prefix AX25_P_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ax25_protocols.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/baud_options.in -->
# sources/test-tools/strace/src/xlat/baud_options.in

Purpose: Declarative xlat input table `baud_options` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 38 constant rows, including `B0`
- Representative constants: `B0`, `B50`, `B75`, `B110`, `B134`, `B150`, `B200`, `B300`, `B600`, `B1200`...
- Generator directives/preprocessor guards: `#From arch/sparc/include/uapi/asm/termbits.h`, `#From include/uapi/asm-generic/termbits-common.h`, `#From include/uapi/asm-generic/termbits.h`, `#Prefix B`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/baud_options.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bdaddr_types.in -->
# sources/test-tools/strace/src/xlat/bdaddr_types.in

Purpose: Declarative xlat input table `bdaddr_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BDADDR_BREDR		0`
- Representative constants: `BDADDR_BREDR`, `BDADDR_LE_PUBLIC`, `BDADDR_LE_RANDOM`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/net/bluetooth/bluetooth.h`, `#Prefix BDADDR_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bdaddr_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/blkpg_ops.in -->
# sources/test-tools/strace/src/xlat/blkpg_ops.in

Purpose: Declarative xlat input table `blkpg_ops` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BLKPG_ADD_PARTITION	1`
- Representative constants: `BLKPG_ADD_PARTITION`, `BLKPG_DEL_PARTITION`, `BLKPG_RESIZE_PARTITION`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/blkpg.h`, `#Pattern BLKPG_.*_PARTITION`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/blkpg_ops.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bluetooth_l2_cid.in -->
# sources/test-tools/strace/src/xlat/bluetooth_l2_cid.in

Purpose: Declarative xlat input table `bluetooth_l2_cid` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 10 constant rows, including `L2CAP_CID_SIGNALING	0x0001`
- Representative constants: `L2CAP_CID_SIGNALING`, `L2CAP_CID_CONN_LESS`, `L2CAP_CID_A2MP`, `L2CAP_CID_ATT`, `L2CAP_CID_LE_SIGNALING`, `L2CAP_CID_SMP`, `L2CAP_CID_SMP_BREDR`, `L2CAP_CID_DYN_START`, `L2CAP_CID_LE_DYN_END`, `L2CAP_CID_DYN_END`
- Generator directives/preprocessor guards: `#sorted sort -k2,2`, `#From include/net/bluetooth/l2cap.h`, `#Prefix L2CAP_CID_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bluetooth_l2_cid.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bluetooth_l2_psm.in -->
# sources/test-tools/strace/src/xlat/bluetooth_l2_psm.in

Purpose: Declarative xlat input table `bluetooth_l2_psm` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `L2CAP_PSM_SDP           0x0001`
- Representative constants: `L2CAP_PSM_SDP`, `L2CAP_PSM_RFCOMM`, `L2CAP_PSM_3DSP`, `L2CAP_PSM_IPSP`, `L2CAP_PSM_LE_DYN_START`, `L2CAP_PSM_LE_DYN_END`, `L2CAP_PSM_DYN_START`, `L2CAP_PSM_AUTO_END`, `L2CAP_PSM_DYN_END`
- Generator directives/preprocessor guards: `#sorted sort -k2,2`, `#From include/net/bluetooth/l2cap.h`, `#Prefix L2CAP_PSM_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bluetooth_l2_psm.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bootflags1.in -->
# sources/test-tools/strace/src/xlat/bootflags1.in

Purpose: Declarative xlat input table `bootflags1` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `LINUX_REBOOT_MAGIC1 0xfee1dead`
- Generator directives/preprocessor guards: `#From include/uapi/linux/reboot.h`, `#Prefix LINUX_REBOOT_MAGIC1`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bootflags1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bootflags2.in -->
# sources/test-tools/strace/src/xlat/bootflags2.in

Purpose: Declarative xlat input table `bootflags2` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `LINUX_REBOOT_MAGIC2 672274793`
- Representative constants: `LINUX_REBOOT_MAGIC2`, `LINUX_REBOOT_MAGIC2A`, `LINUX_REBOOT_MAGIC2B`, `LINUX_REBOOT_MAGIC2C`
- Generator directives/preprocessor guards: `#From include/uapi/linux/reboot.h`, `#Prefix LINUX_REBOOT_MAGIC2`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bootflags2.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bootflags3.in -->
# sources/test-tools/strace/src/xlat/bootflags3.in

Purpose: Declarative xlat input table `bootflags3` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `LINUX_REBOOT_CMD_RESTART 0x01234567`
- Representative constants: `LINUX_REBOOT_CMD_RESTART`, `LINUX_REBOOT_CMD_HALT`, `LINUX_REBOOT_CMD_CAD_ON`, `LINUX_REBOOT_CMD_CAD_OFF`, `LINUX_REBOOT_CMD_POWER_OFF`, `LINUX_REBOOT_CMD_RESTART2`, `LINUX_REBOOT_CMD_SW_SUSPEND`, `LINUX_REBOOT_CMD_KEXEC`
- Generator directives/preprocessor guards: `#From include/uapi/linux/reboot.h`, `#Prefix LINUX_REBOOT_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bootflags3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_attach_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_attach_flags.in

Purpose: Declarative xlat input table `bpf_attach_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `BPF_F_ALLOW_OVERRIDE	1U`
- Representative constants: `BPF_F_ALLOW_OVERRIDE`, `BPF_F_ALLOW_MULTI`, `BPF_F_REPLACE`, `BPF_F_BEFORE`, `BPF_F_AFTER`, `BPF_F_ID`, `BPF_F_PREORDER`, `BPF_F_LINK`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_attach_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_attach_type.in -->
# sources/test-tools/strace/src/xlat/bpf_attach_type.in

Purpose: Declarative xlat input table `bpf_attach_type` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 59 constant rows, including `BPF_CGROUP_INET_INGRESS 0`
- Representative constants: `BPF_CGROUP_INET_INGRESS`, `BPF_CGROUP_INET_EGRESS`, `BPF_CGROUP_INET_SOCK_CREATE`, `BPF_CGROUP_SOCK_OPS`, `BPF_SK_SKB_STREAM_PARSER`, `BPF_SK_SKB_STREAM_VERDICT`, `BPF_CGROUP_DEVICE`, `BPF_SK_MSG_VERDICT`, `BPF_CGROUP_INET4_BIND`, `BPF_CGROUP_INET6_BIND`...
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_attach_type.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_class.in -->
# sources/test-tools/strace/src/xlat/bpf_class.in

Purpose: Declarative xlat input table `bpf_class` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `BPF_LD		0x0`
- Representative constants: `BPF_LD`, `BPF_LDX`, `BPF_ST`, `BPF_STX`, `BPF_ALU`, `BPF_JMP`, `BPF_RET`, `BPF_MISC`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_class.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_commands.in -->
# sources/test-tools/strace/src/xlat/bpf_commands.in

Purpose: Declarative xlat input table `bpf_commands` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 39 constant rows, including `BPF_MAP_CREATE 0`
- Representative constants: `BPF_MAP_CREATE`, `BPF_MAP_LOOKUP_ELEM`, `BPF_MAP_UPDATE_ELEM`, `BPF_MAP_DELETE_ELEM`, `BPF_MAP_GET_NEXT_KEY`, `BPF_PROG_LOAD`, `BPF_OBJ_PIN`, `BPF_OBJ_GET`, `BPF_PROG_ATTACH`, `BPF_PROG_DETACH`...
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_commands.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_file_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_file_flags.in

Purpose: Declarative xlat input table `bpf_file_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `BPF_F_RDONLY		(1U << 3)`
- Representative constants: `BPF_F_RDONLY`, `BPF_F_WRONLY`, `BPF_F_PATH_FD`, `BPF_F_VTYPE_BTF_OBJ_FD`, `BPF_F_TOKEN_FD`, `BPF_F_SEGV_ON_FAULT`, `BPF_F_NO_USER_CONV`, `BPF_F_RB_OVERWRITE`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_file_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_file_mode_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_file_mode_flags.in

Purpose: Declarative xlat input table `bpf_file_mode_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `BPF_F_RDONLY	(1U << 3)`
- Representative constants: `BPF_F_RDONLY`, `BPF_F_WRONLY`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_file_mode_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_link_create_kprobe_multi_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_link_create_kprobe_multi_flags.in

Purpose: Declarative xlat input table `bpf_link_create_kprobe_multi_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BPF_F_KPROBE_MULTI_RETURN	(1U << 0)`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_KPROBE_MULTI_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_link_create_kprobe_multi_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_link_create_netfilter_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_link_create_netfilter_flags.in

Purpose: Declarative xlat input table `bpf_link_create_netfilter_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BPF_F_NETFILTER_IP_DEFRAG	(1U << 0)`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_NETFILTER_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_link_create_netfilter_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_link_create_uprobe_multi_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_link_create_uprobe_multi_flags.in

Purpose: Declarative xlat input table `bpf_link_create_uprobe_multi_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BPF_F_UPROBE_MULTI_RETURN	(1U << 0)`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_UPROBE_MULTI_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_link_create_uprobe_multi_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_map_flags.in

Purpose: Declarative xlat input table `bpf_map_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 14 constant rows, including `BPF_F_NO_PREALLOC	1U`
- Representative constants: `BPF_F_NO_PREALLOC`, `BPF_F_NO_COMMON_LRU`, `BPF_F_NUMA_NODE`, `BPF_F_RDONLY`, `BPF_F_WRONLY`, `BPF_F_STACK_BUILD_ID`, `BPF_F_ZERO_SEED`, `BPF_F_RDONLY_PROG`, `BPF_F_WRONLY_PROG`, `BPF_F_CLONE`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_lookup_elem_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_map_lookup_elem_flags.in

Purpose: Declarative xlat input table `bpf_map_lookup_elem_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: flag bits with higher value first, BPF_ANY(0) last

Important APIs/types/functions:
- Contains 4 constant rows, including `BPF_F_ALL_CPUS	16`
- Representative constants: `BPF_F_ALL_CPUS`, `BPF_F_CPU`, `BPF_F_LOCK`, `BPF_ANY`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_lookup_elem_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_types.in -->
# sources/test-tools/strace/src/xlat/bpf_map_types.in

Purpose: Declarative xlat input table `bpf_map_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 35 constant rows, including `BPF_MAP_TYPE_UNSPEC 0`
- Representative constants: `BPF_MAP_TYPE_UNSPEC`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_PROG_ARRAY`, `BPF_MAP_TYPE_PERF_EVENT_ARRAY`, `BPF_MAP_TYPE_PERCPU_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`, `BPF_MAP_TYPE_STACK_TRACE`, `BPF_MAP_TYPE_CGROUP_ARRAY`, `BPF_MAP_TYPE_LRU_HASH`...
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#Prefix BPF_MAP_TYPE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_update_elem_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_map_update_elem_flags.in

Purpose: Declarative xlat input table `bpf_map_update_elem_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: higher-valued bits and mutual modes first, BPF_ANY(0) last

Important APIs/types/functions:
- Contains 6 constant rows, including `BPF_F_ALL_CPUS	16`
- Representative constants: `BPF_F_ALL_CPUS`, `BPF_F_CPU`, `BPF_F_LOCK`, `BPF_EXIST`, `BPF_NOEXIST`, `BPF_ANY`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_map_update_elem_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_miscop.in -->
# sources/test-tools/strace/src/xlat/bpf_miscop.in

Purpose: Declarative xlat input table `bpf_miscop` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `BPF_TAX	0x00`
- Representative constants: `BPF_TAX`, `BPF_TXA`
- Generator directives/preprocessor guards: `#From include/uapi/linux/filter.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_miscop.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_mode.in -->
# sources/test-tools/strace/src/xlat/bpf_mode.in

Purpose: Declarative xlat input table `bpf_mode` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 7 constant rows, including `BPF_IMM		0x00`
- Representative constants: `BPF_IMM`, `BPF_ABS`, `BPF_IND`, `BPF_MEM`, `BPF_LEN`, `BPF_MSH`, `BPF_XADD`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_mode.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_op_alu.in -->
# sources/test-tools/strace/src/xlat/bpf_op_alu.in

Purpose: Declarative xlat input table `bpf_op_alu` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 14 constant rows, including `BPF_ADD		0x00`
- Representative constants: `BPF_ADD`, `BPF_SUB`, `BPF_MUL`, `BPF_DIV`, `BPF_OR`, `BPF_AND`, `BPF_LSH`, `BPF_RSH`, `BPF_NEG`, `BPF_MOD`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_op_alu.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_op_jmp.in -->
# sources/test-tools/strace/src/xlat/bpf_op_jmp.in

Purpose: Declarative xlat input table `bpf_op_jmp` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 15 constant rows, including `BPF_JA		0x00`
- Representative constants: `BPF_JA`, `BPF_JEQ`, `BPF_JGT`, `BPF_JGE`, `BPF_JSET`, `BPF_JNE`, `BPF_JSGT`, `BPF_JSGE`, `BPF_CALL`, `BPF_EXIT`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_op_jmp.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_prog_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_prog_flags.in

Purpose: Declarative xlat input table `bpf_prog_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `BPF_F_STRICT_ALIGNMENT		1U`
- Representative constants: `BPF_F_STRICT_ALIGNMENT`, `BPF_F_ANY_ALIGNMENT`, `BPF_F_TEST_RND_HI32`, `BPF_F_TEST_STATE_FREQ`, `BPF_F_SLEEPABLE`, `BPF_F_XDP_HAS_FRAGS`, `BPF_F_XDP_DEV_BOUND_ONLY`, `BPF_F_TEST_REG_INVARIANTS`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_prog_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_prog_types.in -->
# sources/test-tools/strace/src/xlat/bpf_prog_types.in

Purpose: Declarative xlat input table `bpf_prog_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 33 constant rows, including `BPF_PROG_TYPE_UNSPEC 0`
- Representative constants: `BPF_PROG_TYPE_UNSPEC`, `BPF_PROG_TYPE_SOCKET_FILTER`, `BPF_PROG_TYPE_KPROBE`, `BPF_PROG_TYPE_SCHED_CLS`, `BPF_PROG_TYPE_SCHED_ACT`, `BPF_PROG_TYPE_TRACEPOINT`, `BPF_PROG_TYPE_XDP`, `BPF_PROG_TYPE_PERF_EVENT`, `BPF_PROG_TYPE_CGROUP_SKB`, `BPF_PROG_TYPE_CGROUP_SOCK`...
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#Prefix BPF_PROG_TYPE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_prog_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_query_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_query_flags.in

Purpose: Declarative xlat input table `bpf_query_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BPF_F_QUERY_EFFECTIVE	(1U << 0)`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_QUERY_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_query_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_rval.in -->
# sources/test-tools/strace/src/xlat/bpf_rval.in

Purpose: Declarative xlat input table `bpf_rval` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BPF_K	0x00`
- Representative constants: `BPF_K`, `BPF_X`, `BPF_A`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf_common.h`, `#From include/uapi/linux/filter.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_rval.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_size.in -->
# sources/test-tools/strace/src/xlat/bpf_size.in

Purpose: Declarative xlat input table `bpf_size` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BPF_W	0x00`
- Representative constants: `BPF_W`, `BPF_H`, `BPF_B`, `BPF_DW`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_size.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_src.in -->
# sources/test-tools/strace/src/xlat/bpf_src.in

Purpose: Declarative xlat input table `bpf_src` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `BPF_K	0x00`
- Representative constants: `BPF_K`, `BPF_X`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_src.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_stats_type.in -->
# sources/test-tools/strace/src/xlat/bpf_stats_type.in

Purpose: Declarative xlat input table `bpf_stats_type` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BPF_STATS_RUN_TIME	0`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#Prefix BPF_STATS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_stats_type.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_task_fd_type.in -->
# sources/test-tools/strace/src/xlat/bpf_task_fd_type.in

Purpose: Declarative xlat input table `bpf_task_fd_type` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `BPF_FD_TYPE_RAW_TRACEPOINT	0`
- Representative constants: `BPF_FD_TYPE_RAW_TRACEPOINT`, `BPF_FD_TYPE_TRACEPOINT`, `BPF_FD_TYPE_KPROBE`, `BPF_FD_TYPE_KRETPROBE`, `BPF_FD_TYPE_UPROBE`, `BPF_FD_TYPE_URETPROBE`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#Prefix BPF_FD_TYPE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_task_fd_type.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_test_run_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_test_run_flags.in

Purpose: Declarative xlat input table `bpf_test_run_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `BPF_F_TEST_RUN_ON_CPU		(1U << 0)`
- Representative constants: `BPF_F_TEST_RUN_ON_CPU`, `BPF_F_TEST_XDP_LIVE_FRAMES`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_TEST_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_test_run_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bsg_flags.in -->
# sources/test-tools/strace/src/xlat/bsg_flags.in

Purpose: Declarative xlat input table `bsg_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `BSG_FLAG_Q_AT_TAIL`
- Representative constants: `BSG_FLAG_Q_AT_TAIL`, `BSG_FLAG_Q_AT_HEAD`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/bsg.h`, `#Prefix BSG_FLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bsg_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bsg_protocol.in -->
# sources/test-tools/strace/src/xlat/bsg_protocol.in

Purpose: Declarative xlat input table `bsg_protocol` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BSG_PROTOCOL_SCSI`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/bsg.h`, `#Prefix BSG_PROTOCOL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bsg_protocol.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bsg_subprotocol.in -->
# sources/test-tools/strace/src/xlat/bsg_subprotocol.in

Purpose: Declarative xlat input table `bsg_subprotocol` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BSG_SUB_PROTOCOL_SCSI_CMD`
- Representative constants: `BSG_SUB_PROTOCOL_SCSI_CMD`, `BSG_SUB_PROTOCOL_SCSI_TMF`, `BSG_SUB_PROTOCOL_SCSI_TRANSPORT`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/bsg.h`, `#Prefix BSG_SUB_PROTOCOL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bsg_subprotocol.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bt_protocols.in -->
# sources/test-tools/strace/src/xlat/bt_protocols.in

Purpose: Declarative xlat input table `bt_protocols` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `BTPROTO_L2CAP	0`
- Representative constants: `BTPROTO_L2CAP`, `BTPROTO_HCI`, `BTPROTO_SCO`, `BTPROTO_RFCOMM`, `BTPROTO_BNEP`, `BTPROTO_CMTP`, `BTPROTO_HIDP`, `BTPROTO_AVDTP`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/net/bluetooth/bluetooth.h`, `#Prefix BTPROTO_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bt_protocols.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_args.in -->
# sources/test-tools/strace/src/xlat/btrfs_balance_args.in

Purpose: Declarative xlat input table `btrfs_balance_args` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `BTRFS_BALANCE_ARGS_PROFILES`
- Representative constants: `BTRFS_BALANCE_ARGS_PROFILES`, `BTRFS_BALANCE_ARGS_USAGE`, `BTRFS_BALANCE_ARGS_DEVID`, `BTRFS_BALANCE_ARGS_DRANGE`, `BTRFS_BALANCE_ARGS_VRANGE`, `BTRFS_BALANCE_ARGS_LIMIT`, `BTRFS_BALANCE_ARGS_LIMIT_RANGE`, `BTRFS_BALANCE_ARGS_STRIPES_RANGE`, `BTRFS_BALANCE_ARGS_CONVERT`, `BTRFS_BALANCE_ARGS_SOFT`...
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_BALANCE_ARGS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_args.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_ctl_cmds.in -->
# sources/test-tools/strace/src/xlat/btrfs_balance_ctl_cmds.in

Purpose: Declarative xlat input table `btrfs_balance_ctl_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `BTRFS_BALANCE_CTL_PAUSE`
- Representative constants: `BTRFS_BALANCE_CTL_PAUSE`, `BTRFS_BALANCE_CTL_CANCEL`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_BALANCE_CTL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_ctl_cmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_balance_flags.in

Purpose: Declarative xlat input table `btrfs_balance_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 5 constant rows, including `BTRFS_BALANCE_DATA`
- Representative constants: `BTRFS_BALANCE_DATA`, `BTRFS_BALANCE_SYSTEM`, `BTRFS_BALANCE_METADATA`, `BTRFS_BALANCE_FORCE`, `BTRFS_BALANCE_RESUME`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_BALANCE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_state.in -->
# sources/test-tools/strace/src/xlat/btrfs_balance_state.in

Purpose: Declarative xlat input table `btrfs_balance_state` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BTRFS_BALANCE_STATE_RUNNING`
- Representative constants: `BTRFS_BALANCE_STATE_RUNNING`, `BTRFS_BALANCE_STATE_PAUSE_REQ`, `BTRFS_BALANCE_STATE_CANCEL_REQ`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_BALANCE_STATE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_balance_state.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_compress_types.in -->
# sources/test-tools/strace/src/xlat/btrfs_compress_types.in

Purpose: Declarative xlat input table `btrfs_compress_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BTRFS_COMPRESS_NONE 0`
- Representative constants: `BTRFS_COMPRESS_NONE`, `BTRFS_COMPRESS_ZLIB`, `BTRFS_COMPRESS_LZO`, `BTRFS_COMPRESS_ZSTD`
- Generator directives/preprocessor guards: `#value_indexed`, `#From fs/btrfs/fs.h`, `#Prefix BTRFS_COMPRESS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_compress_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_cont_reading_from_srcdev_mode.in -->
# sources/test-tools/strace/src/xlat/btrfs_cont_reading_from_srcdev_mode.in

Purpose: Declarative xlat input table `btrfs_cont_reading_from_srcdev_mode` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `BTRFS_IOCTL_DEV_REPLACE_CONT_READING_FROM_SRCDEV_MODE_ALWAYS`
- Representative constants: `BTRFS_IOCTL_DEV_REPLACE_CONT_READING_FROM_SRCDEV_MODE_ALWAYS`, `BTRFS_IOCTL_DEV_REPLACE_CONT_READING_FROM_SRCDEV_MODE_AVOID`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_IOCTL_DEV_REPLACE_CONT_READING_FROM_SRCDEV_MODE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_cont_reading_from_srcdev_mode.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_csum_types.in -->
# sources/test-tools/strace/src/xlat/btrfs_csum_types.in

Purpose: Declarative xlat input table `btrfs_csum_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BTRFS_CSUM_TYPE_CRC32`
- Representative constants: `BTRFS_CSUM_TYPE_CRC32`, `BTRFS_CSUM_TYPE_XXHASH`, `BTRFS_CSUM_TYPE_SHA256`, `BTRFS_CSUM_TYPE_BLAKE2`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/btrfs_tree.h`, `#Prefix BTRFS_CSUM_TYPE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_csum_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_defrag_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_defrag_flags.in

Purpose: Declarative xlat input table `btrfs_defrag_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BTRFS_DEFRAG_RANGE_COMPRESS`
- Representative constants: `BTRFS_DEFRAG_RANGE_COMPRESS`, `BTRFS_DEFRAG_RANGE_START_IO`, `BTRFS_DEFRAG_RANGE_COMPRESS_LEVEL`, `BTRFS_DEFRAG_RANGE_NOCOMPRESS`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_DEFRAG_RANGE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_defrag_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_replace_cmds.in -->
# sources/test-tools/strace/src/xlat/btrfs_dev_replace_cmds.in

Purpose: Declarative xlat input table `btrfs_dev_replace_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BTRFS_IOCTL_DEV_REPLACE_CMD_START`
- Representative constants: `BTRFS_IOCTL_DEV_REPLACE_CMD_START`, `BTRFS_IOCTL_DEV_REPLACE_CMD_STATUS`, `BTRFS_IOCTL_DEV_REPLACE_CMD_CANCEL`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_IOCTL_DEV_REPLACE_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_replace_cmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_replace_results.in -->
# sources/test-tools/strace/src/xlat/btrfs_dev_replace_results.in

Purpose: Declarative xlat input table `btrfs_dev_replace_results` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BTRFS_IOCTL_DEV_REPLACE_RESULT_NO_ERROR`
- Representative constants: `BTRFS_IOCTL_DEV_REPLACE_RESULT_NO_ERROR`, `BTRFS_IOCTL_DEV_REPLACE_RESULT_NOT_STARTED`, `BTRFS_IOCTL_DEV_REPLACE_RESULT_ALREADY_STARTED`, `BTRFS_IOCTL_DEV_REPLACE_RESULT_SCRUB_INPROGRESS`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_IOCTL_DEV_REPLACE_RESULT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_replace_results.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_replace_state.in -->
# sources/test-tools/strace/src/xlat/btrfs_dev_replace_state.in

Purpose: Declarative xlat input table `btrfs_dev_replace_state` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 5 constant rows, including `BTRFS_IOCTL_DEV_REPLACE_STATE_NEVER_STARTED`
- Representative constants: `BTRFS_IOCTL_DEV_REPLACE_STATE_NEVER_STARTED`, `BTRFS_IOCTL_DEV_REPLACE_STATE_STARTED`, `BTRFS_IOCTL_DEV_REPLACE_STATE_FINISHED`, `BTRFS_IOCTL_DEV_REPLACE_STATE_CANCELED`, `BTRFS_IOCTL_DEV_REPLACE_STATE_SUSPENDED`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_IOCTL_DEV_REPLACE_STATE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_replace_state.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_stats_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_dev_stats_flags.in

Purpose: Declarative xlat input table `btrfs_dev_stats_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BTRFS_DEV_STATS_RESET`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_DEV_STATS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_stats_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_stats_values.in -->
# sources/test-tools/strace/src/xlat/btrfs_dev_stats_values.in

Purpose: Declarative xlat input table `btrfs_dev_stats_values` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 5 constant rows, including `BTRFS_DEV_STAT_WRITE_ERRS`
- Representative constants: `BTRFS_DEV_STAT_WRITE_ERRS`, `BTRFS_DEV_STAT_READ_ERRS`, `BTRFS_DEV_STAT_FLUSH_ERRS`, `BTRFS_DEV_STAT_CORRUPTION_ERRS`, `BTRFS_DEV_STAT_GENERATION_ERRS`
- Generator directives/preprocessor guards: `#Generated by maint/enum2xlat.sh from "enum btrfs_dev_stat_values" in bundled/linux/include/uapi/linux/btrfs.h; do not edit.`, `#unconditional`, `#value_indexed`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_dev_stats_values.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_features_compat.in -->
# sources/test-tools/strace/src/xlat/btrfs_features_compat.in

Purpose: Declarative xlat input table `btrfs_features_compat` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 0 constant rows

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_features_compat.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_features_compat_ro.in -->
# sources/test-tools/strace/src/xlat/btrfs_features_compat_ro.in

Purpose: Declarative xlat input table `btrfs_features_compat_ro` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BTRFS_FEATURE_COMPAT_RO_FREE_SPACE_TREE`
- Representative constants: `BTRFS_FEATURE_COMPAT_RO_FREE_SPACE_TREE`, `BTRFS_FEATURE_COMPAT_RO_FREE_SPACE_TREE_VALID`, `BTRFS_FEATURE_COMPAT_RO_VERITY`, `BTRFS_FEATURE_COMPAT_RO_BLOCK_GROUP_TREE`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_FEATURE_COMPAT_RO_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_features_compat_ro.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_features_incompat.in -->
# sources/test-tools/strace/src/xlat/btrfs_features_incompat.in

Purpose: Declarative xlat input table `btrfs_features_incompat` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 17 constant rows, including `BTRFS_FEATURE_INCOMPAT_MIXED_BACKREF`
- Representative constants: `BTRFS_FEATURE_INCOMPAT_MIXED_BACKREF`, `BTRFS_FEATURE_INCOMPAT_DEFAULT_SUBVOL`, `BTRFS_FEATURE_INCOMPAT_MIXED_GROUPS`, `BTRFS_FEATURE_INCOMPAT_COMPRESS_LZO`, `BTRFS_FEATURE_INCOMPAT_COMPRESS_ZSTD`, `BTRFS_FEATURE_INCOMPAT_BIG_METADATA`, `BTRFS_FEATURE_INCOMPAT_EXTENDED_IREF`, `BTRFS_FEATURE_INCOMPAT_RAID56`, `BTRFS_FEATURE_INCOMPAT_SKINNY_METADATA`, `BTRFS_FEATURE_INCOMPAT_NO_HOLES`...
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_FEATURE_INCOMPAT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_features_incompat.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_fs_info_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_fs_info_flags.in

Purpose: Declarative xlat input table `btrfs_fs_info_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BTRFS_FS_INFO_FLAG_CSUM_INFO`
- Representative constants: `BTRFS_FS_INFO_FLAG_CSUM_INFO`, `BTRFS_FS_INFO_FLAG_GENERATION`, `BTRFS_FS_INFO_FLAG_METADATA_UUID`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_FS_INFO_FLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_fs_info_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_key_types.in -->
# sources/test-tools/strace/src/xlat/btrfs_key_types.in

Purpose: Declarative xlat input table `btrfs_key_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 46 constant rows, including `BTRFS_INODE_ITEM_KEY`
- Representative constants: `BTRFS_INODE_ITEM_KEY`, `BTRFS_INODE_REF_KEY`, `BTRFS_INODE_EXTREF_KEY`, `BTRFS_XATTR_ITEM_KEY`, `BTRFS_VERITY_DESC_ITEM_KEY`, `BTRFS_VERITY_MERKLE_ITEM_KEY`, `BTRFS_ORPHAN_ITEM_KEY`, `BTRFS_DIR_LOG_ITEM_KEY`, `BTRFS_DIR_LOG_INDEX_KEY`, `BTRFS_DIR_ITEM_KEY`...
- Generator directives/preprocessor guards: `#sorted`, `#val_type uint64_t`, `#From include/linux/libfdt_env.h`, `#From include/uapi/linux/btrfs_tree.h`, `#Prefix BTRFS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_key_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_logical_ino_args_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_logical_ino_args_flags.in

Purpose: Declarative xlat input table `btrfs_logical_ino_args_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BTRFS_LOGICAL_INO_ARGS_IGNORE_OFFSET`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_LOGICAL_INO_ARGS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_logical_ino_args_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_ctl_cmds.in -->
# sources/test-tools/strace/src/xlat/btrfs_qgroup_ctl_cmds.in

Purpose: Declarative xlat input table `btrfs_qgroup_ctl_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BTRFS_QUOTA_CTL_ENABLE`
- Representative constants: `BTRFS_QUOTA_CTL_ENABLE`, `BTRFS_QUOTA_CTL_DISABLE`, `BTRFS_QUOTA_CTL_RESCAN__NOTUSED`, `BTRFS_QUOTA_CTL_ENABLE_SIMPLE_QUOTA`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_QUOTA_CTL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_ctl_cmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_inherit_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_qgroup_inherit_flags.in

Purpose: Declarative xlat input table `btrfs_qgroup_inherit_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BTRFS_QGROUP_INHERIT_SET_LIMITS`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_QGROUP_INHERIT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_inherit_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_limit_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_qgroup_limit_flags.in

Purpose: Declarative xlat input table `btrfs_qgroup_limit_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `BTRFS_QGROUP_LIMIT_MAX_RFER`
- Representative constants: `BTRFS_QGROUP_LIMIT_MAX_RFER`, `BTRFS_QGROUP_LIMIT_MAX_EXCL`, `BTRFS_QGROUP_LIMIT_RSV_RFER`, `BTRFS_QGROUP_LIMIT_RSV_EXCL`, `BTRFS_QGROUP_LIMIT_RFER_CMPR`, `BTRFS_QGROUP_LIMIT_EXCL_CMPR`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_QGROUP_LIMIT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_limit_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_status_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_qgroup_status_flags.in

Purpose: Declarative xlat input table `btrfs_qgroup_status_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `BTRFS_QGROUP_STATUS_FLAG_ON`
- Representative constants: `BTRFS_QGROUP_STATUS_FLAG_ON`, `BTRFS_QGROUP_STATUS_FLAG_RESCAN`, `BTRFS_QGROUP_STATUS_FLAG_INCONSISTENT`, `BTRFS_QGROUP_STATUS_FLAG_SIMPLE_MODE`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs_tree.h`, `#Prefix BTRFS_QGROUP_STATUS_FLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_qgroup_status_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_scrub_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_scrub_flags.in

Purpose: Declarative xlat input table `btrfs_scrub_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BTRFS_SCRUB_READONLY`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_SCRUB_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_scrub_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_send_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_send_flags.in

Purpose: Declarative xlat input table `btrfs_send_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 5 constant rows, including `BTRFS_SEND_FLAG_NO_FILE_DATA`
- Representative constants: `BTRFS_SEND_FLAG_NO_FILE_DATA`, `BTRFS_SEND_FLAG_OMIT_STREAM_HEADER`, `BTRFS_SEND_FLAG_OMIT_END_CMD`, `BTRFS_SEND_FLAG_VERSION`, `BTRFS_SEND_FLAG_COMPRESSED`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_SEND_FLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_send_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_snap_flags_v2.in -->
# sources/test-tools/strace/src/xlat/btrfs_snap_flags_v2.in

Purpose: Declarative xlat input table `btrfs_snap_flags_v2` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BTRFS_SUBVOL_CREATE_ASYNC`
- Representative constants: `BTRFS_SUBVOL_CREATE_ASYNC`, `BTRFS_SUBVOL_RDONLY`, `BTRFS_SUBVOL_QGROUP_INHERIT`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs.h`, `#Prefix BTRFS_SUBVOL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_snap_flags_v2.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_space_info_flags.in -->
# sources/test-tools/strace/src/xlat/btrfs_space_info_flags.in

Purpose: Declarative xlat input table `btrfs_space_info_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 15 constant rows, including `BTRFS_BLOCK_GROUP_DATA`
- Representative constants: `BTRFS_BLOCK_GROUP_DATA`, `BTRFS_BLOCK_GROUP_SYSTEM`, `BTRFS_BLOCK_GROUP_METADATA`, `BTRFS_BLOCK_GROUP_RAID0`, `BTRFS_BLOCK_GROUP_RAID1`, `BTRFS_BLOCK_GROUP_DUP`, `BTRFS_BLOCK_GROUP_RAID10`, `BTRFS_BLOCK_GROUP_RAID5`, `BTRFS_BLOCK_GROUP_RAID6`, `BTRFS_BLOCK_GROUP_RAID1C3`...
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs_tree.h`, `#Prefix BTRFS_BLOCK_GROUP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_space_info_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_tree_objectids.in -->
# sources/test-tools/strace/src/xlat/btrfs_tree_objectids.in

Purpose: Declarative xlat input table `btrfs_tree_objectids` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 16 constant rows, including `BTRFS_ROOT_TREE_OBJECTID`
- Representative constants: `BTRFS_ROOT_TREE_OBJECTID`, `BTRFS_EXTENT_TREE_OBJECTID`, `BTRFS_CHUNK_TREE_OBJECTID`, `BTRFS_DEV_TREE_OBJECTID`, `BTRFS_FS_TREE_OBJECTID`, `BTRFS_ROOT_TREE_DIR_OBJECTID`, `BTRFS_CSUM_TREE_OBJECTID`, `BTRFS_QUOTA_TREE_OBJECTID`, `BTRFS_UUID_TREE_OBJECTID`, `BTRFS_FREE_SPACE_TREE_OBJECTID`...
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/btrfs_tree.h`, `#Prefix BTRFS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_tree_objectids.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cacheflush_flags.in -->
# sources/test-tools/strace/src/xlat/cacheflush_flags.in

Purpose: Declarative xlat input table `cacheflush_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `FLUSH_CACHE_BOTH	3`
- Representative constants: `FLUSH_CACHE_BOTH`, `FLUSH_CACHE_DATA`, `FLUSH_CACHE_INSN`, `BCACHE`, `ICACHE`, `DCACHE`, `BCACHE`, `ICACHE`, `DCACHE`, `CACHEFLUSH_D_INVAL`...
- Generator directives/preprocessor guards: `#From arch/arc/include/uapi/asm/cachectl.h`, `#From arch/m68k/include/uapi/asm/cachectl.h`, `#From arch/sh/include/uapi/asm/cachectl.h`, `#if defined M68K`, `#elif defined BFIN || defined CSKY`, `#elif defined SH`, `#endif`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cacheflush_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cacheflush_scope.in -->
# sources/test-tools/strace/src/xlat/cacheflush_scope.in

Purpose: Declarative xlat input table `cacheflush_scope` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `FLUSH_SCOPE_LINE`
- Representative constants: `FLUSH_SCOPE_LINE`, `FLUSH_SCOPE_PAGE`, `FLUSH_SCOPE_ALL`
- Generator directives/preprocessor guards: `#From arch/m68k/include/uapi/asm/cachectl.h`, `#Prefix FLUSH_SCOPE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cacheflush_scope.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/caif_protocols.in -->
# sources/test-tools/strace/src/xlat/caif_protocols.in

Purpose: Declarative xlat input table `caif_protocols` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `CAIFPROTO_AT		0`
- Representative constants: `CAIFPROTO_AT`, `CAIFPROTO_DATAGRAM`, `CAIFPROTO_DATAGRAM_LOOP`, `CAIFPROTO_UTIL`, `CAIFPROTO_RFM`, `CAIFPROTO_DEBUG`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/caif/caif_socket.h`, `#Prefix CAIFPROTO_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/caif_protocols.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/can_protocols.in -->
# sources/test-tools/strace/src/xlat/can_protocols.in

Purpose: Declarative xlat input table `can_protocols` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 7 constant rows, including `CAN_RAW		1`
- Representative constants: `CAN_RAW`, `CAN_BCM`, `CAN_TP16`, `CAN_TP20`, `CAN_MCNET`, `CAN_ISOTP`, `CAN_J1939`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/can.h`, `#Prefix CAN_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/can_protocols.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap.in -->
# sources/test-tools/strace/src/xlat/cap.in

Purpose: Declarative xlat input table `cap` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 41 constant rows, including `CAP_CHOWN`
- Representative constants: `CAP_CHOWN`, `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, `CAP_FOWNER`, `CAP_FSETID`, `CAP_KILL`, `CAP_SETGID`, `CAP_SETUID`, `CAP_SETPCAP`, `CAP_LINUX_IMMUTABLE`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/capability.h`, `#Prefix CAP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap_mask0.in -->
# sources/test-tools/strace/src/xlat/cap_mask0.in

Purpose: Declarative xlat input table `cap_mask0` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 32 constant rows, including `1<<CAP_CHOWN`
- Representative constants: `1<<CAP_CHOWN`, `1<<CAP_DAC_OVERRIDE`, `1<<CAP_DAC_READ_SEARCH`, `1<<CAP_FOWNER`, `1<<CAP_FSETID`, `1<<CAP_KILL`, `1<<CAP_SETGID`, `1<<CAP_SETUID`, `1<<CAP_SETPCAP`, `1<<CAP_LINUX_IMMUTABLE`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/capability.h`, `#Prefix CAP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap_mask0.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap_mask1.in -->
# sources/test-tools/strace/src/xlat/cap_mask1.in

Purpose: Declarative xlat input table `cap_mask1` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `1<<CAP_MAC_OVERRIDE`
- Representative constants: `1<<CAP_MAC_OVERRIDE`, `1<<CAP_MAC_ADMIN`, `1<<CAP_SYSLOG`, `1<<CAP_WAKE_ALARM`, `1<<CAP_BLOCK_SUSPEND`, `1<<CAP_AUDIT_READ`, `1<<CAP_PERFMON`, `1<<CAP_BPF`, `1<<CAP_CHECKPOINT_RESTORE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/capability.h`, `#Prefix CAP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap_mask1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap_version.in -->
# sources/test-tools/strace/src/xlat/cap_version.in

Purpose: Declarative xlat input table `cap_version` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `_LINUX_CAPABILITY_VERSION_1`
- Representative constants: `_LINUX_CAPABILITY_VERSION_1`, `_LINUX_CAPABILITY_VERSION_2`, `_LINUX_CAPABILITY_VERSION_3`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/capability.h`, `#Prefix _LINUX_CAPABILITY_VERSION_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cap_version.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clockflags.in -->
# sources/test-tools/strace/src/xlat/clockflags.in

Purpose: Declarative xlat input table `clockflags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `TIMER_ABSTIME`
- Generator directives/preprocessor guards: `#From include/uapi/linux/time.h`, `#Prefix TIMER_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clockflags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clocknames.in -->
# sources/test-tools/strace/src/xlat/clocknames.in

Purpose: Declarative xlat input table `clocknames` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 12 constant rows, including `CLOCK_REALTIME 0`
- Representative constants: `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_PROCESS_CPUTIME_ID`, `CLOCK_THREAD_CPUTIME_ID`, `CLOCK_MONOTONIC_RAW`, `CLOCK_REALTIME_COARSE`, `CLOCK_MONOTONIC_COARSE`, `CLOCK_BOOTTIME`, `CLOCK_REALTIME_ALARM`, `CLOCK_BOOTTIME_ALARM`...
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/time.h`, `#Prefix CLOCK_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clocknames.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clone3_flags.in -->
# sources/test-tools/strace/src/xlat/clone3_flags.in

Purpose: Declarative xlat input table `clone3_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 7 constant rows, including `CLONE_NEWTIME`
- Representative constants: `CLONE_NEWTIME`, `CLONE_CLEAR_SIGHAND`, `CLONE_INTO_CGROUP`, `CLONE_AUTOREAP`, `CLONE_NNP`, `CLONE_PIDFD_AUTOKILL`, `CLONE_EMPTY_MNTNS`
- Generator directives/preprocessor guards: `#unconditional`, `#val_type uint64_t`, `#From include/uapi/linux/sched.h`, `#Prefix CLONE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clone3_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clone_flags.in -->
# sources/test-tools/strace/src/xlat/clone_flags.in

Purpose: Declarative xlat input table `clone_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: CLONE_DETACHED ignored by kernel

Important APIs/types/functions:
- Contains 23 constant rows, including `CLONE_VM`
- Representative constants: `CLONE_VM`, `CLONE_FS`, `CLONE_FILES`, `CLONE_SIGHAND`, `CLONE_PIDFD`, `CLONE_PTRACE`, `CLONE_VFORK`, `CLONE_PARENT`, `CLONE_THREAD`, `CLONE_NEWNS`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/sched.h`, `#Prefix CLONE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/clone_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/close_range_flags.in -->
# sources/test-tools/strace/src/xlat/close_range_flags.in

Purpose: Declarative xlat input table `close_range_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `CLOSE_RANGE_UNSHARE`
- Representative constants: `CLOSE_RANGE_UNSHARE`, `CLOSE_RANGE_CLOEXEC`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/close_range.h`, `#Prefix CLOSE_RANGE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/close_range_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/compat_ptrace_cmds.in -->
# sources/test-tools/strace/src/xlat/compat_ptrace_cmds.in

Purpose: Declarative xlat input table `compat_ptrace_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as:  These two are not defined in arch/arm64/include/asm/ptrace.h,

Important APIs/types/functions:
- Contains 10 constant rows, including `COMPAT_PTRACE_GETREGS		12`
- Representative constants: `COMPAT_PTRACE_GETREGS`, `COMPAT_PTRACE_SETREGS`, `COMPAT_PTRACE_GETFPREGS`, `COMPAT_PTRACE_SETFPREGS`, `COMPAT_PTRACE_GET_THREAD_AREA`, `COMPAT_PTRACE_SET_SYSCALL`, `COMPAT_PTRACE_GETVFPREGS`, `COMPAT_PTRACE_SETVFPREGS`, `COMPAT_PTRACE_GETHBPREGS`, `COMPAT_PTRACE_SETHBPREGS`
- Generator directives/preprocessor guards: `#sorted`, `#From arch/arm64/include/asm/ptrace.h`, `#Prefix COMPAT_PTRACE_`, `#if defined __arm64__ || defined __aarch64__`, `#endif`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/compat_ptrace_cmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/counter_ioctl_component_types.in -->
# sources/test-tools/strace/src/xlat/counter_ioctl_component_types.in

Purpose: Declarative xlat input table `counter_ioctl_component_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `COUNTER_COMPONENT_NONE			0`
- Representative constants: `COUNTER_COMPONENT_NONE`, `COUNTER_COMPONENT_SIGNAL`, `COUNTER_COMPONENT_COUNT`, `COUNTER_COMPONENT_FUNCTION`, `COUNTER_COMPONENT_SYNAPSE_ACTION`, `COUNTER_COMPONENT_EXTENSION`
- Generator directives/preprocessor guards: `#enum`, `#value_indexed`, `#unconditional`, `#From include/uapi/linux/counter.h`, `#Prefix COUNTER_COMPONENT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/counter_ioctl_component_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/counter_ioctl_event_types.in -->
# sources/test-tools/strace/src/xlat/counter_ioctl_event_types.in

Purpose: Declarative xlat input table `counter_ioctl_event_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `COUNTER_EVENT_OVERFLOW			0`
- Representative constants: `COUNTER_EVENT_OVERFLOW`, `COUNTER_EVENT_UNDERFLOW`, `COUNTER_EVENT_OVERFLOW_UNDERFLOW`, `COUNTER_EVENT_THRESHOLD`, `COUNTER_EVENT_INDEX`, `COUNTER_EVENT_CHANGE_OF_STATE`, `COUNTER_EVENT_CAPTURE`, `COUNTER_EVENT_DIRECTION_CHANGE`
- Generator directives/preprocessor guards: `#enum`, `#value_indexed`, `#unconditional`, `#From include/uapi/linux/counter.h`, `#Prefix COUNTER_EVENT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/counter_ioctl_event_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/counter_ioctl_scopes.in -->
# sources/test-tools/strace/src/xlat/counter_ioctl_scopes.in

Purpose: Declarative xlat input table `counter_ioctl_scopes` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `COUNTER_SCOPE_DEVICE	0`
- Representative constants: `COUNTER_SCOPE_DEVICE`, `COUNTER_SCOPE_SIGNAL`, `COUNTER_SCOPE_COUNT`
- Generator directives/preprocessor guards: `#enum`, `#value_indexed`, `#unconditional`, `#From include/uapi/linux/counter.h`, `#Prefix COUNTER_SCOPE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/counter_ioctl_scopes.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cpuclocknames.in -->
# sources/test-tools/strace/src/xlat/cpuclocknames.in

Purpose: Declarative xlat input table `cpuclocknames` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `CPUCLOCK_PROF	0`
- Representative constants: `CPUCLOCK_PROF`, `CPUCLOCK_VIRT`, `CPUCLOCK_SCHED`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/linux/posix-timers_types.h`, `#Prefix CPUCLOCK_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cpuclocknames.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/crypto_nl_attrs.in -->
# sources/test-tools/strace/src/xlat/crypto_nl_attrs.in

Purpose: Declarative xlat input table `crypto_nl_attrs` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 23 constant rows, including `CRYPTOCFGA_UNSPEC`
- Representative constants: `CRYPTOCFGA_UNSPEC`, `CRYPTOCFGA_PRIORITY_VAL`, `CRYPTOCFGA_REPORT_LARVAL`, `CRYPTOCFGA_REPORT_HASH`, `CRYPTOCFGA_REPORT_BLKCIPHER`, `CRYPTOCFGA_REPORT_AEAD`, `CRYPTOCFGA_REPORT_COMPRESS`, `CRYPTOCFGA_REPORT_RNG`, `CRYPTOCFGA_REPORT_CIPHER`, `CRYPTOCFGA_REPORT_AKCIPHER`...
- Generator directives/preprocessor guards: `#Generated by maint/enum2xlat.sh from "enum crypto_attr_type_t" in bundled/linux/include/uapi/linux/cryptouser.h; do not edit.`, `#unconditional`, `#value_indexed`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/crypto_nl_attrs.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dcb_commands.in -->
# sources/test-tools/strace/src/xlat/dcb_commands.in

Purpose: Declarative xlat input table `dcb_commands` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 28 constant rows, including `DCB_CMD_UNDEFINED`
- Representative constants: `DCB_CMD_UNDEFINED`, `DCB_CMD_GSTATE`, `DCB_CMD_SSTATE`, `DCB_CMD_PGTX_GCFG`, `DCB_CMD_PGTX_SCFG`, `DCB_CMD_PGRX_GCFG`, `DCB_CMD_PGRX_SCFG`, `DCB_CMD_PFC_GCFG`, `DCB_CMD_PFC_SCFG`, `DCB_CMD_SET_ALL`...
- Generator directives/preprocessor guards: `#Generated by maint/enum2xlat.sh from "enum dcbnl_commands" in bundled/linux/include/uapi/linux/dcbnl.h; do not edit.`, `#unconditional`, `#value_indexed`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dcb_commands.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/delete_module_flags.in -->
# sources/test-tools/strace/src/xlat/delete_module_flags.in

Purpose: Declarative xlat input table `delete_module_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `O_NONBLOCK`
- Representative constants: `O_NONBLOCK`, `O_TRUNC`
- Generator directives/preprocessor guards: `#From include/uapi/asm-generic/fcntl.h`, `#Prefix O_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/delete_module_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dirent_types.in -->
# sources/test-tools/strace/src/xlat/dirent_types.in

Purpose: Declarative xlat input table `dirent_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `DT_UNKNOWN`
- Representative constants: `DT_UNKNOWN`, `DT_FIFO`, `DT_CHR`, `DT_DIR`, `DT_BLK`, `DT_REG`, `DT_LNK`, `DT_SOCK`, `DT_WHT`
- Generator directives/preprocessor guards: `#From include/linux/fs_types.h`, `#Prefix DT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dirent_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dm_flags.in -->
# sources/test-tools/strace/src/xlat/dm_flags.in

Purpose: Declarative xlat input table `dm_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 19 constant rows, including `DM_READONLY_FLAG`
- Representative constants: `DM_READONLY_FLAG`, `DM_SUSPEND_FLAG`, `DM_EXISTS_FLAG`, `DM_PERSISTENT_DEV_FLAG`, `DM_STATUS_TABLE_FLAG`, `DM_ACTIVE_PRESENT_FLAG`, `DM_INACTIVE_PRESENT_FLAG`, `DM_BUFFER_FULL_FLAG`, `DM_SKIP_BDGET_FLAG`, `DM_SKIP_LOCKFS_FLAG`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/dm-ioctl.h`, `#Prefix DM_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dm_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_class.in -->
# sources/test-tools/strace/src/xlat/ebpf_class.in

Purpose: Declarative xlat input table `ebpf_class` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `BPF_LD		0x0`
- Representative constants: `BPF_LD`, `BPF_LDX`, `BPF_ST`, `BPF_STX`, `BPF_ALU`, `BPF_JMP`, `BPF_JMP32`, `BPF_ALU64`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_class.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_mode.in -->
# sources/test-tools/strace/src/xlat/ebpf_mode.in

Purpose: Declarative xlat input table `ebpf_mode` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `BPF_IMM		0x00`
- Representative constants: `BPF_IMM`, `BPF_ABS`, `BPF_IND`, `BPF_MEM`, `BPF_MEMSX`, `BPF_ATOMIC`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#From include/uapi/linux/bpf_common.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_mode.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_op_alu.in -->
# sources/test-tools/strace/src/xlat/ebpf_op_alu.in

Purpose: Declarative xlat input table `ebpf_op_alu` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `BPF_MOV		0xb0`
- Representative constants: `BPF_MOV`, `BPF_ARSH`, `BPF_END`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_op_alu.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_op_jmp.in -->
# sources/test-tools/strace/src/xlat/ebpf_op_jmp.in

Purpose: Declarative xlat input table `ebpf_op_jmp` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `BPF_JNE		0x50`
- Representative constants: `BPF_JNE`, `BPF_JSGT`, `BPF_JSGE`, `BPF_CALL`, `BPF_EXIT`, `BPF_JLT`, `BPF_JLE`, `BPF_JSLT`, `BPF_JSLE`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_op_jmp.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_regs.in -->
# sources/test-tools/strace/src/xlat/ebpf_regs.in

Purpose: Declarative xlat input table `ebpf_regs` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `BPF_REG_0  0`
- Representative constants: `BPF_REG_0`, `BPF_REG_1`, `BPF_REG_2`, `BPF_REG_3`, `BPF_REG_4`, `BPF_REG_5`, `BPF_REG_6`, `BPF_REG_7`, `BPF_REG_8`, `BPF_REG_9`...
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/bpf.h`, `#Prefix BPF_REG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_regs.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_size.in -->
# sources/test-tools/strace/src/xlat/ebpf_size.in

Purpose: Declarative xlat input table `ebpf_size` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `BPF_DW	0x18`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ebpf_size.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/efd_flags.in -->
# sources/test-tools/strace/src/xlat/efd_flags.in

Purpose: Declarative xlat input table `efd_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `EFD_SEMAPHORE	1`
- Representative constants: `EFD_SEMAPHORE`, `EFD_CLOEXEC`, `EFD_NONBLOCK`
- Generator directives/preprocessor guards: `#From include/uapi/linux/eventfd.h`, `#Prefix EFD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/efd_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/elf_em.in -->
# sources/test-tools/strace/src/xlat/elf_em.in

Purpose: Declarative xlat input table `elf_em` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: See also https://www.sco.com/developers/gabi/latest/ch4.eheader.html EM_IAMCU		6 - Intel MCU

Important APIs/types/functions:
- Contains 188 constant rows, including `EM_NONE			0`
- Representative constants: `EM_NONE`, `EM_M32`, `EM_SPARC`, `EM_386`, `EM_68K`, `EM_88K`, `EM_486`, `EM_860`, `EM_MIPS`, `EM_S370`...
- Generator directives/preprocessor guards: `#sorted`, `#From include/uapi/linux/elf-em.h`, `#Prefix EM_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/elf_em.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/epollctls.in -->
# sources/test-tools/strace/src/xlat/epollctls.in

Purpose: Declarative xlat input table `epollctls` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `EPOLL_CTL_ADD 1`
- Representative constants: `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/eventpoll.h`, `#Prefix EPOLL_CTL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/epollctls.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/epollevents.in -->
# sources/test-tools/strace/src/xlat/epollevents.in

Purpose: Declarative xlat input table `epollevents` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 16 constant rows, including `EPOLLIN		0x00000001`
- Representative constants: `EPOLLIN`, `EPOLLPRI`, `EPOLLOUT`, `EPOLLERR`, `EPOLLHUP`, `EPOLLNVAL`, `EPOLLRDNORM`, `EPOLLRDBAND`, `EPOLLWRNORM`, `EPOLLWRBAND`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/eventpoll.h`, `#Prefix EPOLL`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/epollevents.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/epollflags.in -->
# sources/test-tools/strace/src/xlat/epollflags.in

Purpose: Declarative xlat input table `epollflags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `EPOLL_CLOEXEC	O_CLOEXEC`
- Generator directives/preprocessor guards: `#From include/uapi/linux/eventpoll.h`, `#Prefix EPOLL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/epollflags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ethernet_protocols.in -->
# sources/test-tools/strace/src/xlat/ethernet_protocols.in

Purpose: Declarative xlat input table `ethernet_protocols` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 101 constant rows, including `ETH_P_802_3	0x0001		/* Dummy type for 802.3 frames  */`
- Representative constants: `ETH_P_802_3`, `ETH_P_AX25`, `ETH_P_ALL`, `ETH_P_802_2`, `ETH_P_SNAP`, `ETH_P_DDCMP`, `ETH_P_WAN_PPP`, `ETH_P_PPP_MP`, `ETH_P_LOCALTALK`, `ETH_P_CAN`...
- Generator directives/preprocessor guards: `#sorted sort -k2,2`, `#From include/uapi/linux/if_ether.h`, `#Prefix ETH_P_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ethernet_protocols.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_abs.in -->
# sources/test-tools/strace/src/xlat/evdev_abs.in

Purpose: Declarative xlat input table `evdev_abs` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 44 constant rows, including `ABS_X`
- Representative constants: `ABS_X`, `ABS_Y`, `ABS_Z`, `ABS_RX`, `ABS_RY`, `ABS_RZ`, `ABS_THROTTLE`, `ABS_RUDDER`, `ABS_WHEEL`, `ABS_GAS`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix ABS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_abs.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_autorepeat.in -->
# sources/test-tools/strace/src/xlat/evdev_autorepeat.in

Purpose: Declarative xlat input table `evdev_autorepeat` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `REP_DELAY`
- Representative constants: `REP_DELAY`, `REP_PERIOD`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix REP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_autorepeat.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_ev.in -->
# sources/test-tools/strace/src/xlat/evdev_ev.in

Purpose: Declarative xlat input table `evdev_ev` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 12 constant rows, including `EV_SYN`
- Representative constants: `EV_SYN`, `EV_KEY`, `EV_REL`, `EV_ABS`, `EV_MSC`, `EV_SW`, `EV_LED`, `EV_SND`, `EV_REP`, `EV_FF`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix EV_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_ev.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_ff_status.in -->
# sources/test-tools/strace/src/xlat/evdev_ff_status.in

Purpose: Declarative xlat input table `evdev_ff_status` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `FF_STATUS_STOPPED`
- Representative constants: `FF_STATUS_STOPPED`, `FF_STATUS_PLAYING`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input.h`, `#Prefix FF_STATUS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_ff_status.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_ff_types.in -->
# sources/test-tools/strace/src/xlat/evdev_ff_types.in

Purpose: Declarative xlat input table `evdev_ff_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 17 constant rows, including `FF_HAPTIC`
- Representative constants: `FF_HAPTIC`, `FF_RUMBLE`, `FF_PERIODIC`, `FF_CONSTANT`, `FF_SPRING`, `FF_FRICTION`, `FF_DAMPER`, `FF_INERTIA`, `FF_RAMP`, `FF_SQUARE`...
- Generator directives/preprocessor guards: `#unconditional`, `#sorted sort -k2,2`, `#From include/uapi/linux/input.h`, `#Prefix FF_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_ff_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_keycode.in -->
# sources/test-tools/strace/src/xlat/evdev_keycode.in

Purpose: Declarative xlat input table `evdev_keycode` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: awk '{if (NF>1) {n=strtonum($2)}; printf("%d %s\n", n, $0)}' |sort -s -k1,1n |sed 's/^[0-9]* //'

Important APIs/types/functions:
- Contains 627 constant rows, including `KEY_RESERVED`
- Representative constants: `KEY_RESERVED`, `KEY_ESC`, `KEY_1`, `KEY_2`, `KEY_3`, `KEY_4`, `KEY_5`, `KEY_6`, `KEY_7`, `KEY_8`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix BTN_ KEY_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_keycode.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_leds.in -->
# sources/test-tools/strace/src/xlat/evdev_leds.in

Purpose: Declarative xlat input table `evdev_leds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `LED_NUML`
- Representative constants: `LED_NUML`, `LED_CAPSL`, `LED_SCROLLL`, `LED_COMPOSE`, `LED_KANA`, `LED_SLEEP`, `LED_SUSPEND`, `LED_MUTE`, `LED_MISC`, `LED_MAIL`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix LED_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_leds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_misc.in -->
# sources/test-tools/strace/src/xlat/evdev_misc.in

Purpose: Declarative xlat input table `evdev_misc` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `MSC_SERIAL`
- Representative constants: `MSC_SERIAL`, `MSC_PULSELED`, `MSC_GESTURE`, `MSC_RAW`, `MSC_SCAN`, `MSC_TIMESTAMP`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix MSC_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_misc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_mtslots.in -->
# sources/test-tools/strace/src/xlat/evdev_mtslots.in

Purpose: Declarative xlat input table `evdev_mtslots` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 15 constant rows, including `ABS_MT_SLOT`
- Representative constants: `ABS_MT_SLOT`, `ABS_MT_TOUCH_MAJOR`, `ABS_MT_TOUCH_MINOR`, `ABS_MT_WIDTH_MAJOR`, `ABS_MT_WIDTH_MINOR`, `ABS_MT_ORIENTATION`, `ABS_MT_POSITION_X`, `ABS_MT_POSITION_Y`, `ABS_MT_TOOL_TYPE`, `ABS_MT_BLOB_ID`...
- Generator directives/preprocessor guards: `#unconditional`, `#sorted`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix ABS_MT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_mtslots.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_prop.in -->
# sources/test-tools/strace/src/xlat/evdev_prop.in

Purpose: Declarative xlat input table `evdev_prop` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `INPUT_PROP_POINTER`
- Representative constants: `INPUT_PROP_POINTER`, `INPUT_PROP_DIRECT`, `INPUT_PROP_BUTTONPAD`, `INPUT_PROP_SEMI_MT`, `INPUT_PROP_TOPBUTTONPAD`, `INPUT_PROP_POINTING_STICK`, `INPUT_PROP_ACCELEROMETER`, `INPUT_PROP_PRESSUREPAD`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix INPUT_PROP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_prop.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_relative_axes.in -->
# sources/test-tools/strace/src/xlat/evdev_relative_axes.in

Purpose: Declarative xlat input table `evdev_relative_axes` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 13 constant rows, including `REL_X`
- Representative constants: `REL_X`, `REL_Y`, `REL_Z`, `REL_RX`, `REL_RY`, `REL_RZ`, `REL_HWHEEL`, `REL_DIAL`, `REL_WHEEL`, `REL_MISC`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix REL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_relative_axes.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_snd.in -->
# sources/test-tools/strace/src/xlat/evdev_snd.in

Purpose: Declarative xlat input table `evdev_snd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `SND_CLICK`
- Representative constants: `SND_CLICK`, `SND_BELL`, `SND_TONE`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix SND_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_snd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_switch.in -->
# sources/test-tools/strace/src/xlat/evdev_switch.in

Purpose: Declarative xlat input table `evdev_switch` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 18 constant rows, including `SW_LID`
- Representative constants: `SW_LID`, `SW_TABLET_MODE`, `SW_HEADPHONE_INSERT`, `SW_RFKILL_ALL`, `SW_MICROPHONE_INSERT`, `SW_DOCK`, `SW_LINEOUT_INSERT`, `SW_JACK_PHYSICAL_INSERT`, `SW_VIDEOOUT_INSERT`, `SW_CAMERA_LENS_COVER`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix SW_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_switch.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/execveat_flags.in -->
# sources/test-tools/strace/src/xlat/execveat_flags.in

Purpose: Declarative xlat input table `execveat_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `AT_SYMLINK_NOFOLLOW`
- Representative constants: `AT_SYMLINK_NOFOLLOW`, `AT_EMPTY_PATH`, `AT_EXECVE_CHECK`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fcntl.h`, `#Prefix AT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/execveat_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/f_owner_types.in -->
# sources/test-tools/strace/src/xlat/f_owner_types.in

Purpose: Declarative xlat input table `f_owner_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `F_OWNER_TID`
- Representative constants: `F_OWNER_TID`, `F_OWNER_PID`, `F_OWNER_PGRP`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/asm-generic/fcntl.h`, `#Prefix F_OWNER_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/f_owner_types.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/f_seals.in -->
# sources/test-tools/strace/src/xlat/f_seals.in

Purpose: Declarative xlat input table `f_seals` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `F_SEAL_SEAL`
- Representative constants: `F_SEAL_SEAL`, `F_SEAL_SHRINK`, `F_SEAL_GROW`, `F_SEAL_WRITE`, `F_SEAL_FUTURE_WRITE`, `F_SEAL_EXEC`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fcntl.h`, `#Prefix F_SEAL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/f_seals.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/faccessat_flags.in -->
# sources/test-tools/strace/src/xlat/faccessat_flags.in

Purpose: Declarative xlat input table `faccessat_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `AT_SYMLINK_NOFOLLOW	0x100`
- Representative constants: `AT_SYMLINK_NOFOLLOW`, `AT_EACCESS`, `AT_EMPTY_PATH`
- Generator directives/preprocessor guards: `#From include/uapi/linux/fcntl.h`, `#Prefix AT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/faccessat_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/falloc_flags.in -->
# sources/test-tools/strace/src/xlat/falloc_flags.in

Purpose: Declarative xlat input table `falloc_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `FALLOC_FL_KEEP_SIZE`
- Representative constants: `FALLOC_FL_KEEP_SIZE`, `FALLOC_FL_PUNCH_HOLE`, `FALLOC_FL_NO_HIDE_STALE`, `FALLOC_FL_COLLAPSE_RANGE`, `FALLOC_FL_ZERO_RANGE`, `FALLOC_FL_INSERT_RANGE`, `FALLOC_FL_UNSHARE_RANGE`, `FALLOC_FL_WRITE_ZEROES`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/falloc.h`, `#Prefix FALLOC_FL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/falloc_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_classes.in -->
# sources/test-tools/strace/src/xlat/fan_classes.in

Purpose: Declarative xlat input table `fan_classes` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `FAN_CLASS_NOTIF 0x00000000`
- Representative constants: `FAN_CLASS_NOTIF`, `FAN_CLASS_CONTENT`, `FAN_CLASS_PRE_CONTENT`
- Generator directives/preprocessor guards: `#From include/uapi/linux/fanotify.h`, `#Prefix FAN_CLASS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_classes.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_event_flags.in -->
# sources/test-tools/strace/src/xlat/fan_event_flags.in

Purpose: Declarative xlat input table `fan_event_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 25 constant rows, including `FAN_ACCESS		0x00000001`
- Representative constants: `FAN_ACCESS`, `FAN_MODIFY`, `FAN_ATTRIB`, `FAN_CLOSE_WRITE`, `FAN_CLOSE_NOWRITE`, `FAN_OPEN`, `FAN_MOVED_FROM`, `FAN_MOVED_TO`, `FAN_CREATE`, `FAN_DELETE`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/fanotify.h`, `#Prefix FAN_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_event_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_init_flags.in -->
# sources/test-tools/strace/src/xlat/fan_init_flags.in

Purpose: Declarative xlat input table `fan_init_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 13 constant rows, including `FAN_CLOEXEC		0x00000001`
- Representative constants: `FAN_CLOEXEC`, `FAN_NONBLOCK`, `FAN_UNLIMITED_QUEUE`, `FAN_UNLIMITED_MARKS`, `FAN_ENABLE_AUDIT`, `FAN_REPORT_PIDFD`, `FAN_REPORT_TID`, `FAN_REPORT_FID`, `FAN_REPORT_DIR_FID`, `FAN_REPORT_NAME`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/fanotify.h`, `#Prefix FAN_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_init_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_mark_flags.in -->
# sources/test-tools/strace/src/xlat/fan_mark_flags.in

Purpose: Declarative xlat input table `fan_mark_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 12 constant rows, including `FAN_MARK_ADD			0x00000001`
- Representative constants: `FAN_MARK_ADD`, `FAN_MARK_REMOVE`, `FAN_MARK_FLUSH`, `FAN_MARK_DONT_FOLLOW`, `FAN_MARK_ONLYDIR`, `FAN_MARK_MNTNS`, `FAN_MARK_MOUNT`, `FAN_MARK_FILESYSTEM`, `FAN_MARK_IGNORED_MASK`, `FAN_MARK_IGNORED_SURV_MODIFY`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/fanotify.h`, `#Prefix FAN_MARK_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fan_mark_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fchmodat_flags.in -->
# sources/test-tools/strace/src/xlat/fchmodat_flags.in

Purpose: Declarative xlat input table `fchmodat_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `AT_SYMLINK_NOFOLLOW`
- Representative constants: `AT_SYMLINK_NOFOLLOW`, `AT_EMPTY_PATH`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fcntl.h`, `#Prefix AT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fchmodat_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fcntlcmds.in -->
# sources/test-tools/strace/src/xlat/fcntlcmds.in

Purpose: Declarative xlat input table `fcntlcmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 38 constant rows, including `F_DUPFD`
- Representative constants: `F_DUPFD`, `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, `F_GETLK`, `F_SETLK`, `F_SETLKW`, `F_SETOWN`, `F_GETOWN`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/asm-generic/fcntl.h`, `#From include/uapi/linux/fcntl.h`, `#Prefix F_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fcntlcmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fdb_notify_flags.in -->
# sources/test-tools/strace/src/xlat/fdb_notify_flags.in

Purpose: Declarative xlat input table `fdb_notify_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `FDB_NOTIFY_BIT		(1 << 0)`
- Representative constants: `FDB_NOTIFY_BIT`, `FDB_NOTIFY_INACTIVE_BIT`
- Generator directives/preprocessor guards: `#From include/uapi/linux/neighbour.h`, `#Pattern FDB_NOTIFY_.*BIT`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fdb_notify_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fdflags.in -->
# sources/test-tools/strace/src/xlat/fdflags.in

Purpose: Declarative xlat input table `fdflags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `FD_CLOEXEC`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/asm-generic/fcntl.h`, `#Prefix FD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fdflags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fib_rule_actions.in -->
# sources/test-tools/strace/src/xlat/fib_rule_actions.in

Purpose: Declarative xlat input table `fib_rule_actions` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `FR_ACT_UNSPEC`
- Representative constants: `FR_ACT_UNSPEC`, `FR_ACT_TO_TBL`, `FR_ACT_GOTO`, `FR_ACT_NOP`, `FR_ACT_RES3`, `FR_ACT_RES4`, `FR_ACT_BLACKHOLE`, `FR_ACT_UNREACHABLE`, `FR_ACT_PROHIBIT`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/fib_rules.h`, `#Prefix FR_ACT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fib_rule_actions.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fib_rule_flags.in -->
# sources/test-tools/strace/src/xlat/fib_rule_flags.in

Purpose: Declarative xlat input table `fib_rule_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `FIB_RULE_PERMANENT`
- Representative constants: `FIB_RULE_PERMANENT`, `FIB_RULE_INVERT`, `FIB_RULE_UNRESOLVED`, `FIB_RULE_IIF_DETACHED`, `FIB_RULE_OIF_DETACHED`, `FIB_RULE_FIND_SADDR`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fib_rules.h`, `#Prefix FIB_RULE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fib_rule_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fiemap_extent_flags.in -->
# sources/test-tools/strace/src/xlat/fiemap_extent_flags.in

Purpose: Declarative xlat input table `fiemap_extent_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `FIEMAP_EXTENT_LAST`
- Representative constants: `FIEMAP_EXTENT_LAST`, `FIEMAP_EXTENT_UNKNOWN`, `FIEMAP_EXTENT_DELALLOC`, `FIEMAP_EXTENT_ENCODED`, `FIEMAP_EXTENT_DATA_ENCRYPTED`, `FIEMAP_EXTENT_NOT_ALIGNED`, `FIEMAP_EXTENT_DATA_INLINE`, `FIEMAP_EXTENT_DATA_TAIL`, `FIEMAP_EXTENT_UNWRITTEN`, `FIEMAP_EXTENT_MERGED`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fiemap.h`, `#Prefix FIEMAP_EXTENT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fiemap_extent_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fiemap_flags.in -->
# sources/test-tools/strace/src/xlat/fiemap_flags.in

Purpose: Declarative xlat input table `fiemap_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `FIEMAP_FLAG_SYNC`
- Representative constants: `FIEMAP_FLAG_SYNC`, `FIEMAP_FLAG_XATTR`, `FIEMAP_FLAG_CACHE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fiemap.h`, `#Prefix FIEMAP_FLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fiemap_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/file_attr_flags.in -->
# sources/test-tools/strace/src/xlat/file_attr_flags.in

Purpose: Declarative xlat input table `file_attr_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `AT_SYMLINK_NOFOLLOW`
- Representative constants: `AT_SYMLINK_NOFOLLOW`, `AT_EMPTY_PATH`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fcntl.h`, `#Prefix AT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/file_attr_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/flockcmds.in -->
# sources/test-tools/strace/src/xlat/flockcmds.in

Purpose: Declarative xlat input table `flockcmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `LOCK_SH		1`
- Representative constants: `LOCK_SH`, `LOCK_EX`, `LOCK_NB`, `LOCK_UN`, `LOCK_MAND`, `LOCK_RW`, `LOCK_READ`, `LOCK_WRITE`
- Generator directives/preprocessor guards: `#From include/uapi/asm-generic/fcntl.h`, `#Prefix LOCK_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/flockcmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fs_ioc_flags.in -->
# sources/test-tools/strace/src/xlat/fs_ioc_flags.in

Purpose: Declarative xlat input table `fs_ioc_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 29 constant rows, including `FS_SECRM_FL`
- Representative constants: `FS_SECRM_FL`, `FS_UNRM_FL`, `FS_COMPR_FL`, `FS_SYNC_FL`, `FS_IMMUTABLE_FL`, `FS_APPEND_FL`, `FS_NODUMP_FL`, `FS_NOATIME_FL`, `FS_DIRTY_FL`, `FS_COMPRBLK_FL`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fs.h`, `#Pattern FS_.*_FL`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fs_ioc_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fs_shutdown_flags.in -->
# sources/test-tools/strace/src/xlat/fs_shutdown_flags.in

Purpose: Declarative xlat input table `fs_shutdown_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `FS_SHUTDOWN_FLAGS_DEFAULT`
- Representative constants: `FS_SHUTDOWN_FLAGS_DEFAULT`, `FS_SHUTDOWN_FLAGS_LOGFLUSH`, `FS_SHUTDOWN_FLAGS_NOLOGFLUSH`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/fs.h`, `#Prefix FS_SHUTDOWN_FLAGS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fs_shutdown_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fs_xflags.in -->
# sources/test-tools/strace/src/xlat/fs_xflags.in

Purpose: Declarative xlat input table `fs_xflags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 18 constant rows, including `FS_XFLAG_REALTIME`
- Representative constants: `FS_XFLAG_REALTIME`, `FS_XFLAG_PREALLOC`, `FS_XFLAG_IMMUTABLE`, `FS_XFLAG_APPEND`, `FS_XFLAG_SYNC`, `FS_XFLAG_NOATIME`, `FS_XFLAG_NODUMP`, `FS_XFLAG_RTINHERIT`, `FS_XFLAG_PROJINHERIT`, `FS_XFLAG_NOSYMLINKS`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/fs.h`, `#Prefix FS_XFLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fs_xflags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsconfig_cmds.in -->
# sources/test-tools/strace/src/xlat/fsconfig_cmds.in

Purpose: Declarative xlat input table `fsconfig_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `FSCONFIG_SET_FLAG`
- Representative constants: `FSCONFIG_SET_FLAG`, `FSCONFIG_SET_STRING`, `FSCONFIG_SET_BINARY`, `FSCONFIG_SET_PATH`, `FSCONFIG_SET_PATH_EMPTY`, `FSCONFIG_SET_FD`, `FSCONFIG_CMD_CREATE`, `FSCONFIG_CMD_RECONFIGURE`, `FSCONFIG_CMD_CREATE_EXCL`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/mount.h`, `#Prefix FSCONFIG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsconfig_cmds.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmagic.in -->
# sources/test-tools/strace/src/xlat/fsmagic.in

Purpose: Declarative xlat input table `fsmagic` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 117 constant rows, including `QNX4_SUPER_MAGIC	0x0000002f`
- Representative constants: `QNX4_SUPER_MAGIC`, `Z3FOLD_MAGIC`, `AUTOFS_SUPER_MAGIC`, `DEVFS_SUPER_MAGIC`, `EXT_SUPER_MAGIC`, `MINIX_SUPER_MAGIC`, `MINIX_SUPER_MAGIC2`, `DEVPTS_SUPER_MAGIC`, `MINIX2_SUPER_MAGIC`, `MINIX2_SUPER_MAGIC2`...
- Generator directives/preprocessor guards: `#sorted sort -k2,2`, `#From fs/befs/befs_fs_types.h`, `#From fs/freevxfs/vxfs.h`, `#From fs/hfs/hfs.h`, `#From fs/hfsplus/hfsplus_raw.h`, `#From fs/jfs/jfs_incore.h`, `#From fs/ubifs/ubifs.h`, `#From fs/ufs/ufs_fs.h`...

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmagic.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmount_attr_flags.in -->
# sources/test-tools/strace/src/xlat/fsmount_attr_flags.in

Purpose: Declarative xlat input table `fsmount_attr_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: _ATIME == RELATIME | NOATIME | STRICTATIME | 0x40 MOUNT_ATTR_RELATIME == 0

Important APIs/types/functions:
- Contains 9 constant rows, including `MOUNT_ATTR_RDONLY`
- Representative constants: `MOUNT_ATTR_RDONLY`, `MOUNT_ATTR_NOSUID`, `MOUNT_ATTR_NODEV`, `MOUNT_ATTR_NOEXEC`, `MOUNT_ATTR__ATIME`, `MOUNT_ATTR_NOATIME`, `MOUNT_ATTR_STRICTATIME`, `MOUNT_ATTR_NODIRATIME`, `MOUNT_ATTR_NOSYMFOLLOW`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/mount.h`, `#Prefix MOUNT_ATTR_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmount_attr_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmount_flags.in -->
# sources/test-tools/strace/src/xlat/fsmount_flags.in

Purpose: Declarative xlat input table `fsmount_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `FSMOUNT_CLOEXEC`
- Representative constants: `FSMOUNT_CLOEXEC`, `FSMOUNT_NAMESPACE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/mount.h`, `#Prefix FSMOUNT_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmount_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsopen_flags.in -->
# sources/test-tools/strace/src/xlat/fsopen_flags.in

Purpose: Declarative xlat input table `fsopen_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `FSOPEN_CLOEXEC`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/mount.h`, `#Prefix FSOPEN_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsopen_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fspick_flags.in -->
# sources/test-tools/strace/src/xlat/fspick_flags.in

Purpose: Declarative xlat input table `fspick_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `FSPICK_CLOEXEC`
- Representative constants: `FSPICK_CLOEXEC`, `FSPICK_SYMLINK_NOFOLLOW`, `FSPICK_NO_AUTOMOUNT`, `FSPICK_EMPTY_PATH`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/mount.h`, `#Prefix FSPICK_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fspick_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futex2_flags.in -->
# sources/test-tools/strace/src/xlat/futex2_flags.in

Purpose: Declarative xlat input table `futex2_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `FUTEX2_NUMA		0x04`
- Representative constants: `FUTEX2_NUMA`, `FUTEX2_MPOL`, `FUTEX2_PRIVATE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/futex.h`, `#Prefix FUTEX2_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futex2_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futex2_sizes.in -->
# sources/test-tools/strace/src/xlat/futex2_sizes.in

Purpose: Declarative xlat input table `futex2_sizes` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 4 constant rows, including `FUTEX2_SIZE_U8		0`
- Representative constants: `FUTEX2_SIZE_U8`, `FUTEX2_SIZE_U16`, `FUTEX2_SIZE_U32`, `FUTEX2_SIZE_U64`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/futex.h`, `#Prefix FUTEX2_SIZE_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futex2_sizes.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexbitset.in -->
# sources/test-tools/strace/src/xlat/futexbitset.in

Purpose: Declarative xlat input table `futexbitset` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 1 constant rows, including `FUTEX_BITSET_MATCH_ANY	0xffffffff`
- Generator directives/preprocessor guards: `#From include/uapi/linux/futex.h`, `#Prefix FUTEX_BITSET_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexbitset.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexops.in -->
# sources/test-tools/strace/src/xlat/futexops.in

Purpose: Declarative xlat input table `futexops` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 34 constant rows, including `FUTEX_WAIT	0`
- Representative constants: `FUTEX_WAIT`, `FUTEX_WAKE`, `FUTEX_FD`, `FUTEX_REQUEUE`, `FUTEX_CMP_REQUEUE`, `FUTEX_WAKE_OP`, `FUTEX_LOCK_PI`, `FUTEX_UNLOCK_PI`, `FUTEX_TRYLOCK_PI`, `FUTEX_WAIT_BITSET`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/futex.h`, `#Prefix FUTEX_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexops.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexwakecmps.in -->
# sources/test-tools/strace/src/xlat/futexwakecmps.in

Purpose: Declarative xlat input table `futexwakecmps` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `FUTEX_OP_CMP_EQ	0`
- Representative constants: `FUTEX_OP_CMP_EQ`, `FUTEX_OP_CMP_NE`, `FUTEX_OP_CMP_LT`, `FUTEX_OP_CMP_LE`, `FUTEX_OP_CMP_GT`, `FUTEX_OP_CMP_GE`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/futex.h`, `#Prefix FUTEX_OP_CMP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexwakecmps.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexwakeops.in -->
# sources/test-tools/strace/src/xlat/futexwakeops.in

Purpose: Declarative xlat input table `futexwakeops` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 5 constant rows, including `FUTEX_OP_SET	0`
- Representative constants: `FUTEX_OP_SET`, `FUTEX_OP_ADD`, `FUTEX_OP_OR`, `FUTEX_OP_ANDN`, `FUTEX_OP_XOR`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/futex.h`, `#Prefix FUTEX_OP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/futexwakeops.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gen.sh -->
# sources/test-tools/strace/src/xlat/gen.sh

Purpose: Generator script for xlat input files; converts `.in` declarations into C header tables, optional m4 enum records, conditional macro definitions, and validation assertions.

Important APIs/types/functions:
- Shell functions: `usage`, `print_m4_record`, `cond_def`, `check_sort_order`, `print_xlat`, `print_xlat_pair`, `cond_xlat`, `gen_header`, `gen_make`, `gen_git`, `gen_m4_entry`, `main`
- Inputs are an xlat file or directory and an output directory; outputs generated headers and optional `.m4` records.

Control flow:
- parses command-line input/output, reads directives such as `#sorted`, `#value_indexed`, `#unconditional`, `#enum`, `#val_type`, and emits guarded `XLAT`/`XLAT_PAIR` rows
- checks sorted ordering with generated static assertions and emits fallback defines for constants with explicit numeric values

State and persistence behavior:
- uses shell-local counters/flags while processing each file; writes generated files under the requested output tree
- persistent artifacts are generated headers consumed by the build, not runtime state

Dependencies and integration points:
- requires POSIX shell utilities and the strace xlat input conventions
- integrates with generated `xlat/*.h`, `xlat.h`, build rules, and decoders using `printxval`/`printflags`

Risks:
- parser changes can affect every generated xlat table; directive handling must remain backward-compatible
- bad quoting or malformed `.in` rows can generate uncompilable headers or silently wrong fallback constants

Test signals:
- test signals include regenerating all xlat headers, compiling generated static assertions, and diffing generated output for deterministic changes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr.in -->
# sources/test-tools/strace/src/xlat/genl_ctrl_attr.in

Purpose: Declarative xlat input table `genl_ctrl_attr` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `CTRL_ATTR_UNSPEC`
- Representative constants: `CTRL_ATTR_UNSPEC`, `CTRL_ATTR_FAMILY_ID`, `CTRL_ATTR_FAMILY_NAME`, `CTRL_ATTR_VERSION`, `CTRL_ATTR_HDRSIZE`, `CTRL_ATTR_MAXATTR`, `CTRL_ATTR_OPS`, `CTRL_ATTR_MCAST_GROUPS`, `CTRL_ATTR_POLICY`, `CTRL_ATTR_OP_POLICY`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/genetlink.h`, `#Prefix CTRL_ATTR_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_mcast_grp.in -->
# sources/test-tools/strace/src/xlat/genl_ctrl_attr_mcast_grp.in

Purpose: Declarative xlat input table `genl_ctrl_attr_mcast_grp` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `CTRL_ATTR_MCAST_GRP_UNSPEC`
- Representative constants: `CTRL_ATTR_MCAST_GRP_UNSPEC`, `CTRL_ATTR_MCAST_GRP_NAME`, `CTRL_ATTR_MCAST_GRP_ID`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/genetlink.h`, `#Prefix CTRL_ATTR_MCAST_GRP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_mcast_grp.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_op.in -->
# sources/test-tools/strace/src/xlat/genl_ctrl_attr_op.in

Purpose: Declarative xlat input table `genl_ctrl_attr_op` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `CTRL_ATTR_OP_UNSPEC`
- Representative constants: `CTRL_ATTR_OP_UNSPEC`, `CTRL_ATTR_OP_ID`, `CTRL_ATTR_OP_FLAGS`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/genetlink.h`, `#Prefix CTRL_ATTR_OP_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_op.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_op_flags.in -->
# sources/test-tools/strace/src/xlat/genl_ctrl_attr_op_flags.in

Purpose: Declarative xlat input table `genl_ctrl_attr_op_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 5 constant rows, including `GENL_ADMIN_PERM`
- Representative constants: `GENL_ADMIN_PERM`, `GENL_CMD_CAP_DO`, `GENL_CMD_CAP_DUMP`, `GENL_CMD_CAP_HASPOL`, `GENL_UNS_ADMIN_PERM`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/genetlink.h`, `#Prefix GENL_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_op_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_policy.in -->
# sources/test-tools/strace/src/xlat/genl_ctrl_attr_policy.in

Purpose: Declarative xlat input table `genl_ctrl_attr_policy` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `CTRL_ATTR_POLICY_UNSPEC`
- Representative constants: `CTRL_ATTR_POLICY_UNSPEC`, `CTRL_ATTR_POLICY_DO`, `CTRL_ATTR_POLICY_DUMP`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/genetlink.h`, `#Prefix CTRL_ATTR_POLICY_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_attr_policy.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_ctrl_cmd.in

Purpose: Declarative xlat input table `genl_ctrl_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `CTRL_CMD_UNSPEC`
- Representative constants: `CTRL_CMD_UNSPEC`, `CTRL_CMD_NEWFAMILY`, `CTRL_CMD_DELFAMILY`, `CTRL_CMD_GETFAMILY`, `CTRL_CMD_NEWOPS`, `CTRL_CMD_DELOPS`, `CTRL_CMD_GETOPS`, `CTRL_CMD_NEWMCAST_GRP`, `CTRL_CMD_DELMCAST_GRP`, `CTRL_CMD_GETMCAST_GRP`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/genetlink.h`, `#Prefix CTRL_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ctrl_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_devlink_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_devlink_cmd.in

Purpose: Declarative xlat input table `genl_devlink_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 85 constant rows, including `DEVLINK_CMD_UNSPEC`
- Representative constants: `DEVLINK_CMD_UNSPEC`, `DEVLINK_CMD_GET`, `DEVLINK_CMD_SET`, `DEVLINK_CMD_NEW`, `DEVLINK_CMD_DEL`, `DEVLINK_CMD_PORT_GET`, `DEVLINK_CMD_PORT_SET`, `DEVLINK_CMD_PORT_NEW`, `DEVLINK_CMD_PORT_DEL`, `DEVLINK_CMD_PORT_SPLIT`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/devlink.h`, `#Prefix DEVLINK_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_devlink_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ethtool_msg_recv.in -->
# sources/test-tools/strace/src/xlat/genl_ethtool_msg_recv.in

Purpose: Declarative xlat input table `genl_ethtool_msg_recv` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 55 constant rows, including `ETHTOOL_MSG_KERNEL_NONE`
- Representative constants: `ETHTOOL_MSG_KERNEL_NONE`, `ETHTOOL_MSG_STRSET_GET_REPLY`, `ETHTOOL_MSG_LINKINFO_GET_REPLY`, `ETHTOOL_MSG_LINKINFO_NTF`, `ETHTOOL_MSG_LINKMODES_GET_REPLY`, `ETHTOOL_MSG_LINKMODES_NTF`, `ETHTOOL_MSG_LINKSTATE_GET_REPLY`, `ETHTOOL_MSG_DEBUG_GET_REPLY`, `ETHTOOL_MSG_DEBUG_NTF`, `ETHTOOL_MSG_WOL_GET_REPLY`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/ethtool_netlink_generated.h`, `#Prefix ETHTOOL_MSG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ethtool_msg_recv.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ethtool_msg_send.in -->
# sources/test-tools/strace/src/xlat/genl_ethtool_msg_send.in

Purpose: Declarative xlat input table `genl_ethtool_msg_send` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 52 constant rows, including `ETHTOOL_MSG_USER_NONE`
- Representative constants: `ETHTOOL_MSG_USER_NONE`, `ETHTOOL_MSG_STRSET_GET`, `ETHTOOL_MSG_LINKINFO_GET`, `ETHTOOL_MSG_LINKINFO_SET`, `ETHTOOL_MSG_LINKMODES_GET`, `ETHTOOL_MSG_LINKMODES_SET`, `ETHTOOL_MSG_LINKSTATE_GET`, `ETHTOOL_MSG_DEBUG_GET`, `ETHTOOL_MSG_DEBUG_SET`, `ETHTOOL_MSG_WOL_GET`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/ethtool_netlink_generated.h`, `#Prefix ETHTOOL_MSG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ethtool_msg_send.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ioam6_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_ioam6_cmd.in

Purpose: Declarative xlat input table `genl_ioam6_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `IOAM6_CMD_UNSPEC`
- Representative constants: `IOAM6_CMD_UNSPEC`, `IOAM6_CMD_ADD_NAMESPACE`, `IOAM6_CMD_DEL_NAMESPACE`, `IOAM6_CMD_DUMP_NAMESPACES`, `IOAM6_CMD_ADD_SCHEMA`, `IOAM6_CMD_DEL_SCHEMA`, `IOAM6_CMD_DUMP_SCHEMAS`, `IOAM6_CMD_NS_SET_SCHEMA`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/ioam6_genl.h`, `#Prefix IOAM6_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ioam6_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_mptcp_pm_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_mptcp_pm_cmd.in

Purpose: Declarative xlat input table `genl_mptcp_pm_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 12 constant rows, including `MPTCP_PM_CMD_UNSPEC`
- Representative constants: `MPTCP_PM_CMD_UNSPEC`, `MPTCP_PM_CMD_ADD_ADDR`, `MPTCP_PM_CMD_DEL_ADDR`, `MPTCP_PM_CMD_GET_ADDR`, `MPTCP_PM_CMD_FLUSH_ADDRS`, `MPTCP_PM_CMD_SET_LIMITS`, `MPTCP_PM_CMD_GET_LIMITS`, `MPTCP_PM_CMD_SET_FLAGS`, `MPTCP_PM_CMD_ANNOUNCE`, `MPTCP_PM_CMD_REMOVE`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/mptcp_pm.h`, `#Prefix MPTCP_PM_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_mptcp_pm_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_netdev_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_netdev_cmd.in

Purpose: Declarative xlat input table `genl_netdev_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 16 constant rows, including `NETDEV_CMD_DEV_GET`
- Representative constants: `NETDEV_CMD_DEV_GET`, `NETDEV_CMD_DEV_ADD_NTF`, `NETDEV_CMD_DEV_DEL_NTF`, `NETDEV_CMD_DEV_CHANGE_NTF`, `NETDEV_CMD_PAGE_POOL_GET`, `NETDEV_CMD_PAGE_POOL_ADD_NTF`, `NETDEV_CMD_PAGE_POOL_DEL_NTF`, `NETDEV_CMD_PAGE_POOL_CHANGE_NTF`, `NETDEV_CMD_PAGE_POOL_STATS_GET`, `NETDEV_CMD_QUEUE_GET`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/netdev.h`, `#Prefix NETDEV_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_netdev_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_nl80211_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_nl80211_cmd.in

Purpose: Declarative xlat input table `genl_nl80211_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 166 constant rows, including `NL80211_CMD_UNSPEC`
- Representative constants: `NL80211_CMD_UNSPEC`, `NL80211_CMD_GET_WIPHY`, `NL80211_CMD_SET_WIPHY`, `NL80211_CMD_NEW_WIPHY`, `NL80211_CMD_DEL_WIPHY`, `NL80211_CMD_GET_INTERFACE`, `NL80211_CMD_SET_INTERFACE`, `NL80211_CMD_NEW_INTERFACE`, `NL80211_CMD_DEL_INTERFACE`, `NL80211_CMD_GET_KEY`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/nl80211.h`, `#Prefix NL80211_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_nl80211_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_seg6_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_seg6_cmd.in

Purpose: Declarative xlat input table `genl_seg6_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 5 constant rows, including `SEG6_CMD_UNSPEC`
- Representative constants: `SEG6_CMD_UNSPEC`, `SEG6_CMD_SETHMAC`, `SEG6_CMD_DUMPHMAC`, `SEG6_CMD_SET_TUNSRC`, `SEG6_CMD_GET_TUNSRC`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/seg6_genl.h`, `#Prefix SEG6_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_seg6_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_taskstats_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_taskstats_cmd.in

Purpose: Declarative xlat input table `genl_taskstats_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `TASKSTATS_CMD_UNSPEC`
- Representative constants: `TASKSTATS_CMD_UNSPEC`, `TASKSTATS_CMD_GET`, `TASKSTATS_CMD_NEW`, `CGROUPSTATS_CMD_UNSPEC`, `CGROUPSTATS_CMD_GET`, `CGROUPSTATS_CMD_NEW`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/cgroupstats.h`, `#From include/uapi/linux/taskstats.h`, `#Prefix TASKSTATS_CMD_ CGROUPSTATS_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_taskstats_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_tcp_metrics_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_tcp_metrics_cmd.in

Purpose: Declarative xlat input table `genl_tcp_metrics_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `TCP_METRICS_CMD_UNSPEC`
- Representative constants: `TCP_METRICS_CMD_UNSPEC`, `TCP_METRICS_CMD_GET`, `TCP_METRICS_CMD_DEL`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/tcp_metrics.h`, `#Prefix TCP_METRICS_CMD_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_tcp_metrics_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_thermal_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_thermal_cmd.in

Purpose: Declarative xlat input table `genl_thermal_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `THERMAL_GENL_CMD_UNSPEC`
- Representative constants: `THERMAL_GENL_CMD_UNSPEC`, `THERMAL_GENL_CMD_TZ_GET_ID`, `THERMAL_GENL_CMD_TZ_GET_TRIP`, `THERMAL_GENL_CMD_TZ_GET_TEMP`, `THERMAL_GENL_CMD_TZ_GET_GOV`, `THERMAL_GENL_CMD_TZ_GET_MODE`, `THERMAL_GENL_CMD_CDEV_GET`, `THERMAL_GENL_CMD_THRESHOLD_GET`, `THERMAL_GENL_CMD_THRESHOLD_ADD`, `THERMAL_GENL_CMD_THRESHOLD_DELETE`...
- Generator directives/preprocessor guards: `#Generated by maint/enum2xlat.sh from "enum thermal_genl_cmd" in bundled/linux/include/uapi/linux/thermal.h; do not edit.`, `#unconditional`, `#value_indexed`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_thermal_cmd.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/get_mempolicy_flags.in -->
# sources/test-tools/strace/src/xlat/get_mempolicy_flags.in

Purpose: Declarative xlat input table `get_mempolicy_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `MPOL_F_NODE	1`
- Representative constants: `MPOL_F_NODE`, `MPOL_F_ADDR`, `MPOL_F_MEMS_ALLOWED`
- Generator directives/preprocessor guards: `#From include/uapi/linux/mempolicy.h`, `#Prefix MPOL_F_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/get_mempolicy_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getrandom_flags.in -->
# sources/test-tools/strace/src/xlat/getrandom_flags.in

Purpose: Declarative xlat input table `getrandom_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `GRND_NONBLOCK	1`
- Representative constants: `GRND_NONBLOCK`, `GRND_RANDOM`, `GRND_INSECURE`
- Generator directives/preprocessor guards: `#From include/uapi/linux/random.h`, `#Prefix GRND_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getrandom_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_ip_options.in -->
# sources/test-tools/strace/src/xlat/getsock_ip_options.in

Purpose: Declarative xlat input table `getsock_ip_options` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as:  Options specific to getsockopt(SOL_IP).

Important APIs/types/functions:
- Contains 20 constant rows, including `ARPT_SO_GET_INFO`
- Representative constants: `ARPT_SO_GET_INFO`, `ARPT_SO_GET_ENTRIES`, `ARPT_SO_GET_REVISION_MATCH`, `ARPT_SO_GET_REVISION_TARGET`, `EBT_SO_GET_INFO`, `EBT_SO_GET_ENTRIES`, `EBT_SO_GET_INIT_INFO`, `EBT_SO_GET_INIT_ENTRIES`, `IP_VS_SO_GET_VERSION`, `IP_VS_SO_GET_INFO`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/ip_vs.h`, `#From include/uapi/linux/netfilter_arp/arp_tables.h`, `#From include/uapi/linux/netfilter_bridge/ebtables.h`, `#From include/uapi/linux/netfilter_ipv4/ip_tables.h`, `#Prefix ARPT_SO_GET_ EBT_SO_GET_ IP_VS_SO_GET_ IPT_SO_GET_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_ip_options.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_ipv6_options.in -->
# sources/test-tools/strace/src/xlat/getsock_ipv6_options.in

Purpose: Declarative xlat input table `getsock_ipv6_options` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as:  Options specific to getsockopt(SOL_IPV6).

Important APIs/types/functions:
- Contains 4 constant rows, including `IP6T_SO_GET_INFO`
- Representative constants: `IP6T_SO_GET_INFO`, `IP6T_SO_GET_ENTRIES`, `IP6T_SO_GET_REVISION_MATCH`, `IP6T_SO_GET_REVISION_TARGET`
- Generator directives/preprocessor guards: `#From include/uapi/linux/netfilter_ipv6/ip6_tables.h`, `#Prefix IP6T_SO_GET_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_ipv6_options.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_options.in -->
# sources/test-tools/strace/src/xlat/getsock_options.in

Purpose: Declarative xlat input table `getsock_options` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 2 constant rows, including `SO_GET_FILTER 16410`
- Representative constants: `SO_GET_FILTER`, `SO_GET_FILTER`
- Generator directives/preprocessor guards: `#From include/uapi/asm-generic/socket.h`, `#Prefix SO_`, `#if defined __hppa__`, `#else`, `#endif`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_options.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_event_flags.in -->
# sources/test-tools/strace/src/xlat/gpio_event_flags.in

Purpose: Declarative xlat input table `gpio_event_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `GPIOEVENT_REQUEST_BOTH_EDGES`
- Representative constants: `GPIOEVENT_REQUEST_BOTH_EDGES`, `GPIOEVENT_REQUEST_RISING_EDGE`, `GPIOEVENT_REQUEST_FALLING_EDGE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/gpio.h`, `#Prefix GPIOEVENT_REQUEST_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_event_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_handle_flags.in -->
# sources/test-tools/strace/src/xlat/gpio_handle_flags.in

Purpose: Declarative xlat input table `gpio_handle_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `GPIOHANDLE_REQUEST_INPUT`
- Representative constants: `GPIOHANDLE_REQUEST_INPUT`, `GPIOHANDLE_REQUEST_OUTPUT`, `GPIOHANDLE_REQUEST_ACTIVE_LOW`, `GPIOHANDLE_REQUEST_OPEN_DRAIN`, `GPIOHANDLE_REQUEST_OPEN_SOURCE`, `GPIOHANDLE_REQUEST_BIAS_PULL_UP`, `GPIOHANDLE_REQUEST_BIAS_PULL_DOWN`, `GPIOHANDLE_REQUEST_BIAS_DISABLE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/gpio.h`, `#Prefix GPIOHANDLE_REQUEST_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_handle_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_line_flags.in -->
# sources/test-tools/strace/src/xlat/gpio_line_flags.in

Purpose: Declarative xlat input table `gpio_line_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `GPIOLINE_FLAG_KERNEL`
- Representative constants: `GPIOLINE_FLAG_KERNEL`, `GPIOLINE_FLAG_IS_OUT`, `GPIOLINE_FLAG_ACTIVE_LOW`, `GPIOLINE_FLAG_OPEN_DRAIN`, `GPIOLINE_FLAG_OPEN_SOURCE`, `GPIOLINE_FLAG_BIAS_PULL_UP`, `GPIOLINE_FLAG_BIAS_PULL_DOWN`, `GPIOLINE_FLAG_BIAS_DISABLE`
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/gpio.h`, `#Prefix GPIOLINE_FLAG_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_line_flags.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_v2_line_attr_ids.in -->
# sources/test-tools/strace/src/xlat/gpio_v2_line_attr_ids.in

Purpose: Declarative xlat input table `gpio_v2_line_attr_ids` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 3 constant rows, including `GPIO_V2_LINE_ATTR_ID_FLAGS`
- Representative constants: `GPIO_V2_LINE_ATTR_ID_FLAGS`, `GPIO_V2_LINE_ATTR_ID_OUTPUT_VALUES`, `GPIO_V2_LINE_ATTR_ID_DEBOUNCE`
- Generator directives/preprocessor guards: `#Generated by maint/enum2xlat.sh from "enum gpio_v2_line_attr_id" in bundled/linux/include/uapi/linux/gpio.h; do not edit.`, `#unconditional`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gpio_v2_line_attr_ids.in -->
