# subset-b-009333 research

Grouped research report for 64-bit Linux strace ioctl and indirect subcall table headers. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/64/ioctls_inc.h -->
# sources/test-tools/strace/src/linux/64/ioctls_inc.h

Purpose: generated 64-bit Linux ioctl definition input for strace. The file is an initializer fragment consumed by the build-time `ioctlsort` helper, not a standalone C translation unit. It maps ioctl symbols to their originating Linux UAPI header, direction bits, command/type-number value, and encoded argument size so strace can later print symbolic ioctl names instead of only numeric command words.

Important APIs/types/functions: there are no functions or local types in this file. Every data row has the shape `{ "header/path.h", "IOCTL_SYMBOL", dir, type_nr, size }`, matching `struct ioctlent` in `ioctlsort.c` with fields `info`, `name`, `dir`, `type_nr`, and `size`. Direction values are `_IOC_NONE`, `_IOC_READ`, `_IOC_WRITE`, `_IOC_READ|_IOC_WRITE`, or legacy `0`. `ioctlsort.c` converts each row to an encoded command with `type_nr | (size << _IOC_SIZESHIFT) | (dir << _IOC_DIRSHIFT)` and emits sorted `{ "symbol", code }` rows for `ioctlent*.h`. The runtime table type is the smaller `struct_ioctlent` from `defs.h`, containing only `symbol` and `code`.

Control flow: the header participates in a generation pipeline. `ioctls_gen.sh` creates this file from Linux include-tree definitions. During the strace build, `Makefile.am` derives `ioctlent%.h` from architecture-specific `ioctls_inc*.h` files by running `ioctlsort%`. `ioctlsort` includes this fragment, sorts first by symbol/header to remove duplicate symbol names, then sorts by encoded command and symbol, suppressing prefix-shadowed entries for the same code. `syscall.c` includes the generated `ioctlent0.h`/personality variants into `ioctlent` arrays, and `ioctl.c` uses binary search plus `ioctl_next_match` to print all names sharing a numeric command.

State and persistence behavior: this file is static build input. It has no runtime mutation, no persistent storage, and no direct side effects. Its contents persist indirectly in generated `ioctlent*.h` files and compiled strace binaries. When strace switches personality at runtime, `set_personality` selects the matching generated ioctl table and count, so this 64-bit table can be active only for personalities wired to the 64-bit Linux ioctl include set.

Dependencies: depends on the Linux UAPI header set used by `ioctls_gen.sh`, strace's local `_IOC_*` bit layout from `ioctl_iocdef.h`, and the build rules in `Makefile.am`. It is shared by architecture wrappers such as `linux/x86_64/ioctls_inc0.h`, `linux/aarch64/ioctls_inc0.h`, `linux/riscv64/ioctls_inc0.h`, `linux/s390x/ioctls_inc0.h`, and other 64-bit Linux ports that include `../64/ioctls_inc.h`.

Integration points: runtime lookup flows through `ioctl_lookup` in `ioctl.c`, which assumes the generated table is sorted by encoded command. The ioctl decoder then combines symbolic command printing with fd-aware special handling for overlapping tty/sound command ranges. Build-time integration also produces `ioctl_redefs%.h` for non-primary personalities by comparing generated ioctl tables.

Data profile: the file contains one generator comment plus 3,402 initializer rows. The largest source groups in this snapshot include `drm/drm.h` (110 rows), `linux/soundcard.h` (90), `sound/asound.h` (89), `linux/videodev2.h` (83), `asm-generic/ioctls.h` (76), and `linux/sockios.h` (76). Direction distribution is 401 legacy `0`, 558 `_IOC_NONE`, 586 `_IOC_READ`, 920 `_IOC_WRITE`, and 937 `_IOC_READ|_IOC_WRITE`. There are no duplicate symbol names in this generated file, but many encoded command collisions are expected across subsystems; the most duplicated encoded tuple observed is `_IOC_READ|_IOC_WRITE, 0x6441, 0x10`.

Risks: correctness is sensitive to the Linux header snapshot and to 64-bit ABI structure sizes. Stale entries produce misleading ioctl names, while incorrect `size` or direction bits can make command encoding differ from the traced program's ABI. Duplicate numeric ioctl commands are normal, but prefix suppression in `ioctlsort` can hide longer names if ordering assumptions change. Legacy rows with direction `0` and size `0` are valid and must not be rejected by validators just because they do not use `_IOC_*` direction macros.

Test signals: useful checks include regenerating `ioctlent0.h` and confirming `ioctlsort` exits cleanly, verifying the generated output is sorted by code for `bsearch`, checking there are no duplicate symbols before sorting, and running strace ioctl decoding tests that exercise tty overlap ranges, DRM ioctls, socket ioctls, and legacy zero-direction commands. A lightweight static signal is that all non-comment lines match the five-field initializer format and the row count stays explainable against the kernel header refresh that produced it.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/64/ioctls_inc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/64/subcallent.h -->
# sources/test-tools/strace/src/linux/64/subcallent.h

Purpose: 64-bit Linux wrapper for the generic strace indirect subcall table. It adapts the generic socket and SysV IPC subcall entries so 64-bit personalities route `recvmmsg` and `semtimedop` through the time64 decoder implementations.

Important APIs/types/functions: the file temporarily defines `sys_semtimedop` as `sys_semtimedop_time64` and `sys_recvmmsg` as `sys_recvmmsg_time64`, includes `../generic/subcallent.h`, then undefines both macros. The included generic table emits indexed `struct_sysent` initializers for indirect socket subcalls (`socket`, `bind`, `connect`, `recvmsg`, `recvmmsg`, `sendmmsg`, and others) and IPC subcalls (`semop`, `semget`, `semctl`, `semtimedop`, message queue calls, and shared-memory calls). The generic table requires `SYS_socket_subcall` to be defined by the including architecture's `syscallent.h`.

Control flow: architecture syscall tables define a base indirect-subcall number, usually `SYS_socket_subcall 500` for older multiplexed ABIs, then include `../64/subcallent.h`. Preprocessor substitution changes only the decoder function names used by the generic `SEN(recvmmsg)` and `SEN(semtimedop)` entries. After inclusion, the wrapper immediately undefines the aliases so later syscall-table entries or declarations are not accidentally rewritten.

State and persistence behavior: this is compile-time table composition only. It creates no runtime state and persists no data. Its effect is baked into the generated/compiled `sysent` table for architectures that include the 64-bit subcall wrapper. At runtime, strace dispatches through the selected personality's `sysent` entry, which will call the time64-aware decoder function for the affected subcalls.

Dependencies: depends on `../generic/subcallent.h`, `struct_sysent` initializer conventions, `SEN(...)` syscall decoder-name macros, and trace flag macros such as `TRACE_INDIRECT_SUBCALL`, `TN`, `TI`, `TM`, and `SI`. It also depends on the existence of `sys_recvmmsg_time64` and `sys_semtimedop_time64` decoder implementations and on each including architecture defining `SYS_socket_subcall`.

Integration points: included by 64-bit Linux syscall tables for multiplexed-subcall architectures, including `linux/powerpc64/syscallent.h`, `linux/s390x/syscallent.h`, `linux/sparc64/syscallent.h`, `linux/sh64/syscallent.h`, and MIPS n64 through `linux/mips/syscallent-n64.h`. The generic table computes `SYS_ipc_subcall` immediately after socket subcalls, so both socket and IPC multiplexers share one contiguous synthetic syscall-number area.

Risks: the wrapper relies on exact macro names used inside the generic table. If `generic/subcallent.h` changes an entry name or adds another time-sensitive decoder without a corresponding 64-bit alias, 64-bit subcall decoding can silently use the wrong time ABI. Missing `#undef` lines would leak macro substitutions into subsequent includes. Including this wrapper without `SYS_socket_subcall` defined triggers the generic table's preprocessor error.

Test signals: compile coverage for every architecture that includes `../64/subcallent.h` is the primary signal. Runtime strace tests should cover indirect `recvmmsg` and `semtimedop` decoding on affected 64-bit personalities and verify timeout/timespec fields are interpreted as time64. Preprocessor inspection of the built syscall table should show `SEN(recvmmsg)` resolving to `sys_recvmmsg_time64` and `SEN(semtimedop)` resolving to `sys_semtimedop_time64` only inside this included section.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/64/subcallent.h -->
