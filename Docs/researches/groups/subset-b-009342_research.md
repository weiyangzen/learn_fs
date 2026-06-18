# subset-b-009342 research

This grouped report covers the requested strace source files. Each section is source-tree-aligned and bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/s390.c -->
# sources/test-tools/strace/src/s390.c

Purpose: s390/s390x-specific syscall decoders for STHYI hypervisor information, guarded-storage control, runtime instrumentation, and PCI MMIO read/write wrappers.

Important APIs/types/functions: packed STHYI structs (`sthyi_hdr`, `sthyi_machine`, `sthyi_partition`, `sthyi_hypervisor`, `sthyi_guest`), guarded-storage structs, `decode_ebcdic`, `print_sthyi_buf`, section printers, `guard_storage_print_gscb`, `guard_storage_print_gsepl`, and `SYS_FUNC(s390_sthyi)`, `SYS_FUNC(s390_guarded_storage)`, `SYS_FUNC(s390_runtime_instr)`, `SYS_FUNC(s390_pci_mmio_write)`, `SYS_FUNC(s390_pci_mmio_read)`.

Control flow: compiled only for `S390`/`S390X`. `s390_sthyi` prints the function code on entry and, on exit, decodes the page-sized response buffer only for `STHYI_FC_CP_IFL_CAP`; other function codes print the address. STHYI buffer decoding prints a header, then conditionally follows header offsets to machine, partition, hypervisor, and guest sections if offsets and lengths fit within the page. Guarded storage prints command names and decodes the control block only for `GS_SET_BC_CB`; runtime instrumentation prints the signal only for start; PCI write prints input bytes on entry while PCI read prints output bytes on successful exit.

State and persistence behavior: no persistent decoder state. It reads tracee buffers with `umove_or_printaddr`, honors `abbrev(tcp)` by truncating detailed sections, and uses local comments to annotate EBCDIC strings, validity flags, capacity weights, and unknown nonzero tails.

Dependencies and integration points: depends on core print helpers, `PAGE_SIZE`, xlat tables for s390 command/function codes, `current_klongsize`, and arch syscall table mappings. The ABI layouts are locally declared because Linux UAPI does not expose all STHYI/guarded-storage structures.

Risks: manually declared packed structs and offsets must track IBM/kernel ABI changes. Header-provided section offsets are trusted only after range checks, but malformed section sizes still drive truncated comments. Bit comments in guarded-storage event fields are sensitive to correct mask interpretation. EBCDIC conversion is readability-oriented, not a lossless charset conversion.

Test signals: s390 tests should cover full and abbreviated STHYI buffers, bad/short section lengths, unknown tail bytes, invalid section offsets, guarded-storage commands with and without control blocks, runtime start/stop, and successful/failed PCI MMIO read/write output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sched.c -->
# sources/test-tools/strace/src/sched.c

Purpose: decodes scheduler policy, priority, round-robin interval, and `sched_attr` based syscalls.

Important APIs/types/functions: `sprint_policy`, `print_policy`, `print_sched_param`, `do_sched_rr_get_interval`, `print_sched_attr`, and syscall handlers for `sched_getscheduler`, `sched_setscheduler`, `sched_getparam`, `sched_setparam`, `sched_get_priority_min`, `sched_rr_get_interval_time32/time64`, `sched_setattr`, and `sched_getattr`.

Control flow: simple scheduler syscalls print pid and policy/parameter arguments on entry and output parameters on exit. `sched_getscheduler` returns a symbolic aux string for successful return values. `sched_rr_get_interval` shares a helper parameterized by timespec32/timespec64 printers. `print_sched_attr` first reads the user-supplied size, fetches only the available struct version, handles `sched_setattr` keep-policy/keep-params flags, and prints `...` when user/kernel sizes indicate newer fields.

State and persistence behavior: stateless except temporary stack copies. It does not modify tracee memory; it reports kernel-written `attr.size` changes on `sched_setattr` `E2BIG`.

Dependencies and integration points: uses Linux `sched_attr`, xlat tables for policies and flags, pid printers, and time printers. AArch64 has special high-word error formatting for `sched_getattr` size due to a kernel/compiler ABI issue.

Risks: `sched_attr` is versioned and growing; fields must stay aligned with kernel `SCHED_ATTR_SIZE_VER*` constants. `SCHED_FLAG_KEEP_POLICY`/`KEEP_PARAMS` suppress fields in set mode, so tests need both keep and normal paths.

Test signals: cover known/unknown policies, `SCHED_RESET_ON_FORK`, get/set param, time32/time64 RR intervals, `sched_setattr` with size 0, old/new sizes, `E2BIG`, util clamp fields, keep flags, and `sched_getattr` flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/scno.am -->
# sources/test-tools/strace/src/scno.am

Purpose: Automake fragment that generates `scno.h`, a syscall-number header derived from preprocessed architecture syscall table entries.

Important APIs/types/functions: `SCNO_CPPFLAGS`, `syscallent.i` preprocessing rule, `SCNO_SED`, `scno.h` generation rule, `CLEANFILES`, and inclusion of `scno_hook.mk` through an `eval include` hidden from automake.

Control flow: make preprocesses `src/$(OS)/$(ARCH)/syscallent.h` with `config.h` and architecture flags into `syscallent.i`. The `scno.h` rule writes a generated-file banner, appends `scno.head`, runs a sed expression that ignores indirect subcall entries, extracts syscall numbers and names, and emits guarded `__NR_name` definitions with `SYSCALL_BIT`.

State and persistence behavior: produces build artifacts `syscallent.i` and `scno.h`, both registered as clean files. It writes through a temporary `$@-t` file and renames it into place.

Dependencies and integration points: depends on automake variables, C preprocessor, `src/scno.head`, arch syscall tables, and `scno_hook.mk` to add the build dependency from `Makefile` to `scno.h` for ordinary targets.

Risks: the sed expression is tightly coupled to syscall table initializer formatting. New table syntax, nonstandard syscall names, or indirect subcall markers can cause missing or malformed definitions.

Test signals: build on multiple architectures, verify regenerated `scno.h` contains expected `__NR_*` guards, and run `make clean` to confirm generated intermediates are removed.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/scno.am -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/scno_hook.mk -->
# sources/test-tools/strace/src/scno_hook.mk

Purpose: make hook that forces `scno.h` to exist before regenerating `Makefile` for normal build targets.

Important APIs/types/functions: `MAKECMDGOALS` filtering and `Makefile: scno.h` dependency.

Control flow: if goals do not contain `clean` and do not start with `dist`, the fragment adds `scno.h` as a prerequisite of `Makefile`; clean and dist operations avoid this dependency.

State and persistence behavior: no direct file writes; it only changes make dependency graph evaluation.

Dependencies and integration points: included by `scno.am` through `$(eval include ...)`, avoiding automake's direct parsing of the dependency.

Risks: goal filtering is broad and string-based; unusual custom goals containing `clean` or starting with `dist` will skip the hook.

Test signals: invoke ordinary builds, clean targets, and dist targets and confirm `scno.h` is generated only when appropriate.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/scno_hook.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/scsi.c -->
# sources/test-tools/strace/src/scsi.c

Purpose: top-level SCSI ioctl decoder, routing SG_IO v3/v4 requests and decoding common SCSI generic ioctls.

Important APIs/types/functions: `decode_sg_io`, `decode_sg_scsi_id`, `scsi_ioctl`, `decode_sg_io_v3`, `decode_sg_io_v4`, `decode_sg_req_info`, and xlat tables for SG commands/reset flags.

Control flow: for `SG_IO`, entry reads the first 32-bit interface id from the user struct: `'S'` dispatches to v3 and `'Q'` to v4; other ids are printed indirectly. On exit it retrieves the saved interface id from tcb private data and completes response decoding. Other cases decode `SG_GET_SCSI_ID`, request tables, reset flags, pointer integers, value arguments, or return pointer integers only on exit.

State and persistence behavior: uses tcb private data indirectly via the v3/v4 decoders to remember the interface id and entry-side transfer metadata. No durable state beyond syscall entry/exit.

Dependencies and integration points: compiled with richer support when `<scsi/sg.h>` is available. Integrates with the generic ioctl dispatcher and SCSI generic request info decoder.

Risks: SG ioctls mix in/out pointers and interface-id versioning; failure to save entry data leads to unbalanced struct printing. Header availability changes coverage, so build configurations need both paths.

Test signals: exercise SG_IO v3 and v4, unknown interface ids, SG reset bit combinations, pointer integer set/get commands, `SG_GET_SCSI_ID`, and exit-only decode behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/seccomp.c -->
# sources/test-tools/strace/src/seccomp.c

Purpose: decodes the `seccomp` syscall operations and operation-specific argument payloads.

Important APIs/types/functions: `SYS_FUNC(seccomp)`, `decode_seccomp_fprog`, `seccomp_ops`, `seccomp_filter_flags`, `seccomp_ret_action`, and `struct seccomp_notif_sizes`.

Control flow: prints operation on entry, then switches by op. `GET_ACTION_AVAIL` prints raw flags and dereferences an action value. `GET_NOTIF_SIZES` prints flags on entry and decodes returned sizes on exit. `SET_MODE_FILTER` prints filter flags and BPF program. Strict mode and unknown operations print raw flags and address.

State and persistence behavior: no persistent state; reads pointed arguments only when meaningful for the selected operation and syscall phase.

Dependencies and integration points: uses Linux seccomp UAPI, BPF filter decoder, and xlat tables. Pairs with `seccomp_ioctl.c` for user-notification file-descriptor ioctls.

Risks: seccomp operation semantics differ by direction; new operations may need phase-sensitive decoding. `GET_NOTIF_SIZES` carries future-size hints that need ABI-aware tests.

Test signals: cover strict/filter modes, action availability, notification sizes success/failure, unknown ops, invalid pointers, and flag name rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/seccomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/seccomp_ioctl.c -->
# sources/test-tools/strace/src/seccomp_ioctl.c

Purpose: decodes ioctls on seccomp user-notification file descriptors.

Important APIs/types/functions: `seccomp_ioctl`, `print_struct_seccomp_data`, `print_struct_seccomp_notif`, `print_struct_seccomp_notif_resp`, `print_struct_seccomp_notif_addfd`, `SECCOMP_IOCTL_NOTIF_ID_VALID_WRONG_DIR`, and notification/addfd/response xlat tables.

Control flow: `NOTIF_RECV` prints `argp` on entry, suppresses all-zero input structs, and on exit prints notification id, pid, flags, syscall data, arch, IP, and args. `NOTIF_SEND` prints response id/value/error/flags. ID-valid ioctls print a 64-bit id. `ADDFD` decodes source fd, target fd, addfd flags, and open flags. `SET_FLAGS` decodes flags passed directly in the ioctl argument.

State and persistence behavior: no private persistent state; behavior is phase-sensitive for `NOTIF_RECV` because the kernel fills the struct on exit.

Dependencies and integration points: uses seccomp UAPI, audit arch xlat, syscall-name printer, open mode flags, and ioctl size/type checks to detect ABI drift.

Risks: ioctl numbers encode struct sizes, so UAPI changes can break decoding; the file explicitly guards expected sizes. `NOTIF_ID_VALID_WRONG_DIR` compatibility exists for a direction mismatch and should not be removed without test updates.

Test signals: seccomp notification receive with zero/nonzero entry buffers, successful response, negative errno response, addfd flags, id-valid variants, set-flags, and ABI size assertions during build.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/seccomp_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/secontext.c -->
# sources/test-tools/strace/src/secontext.c

Purpose: implements optional SELinux context annotations for traced processes, file descriptors, and paths.

Important APIs/types/functions: `parse_secontext`, `get_expected_filecontext`, `selinux_getpidcon`, `selinux_getfdcon`, `selinux_getfilecon`, `print_context`, `selinux_printfdcon`, `selinux_printfilecon`, and `selinux_printpidcon`.

Control flow: context printing is gated by `secontext_set`. Path and fd helpers resolve the tracee's procfs view (`/proc/PID/root`, `cwd`, `fd`) before calling libselinux. If mismatch checking is enabled, expected contexts are resolved via a cached `selabel_handle`; output prints actual context and appends `!!expected` when the printable actual and expected portions differ.

State and persistence behavior: caches the SELinux label handle and permanently disables mismatch lookup after `selabel_open` fails once. Allocated contexts are freed with `freecon`; resolved paths and expected contexts are local to a print call.

Dependencies and integration points: depends on libselinux, large-file stat wrappers, number-set qualifier state, procfs path helpers, and output quoting state (`xflag`). Called by path/socket/fd printers where SELinux annotations are requested.

Risks: procfs path resolution races with target filesystem changes and fd reuse. Mismatch checking can be unavailable if SELinux policy database cannot be opened. Relative paths rely on `tcp->last_dirfd`; missing or stale dirfd context can suppress annotations.

Test signals: run with full/type-only contexts, mismatch mode, absolute and relative paths, dirfd paths, fd annotations, process annotations, unavailable procfs entries, and disabled/missing SELinux policy.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/secontext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/secontext.h -->
# sources/test-tools/strace/src/secontext.h

Purpose: public interface and compile-time stubs for SELinux context annotation support.

Important APIs/types/functions: `qualify_secontext`, `enum secontext_bits` (`SECONTEXT_FULL`, `SECONTEXT_MISMATCH`), `secontext_set`, `selinux_printfdcon`, `selinux_printfilecon`, and `selinux_printpidcon`.

Control flow: with `ENABLE_SECONTEXT`, the header declares the real functions and qualifier state; otherwise it provides no-op inline implementations for the three print hooks.

State and persistence behavior: header only; real state is the external `number_set *secontext_set` when enabled.

Dependencies and integration points: included by output and address/path decoders that want optional SELinux annotations without sprinkling compile-time guards around call sites.

Risks: no-op stubs must remain signature-compatible with real functions. Adding new secontext modes requires updating the enum, qualifier parser, and tests.

Test signals: build with and without `ENABLE_SECONTEXT`; with support enabled, verify qualifier options populate `secontext_set` and callers link to real functions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/secontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sendfile.c -->
# sources/test-tools/strace/src/sendfile.c

Purpose: decodes `sendfile` and `sendfile64`, including in/out offset pointer updates.

Important APIs/types/functions: `SYS_FUNC(sendfile64)`, `SYS_FUNC(sendfile)`, `umove_or_printaddr`, `umoven_to_uint64_or_printaddr`, `tfetch_to_uint64`, `printfd`, and `tprint_value_changed`.

Control flow: entry prints output fd, input fd, and the initial offset pointer value if readable. If offset is unreadable or count is zero, it prints count immediately and returns decoded. Otherwise it keeps the indirect offset open and on exit prints a changed offset value when the call succeeded and returned nonzero bytes, then prints count.

State and persistence behavior: no tcb private data; the output shape is maintained by leaving the indirect print open between entry and exit.

Dependencies and integration points: uses current personality word size for legacy `sendfile` offset width and fixed 64-bit offset for `sendfile64`.

Risks: offset is optional in Linux semantics, but this decoder relies on safe address printers/fetchers. Entry/exit output balance must remain correct for zero-count, failed, and unreadable-offset cases.

Test signals: null offset, invalid offset, zero count, successful transfer changing offset, no-change transfer, 32-bit and 64-bit personalities, and fd formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sendfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/set_tid_address.c -->
# sources/test-tools/strace/src/set_tid_address.c

Purpose: tiny decoder for `set_tid_address`.

Important APIs/types/functions: `SYS_FUNC(set_tid_address)`, `printaddr`, and return flags `RVAL_DECODED | RVAL_TID`.

Control flow: prints the `tidptr` address and marks the syscall as decoded, with return value interpreted as a thread id.

State and persistence behavior: stateless; it does not dereference the clear-child-tid pointer.

Dependencies and integration points: integrated via syscall tables and core return-value formatting for TIDs.

Risks: low risk; dereferencing would be wrong here because the pointer is a kernel futex/clear-child-tid address rather than a simple input value.

Test signals: verify pointer formatting and TID return annotation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/set_tid_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sg_io_v3.c -->
# sources/test-tools/strace/src/sg_io_v3.c

Purpose: MPERS-aware decoder for SCSI generic SG_IO v3 (`struct sg_io_hdr`) requests and responses.

Important APIs/types/functions: `print_sg_io_buffer`, `decode_request`, `decode_response`, `MPERS_PRINTER_DECL(decode_sg_io_v3)`, `struct_sg_io_hdr`, and xlat tables `sg_io_dxfer_direction`, `sg_io_flags`, and `sg_io_info`.

Control flow: entry prints interface id `'S'`, fetches the struct after the interface field, decodes direction, command buffer, sense-buffer length, iovec count, transfer length, timeout, flags, and outgoing data for TO_DEV/TO_FROM_DEV. It stores an entry copy in tcb private data. Exit fetches the completed struct, validates the interface id, prints incoming data adjusted by residual count, sense data, status fields, duration, residual, and info flags.

State and persistence behavior: stores an allocated entry-side `struct_sg_io_hdr` in tcb private data for exit decoding and fallback printing when the exit fetch fails.

Dependencies and integration points: requires `<scsi/sg.h>` for full decoding; otherwise prints a minimal `'S', ...` shell. Called from `scsi_ioctl` after SG_IO interface dispatch.

Risks: buffer lengths and iovec counts come from tracee memory; incorrect residual handling can overprint or underprint transfer data. MPERS pointer widths must match traced process layout.

Test signals: command-only, data-to-device, data-from-device, bidirectional transfer, iovec and flat buffers, nonzero residual, sense data, changed interface id, exit fetch failure, and builds without SCSI headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sg_io_v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sg_io_v4.c -->
# sources/test-tools/strace/src/sg_io_v4.c

Purpose: decoder for SG_IO v4 / block SCSI generic (`struct sg_io_v4`) requests and responses.

Important APIs/types/functions: `print_sg_io_buffer`, `decode_request`, `decode_response`, `decode_sg_io_v4`, and xlat tables `bsg_protocol`, `bsg_subprotocol`, `bsg_flags`, and shared `sg_io_info`.

Control flow: entry prints guard `'Q'`, protocol/subprotocol, request buffer, request metadata, response maximum length, dout/din iovec counts and lengths, outgoing transfer buffer, timeout, flags, and user pointer; it stores an entry copy. Exit fetches the result struct, validates guard, prints response bytes, incoming data adjusted by `din_resid`, driver/transport/device status, retry delay, info, duration, residuals, and generated tag.

State and persistence behavior: uses tcb private data to retain entry-side addresses and sizes for exit fallback and guard validation.

Dependencies and integration points: uses Linux `<linux/bsg.h>`, generic print/iovec helpers, and is selected by `scsi_ioctl` when the SG_IO interface id is `'Q'`.

Risks: response length is printed twice in the current flow, matching source behavior but worth testing for golden output stability. Residual and iovec length calculations need coverage to avoid reading beyond returned data.

Test signals: v4 requests with request/response buffers, dout and din transfers, iovec paths, residual truncation, guard mismatch, unreadable exit struct, and flag/protocol xlat output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sg_io_v4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/shutdown.c -->
# sources/test-tools/strace/src/shutdown.c

Purpose: decodes the socket `shutdown` syscall.

Important APIs/types/functions: `SYS_FUNC(shutdown)`, `printfd`, and `shutdown_modes` xlat table.

Control flow: prints socket fd and `how` as `SHUT_RD`, `SHUT_WR`, `SHUT_RDWR`, or unknown.

State and persistence behavior: stateless; no tracee memory reads.

Dependencies and integration points: included in socket syscall decoding and depends on `<sys/socket.h>` constants.

Risks: minimal; only xlat coverage for platform constants matters.

Test signals: known shutdown modes, unknown numeric mode, and fd path annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/shutdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sigaltstack.c -->
# sources/test-tools/strace/src/sigaltstack.c

Purpose: MPERS-aware decoder for alternate signal stack structures.

Important APIs/types/functions: `print_stack_t`, `SYS_FUNC(sigaltstack)`, `stack_t`, `sigaltstack_flags`, `DEF_MPERS_TYPE`, and `MPERS_DEFS`.

Control flow: entry decodes the new `ss` stack pointer/flags/size from tracee memory; exit decodes the old stack pointer if provided.

State and persistence behavior: stateless stack-local fetches; no saved entry data.

Dependencies and integration points: uses personality-aware `stack_t` layout and signal-stack xlat flags. Connected to syscall table entries for `sigaltstack`.

Risks: `stack_t` pointer and size widths vary by personality; MPERS generation must match target ABI. Null or unreadable pointers should stay address-only.

Test signals: null `ss`/`old_ss`, invalid pointers, `SS_DISABLE`/`SS_ONSTACK`, 32-bit personality layout, and successful old-stack output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sigaltstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sigevent.h -->
# sources/test-tools/strace/src/sigevent.h

Purpose: local portable definition of a kernel-facing `sigevent`-like structure.

Important APIs/types/functions: `struct_sigevent` with `sigev_value`, `sigev_signo`, `sigev_notify`, `tid`, and thread callback/attribute union fields.

Control flow: header only; consumers fetch and print this layout.

State and persistence behavior: none.

Dependencies and integration points: used by timer/aio/mq style decoders that need a stable internal representation independent of libc header variation.

Risks: pointer width and union layout must match MPERS expectations in consuming files; new notification modes may require downstream print updates.

Test signals: timer or mq syscalls using `SIGEV_SIGNAL`, `SIGEV_THREAD_ID`, and thread callback forms across personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sigevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/signal.c -->
# sources/test-tools/strace/src/signal.c

Purpose: central signal-name, signal-mask, sigaction, signal-delivery, and realtime signal syscall decoders.

Important APIs/types/functions: `signame`, `sprintsigname`, `sprintsigmask_n`, `printsignal`, `print_sigset_addr_len`, `decode_old_sigaction`, `decode_new_sigaction`, `print_sigqueueinfo`, `do_rt_sigtimedwait`, and syscall handlers for old and rt signal APIs plus `pidfd_send_signal` and `restart_syscall`.

Control flow: helper functions map signals including realtime ranges, format dense masks by inverting them when most bits are set, and respect xlat verbosity. Old sigaction handles architecture-specific layouts and optional restorer fields; rt sigaction handles 32-bit tracees on 64-bit kernels with endian-aware mask reconstruction. Syscall handlers choose entry/exit decoding based on whether arguments are input or kernel-filled output. `rt_sigtimedwait` saves the timeout string in tcb private data on entry when siginfo will be printed on exit.

State and persistence behavior: mostly stateless, but uses static buffers for returned strings and tcb private data for `rt_sigtimedwait` timeout preservation. It reads tracee sigsets with bounded `NSIG_BYTES`, not libc `sigset_t` size.

Dependencies and integration points: depends on `nsig.h`, `signalent`, xlat tables for handlers, sigaction flags, procmask commands, pidfd flags, siginfo printers, time printers, and architecture macros (`HAVE_SA_RESTORER`, `MIPS`, `SPARC`, `ALPHA`).

Risks: signal ABI varies heavily by architecture and personality. Static string buffers are overwritten on subsequent calls. Incorrect sigset sizes can overread, so `NSIG_BYTES` and len validation are critical. Old and rt signal paths have different return-value and output-pointer semantics.

Test signals: old and rt sigaction on multiple architectures, restorer/no-restorer layouts, raw/verbose/abbrev xlat modes, dense and sparse masks, invalid sigset lengths, kill/tkill/tgkill, sigqueueinfo, pidfd_send_signal, rt_sigtimedwait entry/exit, realtime signal names, and restart_syscall output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/signalfd.c -->
# sources/test-tools/strace/src/signalfd.c

Purpose: decodes `signalfd` and `signalfd4`.

Important APIs/types/functions: `do_signalfd`, `SYS_FUNC(signalfd)`, `SYS_FUNC(signalfd4)`, `print_sigset_addr_len`, `sfd_flags`, and return flag `RVAL_FD`.

Control flow: shared helper prints fd, mask pointer using the supplied size, size value, and optionally flags for the four-argument variant.

State and persistence behavior: stateless; reads the mask from tracee memory during entry decode.

Dependencies and integration points: relies on signal mask printer from `signal.c`, kernel fd flag constants, and syscall return formatting as a file descriptor.

Risks: kernel requires `sizemask == NSIG_BYTES`, but the decoder prints arbitrary sizes defensively. Flag argument index must remain `3` only for `signalfd4`.

Test signals: signalfd versus signalfd4, known/unknown `SFD_*` flags, invalid mask pointer, nonstandard size, and fd return annotation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/signalfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sigreturn.c -->
# sources/test-tools/strace/src/sigreturn.c

Purpose: delegates `sigreturn` decoding to the architecture-specific implementation while providing shared signal-mask print helpers.

Important APIs/types/functions: `print_sigmask_addr_size`, `tprintsigmask_addr`, `arch_sigreturn`, and `SYS_FUNC(sigreturn)`.

Control flow: includes `arch_sigreturn.c`, calls `arch_sigreturn(tcp)`, and returns decoded. The local helper prints a `{mask=...}` wrapper for arch files that expose saved masks.

State and persistence behavior: no persistent local state; architecture code may read registers or tracee signal frames.

Dependencies and integration points: depends on `ptrace.h`, `regs.h`, `nsig.h`, optional `<asm/sigcontext.h>`, and architecture-specific include selection.

Risks: all meaningful ABI risk sits in per-arch `arch_sigreturn.c` files. This wrapper must keep helper names and include order compatible with those files.

Test signals: architecture-specific sigreturn tests should verify decoded frame fields and masks where supported; builds should cover arches with and without asm sigcontext headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sock.c -->
# sources/test-tools/strace/src/sock.c

Purpose: decodes socket/network interface related ioctls, especially `ifreq` and `ifconf` payloads.

Important APIs/types/functions: `print_ifr_hwaddr`, `print_ifr_map`, `print_ifreq`, `print_ifc_len`, `print_ifconf_ifreq`, `decode_ifconf`, and `MPERS_PRINTER_DECL(sock_ioctl)`.

Control flow: ioctl switch handles `SIOCGIFCONF` with a two-phase decoder that saves the entry `ifconf`, then on exit prints returned length and either the buffer pointer or an array of `ifreq` entries. `ifreq` ioctls print input or output fields according to ioctl direction: socket addresses, hardware addresses, flags, indices, metrics, MTU, names, queue lengths, and maps. Unknown or broad legacy ioctls fall back to address-only printing.

State and persistence behavior: `decode_ifconf` stores the entry `ifconf` in tcb private data to compare returned length/buffer and print output arrays. Other paths are stateless stack fetches.

Dependencies and integration points: MPERS-aware `struct ifreq/ifconf`, socket address printer, hardware address helpers, `iffflags`, `arp_hardware_types`, and generic ioctl dispatcher.

Risks: `ifreq` union interpretation depends entirely on ioctl code. `ifconf` can change both length and pointer on exit, and array decoding depends on returned byte length being a multiple of `struct ifreq`.

Test signals: set/get address ioctls, flags, MTU, names, bridge add/delete, `SIOCGIFCONF` size-query and data-query modes, changed lengths, invalid pointers, and 32-bit personality layout.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sockaddr.c -->
# sources/test-tools/strace/src/sockaddr.c

Purpose: shared socket-address decoder for many Linux address families.

Important APIs/types/functions: `print_sockaddr`, `decode_sockaddr`, `print_inet_addr`, `decode_inet_addr`, per-family printers for UNIX, INET/INET6, AX.25, IPX, X.25, netlink, packet, TIPC, Bluetooth, RxRPC, IEEE 802.15.4, ALG, NFC, VSOCK, QRTR, XDP, and MCTP, plus `sa_printers`.

Control flow: `decode_sockaddr` validates minimum length, copies at most `sockaddr_storage`, zero-pads the local buffer, then calls `print_sockaddr`. `print_sockaddr` prints `sa_family`, dispatches to a family printer only when the family has a registered printer and `addrlen` satisfies that printer's minimum length, otherwise prints raw `sa_data`. Family printers handle byte-order wrappers, nested unions, variable-length arrays, optional tail fields, abstract UNIX names, SELinux file context annotations, and xlat verbosity.

State and persistence behavior: stateless except local static buffers in address-to-string helpers. All tracee memory is copied into a bounded local storage buffer before decoding.

Dependencies and integration points: heavily used by socket syscalls and `sock.c`; depends on many Linux protocol headers, xlat tables, netlink constants, SELinux context hooks, MAC/hardware address printers, and xlat verbosity policy.

Risks: address-family structs evolve and may be shorter than current headers; min-length guards and raw fallback protect output but can miss newer fields. Bluetooth endian wrappers use host-endian conversion based on `is_bigendian`. UNIX path and SELinux annotation are path-sensitive. Numerous xlat tables make golden output broad.

Test signals: valid and short addresses for every registered family, unknown families, abstract UNIX sockets, IPv4/IPv6 raw/verbose output, AX.25 validity/raw paths, packet hardware address truncation, Bluetooth length variants, NFC 32/64-bit service-name length, XDP shared-UMEM fd, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sockaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/socketcall.c -->
# sources/test-tools/strace/src/socketcall.c

Purpose: decodes the legacy multiplexed `socketcall` syscall shell.

Important APIs/types/functions: `SYS_FUNC(socketcall)` and `socketcalls` xlat table.

Control flow: prints the socket subcall number symbolically and prints the argument vector address without decoding the nested arguments here.

State and persistence behavior: stateless.

Dependencies and integration points: used on architectures with legacy socketcall multiplexing; detailed subcall decoding is handled elsewhere after syscall dispatch.

Risks: intentionally shallow; if syscall dispatch does not remap subcalls, output remains only the raw argument vector.

Test signals: known and unknown socketcall numbers and argument pointer formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/socketcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/socketutils.c -->
# sources/test-tools/strace/src/socketutils.c

Purpose: runtime socket metadata resolver, mapping socket inodes to printable protocol/address details and discovering generic netlink family names.

Important APIs/types/functions: cache helpers, `send_query`, `receive_responses`, `inet_send_query`, `inet_parse_response`, `unix_send_query`, `unix_parse_response`, `netlink_send_query`, `netlink_parse_response`, `get_proto_by_name`, `get_family_by_proto`, `get_sockaddr_by_inode`, and `genl_families_xlat`.

Control flow: socket inode lookup first checks a 1024-slot direct-mapped cache. On miss it opens a NETLINK_SOCK_DIAG socket, queries either a known protocol or all protocols, parses matching inet/unix/netlink diagnostic responses, caches a formatted string, and falls back to `PROTO:[inode]` when only a protocol name is known. Generic netlink discovery lazily opens NETLINK_GENERIC, dumps controller families, and builds a dynamic xlat table from family id/name attributes.

State and persistence behavior: global inode cache stores allocated detail strings and replaces entries by `inode & CACHE_MASK`. A static fallback string and static dynamic xlat persist across calls. Cache entries are process-local and never invalidated except by collision replacement.

Dependencies and integration points: depends on netlink diag UAPI, protocol xlat tables, `getfdproto`, kernel version (`os_release`) for UNIX dump behavior, `dyxlat`, and low-level socket syscalls from the tracer process.

Risks: runtime diagnostic sockets can fail due to permissions, kernel support, namespaces, or races with socket closure. Direct-mapped cache can return stale details if an inode is reused before collision replacement. Generic netlink family dump assumes controller response version 2.

Test signals: inode lookup for TCP/UDP IPv4/IPv6, UNIX path and peer info, netlink protocol info, unknown protocol fallback, cache hit/collision, failed diagnostic socket, older UNIX diag dump flag behavior, and generic netlink family xlat creation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/socketutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sparc.c -->
# sources/test-tools/strace/src/sparc.c

Purpose: SPARC-specific decoder for `kern_features` return flags.

Important APIs/types/functions: `SYS_FUNC(kern_features)` and `sparc_kern_features` xlat table.

Control flow: compiled only for SPARC/SPARC64. It does nothing on entry or syscall error; on successful exit it formats the return value as flag names in `tcp->auxstr` and asks return-value formatting to show both hex and string.

State and persistence behavior: no persistent state beyond assigning transient auxstr.

Dependencies and integration points: architecture syscall table and return formatting.

Risks: xlat table must track kernel feature bits; no argument decoding exists because the syscall exposes feature flags via return value.

Test signals: successful return with single/multiple bits, unknown bits, and error path without aux string.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sparc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/sram_alloc.c -->
# sources/test-tools/strace/src/sram_alloc.c

Purpose: Blackfin-only decoder for `sram_alloc`.

Important APIs/types/functions: `SYS_FUNC(sram_alloc)` and `sram_alloc_flags`.

Control flow: compiled only under `BFIN`. Prints size and allocation flags, then marks return value as decoded hexadecimal.

State and persistence behavior: stateless.

Dependencies and integration points: depends on `<bfin_sram.h>` and the Blackfin syscall table.

Risks: architecture-specific code can bit-rot because modern build/test coverage may be sparse. Flag names must match Blackfin SRAM allocation constants.

Test signals: Blackfin build plus known, combined, and unknown SRAM allocation flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/sram_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/stage_output.c -->
# sources/test-tools/strace/src/stage_output.c

Purpose: provides staged syscall output buffering so partially decoded output can be published only on success or dropped on failure.

Important APIs/types/functions: `struct staged_output_data`, `strace_open_memstream`, `strace_close_memstream`, `open_memstream`, `tcp->outf`, and `tcp->staged_output_data`.

Control flow: when `HAVE_OPEN_MEMSTREAM` is available, open allocates staging data, opens a dynamic memory stream, flushes it once so buffer pointers are initialized, saves the real output stream, and redirects `tcp->outf`. Close restores the real stream, optionally writes the staged buffer to it, otherwise logs a debug drop, then frees buffer and staging data. Without `open_memstream`, functions effectively return `NULL`/do nothing.

State and persistence behavior: mutates per-tcb output stream state while staging is active. Cleanup resets `tcp->staged_output_data` to `NULL` and frees all allocated memory.

Dependencies and integration points: used by decoders that cannot know until exit whether staged output should be emitted. Depends on libc `open_memstream` availability and strace error/debug helpers.

Risks: unbalanced open/close would leave `tcp->outf` redirected or leak memory. Nested staging is not supported by this structure. `fclose`/`fflush` failures are reported but staged output may be lost.

Test signals: publish and drop paths, double-close debug path, `open_memstream` failure handling if injectable, and build without `HAVE_OPEN_MEMSTREAM`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/stage_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/stat.c -->
# sources/test-tools/strace/src/stat.c

Purpose: decodes legacy/non-64-bit `stat`, `fstat`, and `newfstatat` syscalls into the common `strace_stat` printer.

Important APIs/types/functions: `decode_struct_stat`, `SYS_FUNC(stat)`, `SYS_FUNC(fstat)`, `SYS_FUNC(newfstatat)`, `fetch_struct_stat`, `print_struct_stat`, `printpath`, `printfd`, `print_dirfd`, and `at_flags`.

Control flow: entry prints path, fd, or dirfd/path inputs. Exit fetches the output stat buffer and prints it through the normalized common stat representation; `newfstatat` then prints flags.

State and persistence behavior: stateless stack-local normalized stat data.

Dependencies and integration points: relies on architecture/personality-specific `fetch_struct_stat` and shared `stat.h` internal representation. Integrates with path/fd printing and AT flag xlats.

Risks: all ABI complexity is in fetch helpers; this wrapper must call the correct fetch function for non-64-bit stat layout. Flags are output on exit, so failed syscalls still show path inputs but may not decode a stat buffer.

Test signals: stat/fstat/newfstatat success and failure, invalid statbuf, symlink/no-follow flags, and personality-specific stat layout.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/stat.h -->
# sources/test-tools/strace/src/stat.h

Purpose: internal normalized file-stat structure used by stat fetchers and printers.

Important APIs/types/functions: `struct strace_stat` fields for device, inode, rdev, size, blocks, blksize, mode, links, uid/gid, timestamps, nanoseconds, and `has_nsec`.

Control flow: header only; fetchers populate the normalized structure and printers consume it.

State and persistence behavior: none.

Dependencies and integration points: included by `stat.c`, `stat64.c`, stat fetch implementations, and common stat printing code.

Risks: normalized field widths must be wide enough for every supported kernel ABI. `has_nsec` controls timestamp precision and must be set correctly by fetchers.

Test signals: stat output with large inode/device/size values, nanosecond and non-nanosecond ABIs, uid/gid formatting, and device/rdev printing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/stat64.c -->
# sources/test-tools/strace/src/stat64.c

Purpose: decodes 64-bit stat-family syscalls using the common `strace_stat` representation.

Important APIs/types/functions: `decode_struct_stat64`, `SYS_FUNC(stat64)`, `SYS_FUNC(fstat64)`, `SYS_FUNC(fstatat64)`, `fetch_struct_stat64`, and `print_struct_stat`.

Control flow: mirrors `stat.c`: entry prints path/fd/dirfd inputs; exit fetches and prints stat64 output buffer; `fstatat64` prints `AT_*` flags.

State and persistence behavior: stateless stack-local decode.

Dependencies and integration points: depends on `fetch_struct_stat64`, `stat.h`, path/fd helpers, and syscall table mappings for older 32-bit ABIs exposing `stat64`.

Risks: easy to confuse with `stat.c`; fetch helper selection is the main correctness boundary. 64-bit fields must remain normalized without truncation.

Test signals: stat64/fstat64/fstatat64 on 32-bit personalities, large files/inodes, invalid output buffers, and flags output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/stat64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/statfs.c -->
# sources/test-tools/strace/src/statfs.c

Purpose: decodes `statfs` path and output filesystem-stat buffer.

Important APIs/types/functions: `SYS_FUNC(statfs)`, `printpath`, and `print_struct_statfs`.

Control flow: entry prints pathname; exit prints `buf` via the common statfs printer.

State and persistence behavior: stateless; output buffer is read only on exit.

Dependencies and integration points: depends on architecture-specific statfs fetch/print support behind `print_struct_statfs`.

Risks: `statfs` layout varies by architecture; wrapper correctness depends on the common printer.

Test signals: valid statfs, invalid buffer, unknown filesystem magic, and path decode failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/statfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/statfs.h -->
# sources/test-tools/strace/src/statfs.h

Purpose: normalized internal representation for filesystem stat data.

Important APIs/types/functions: `struct strace_statfs` fields for type, block sizes/counts, file counts, fsid, name length, fragment size, and mount flags.

Control flow: header only; fetchers fill this representation for common printers.

State and persistence behavior: none.

Dependencies and integration points: included by statfs fetch/print implementations and statfs syscall wrappers.

Risks: fields must cover old and new statfs ABI widths without loss. `f_flags` availability varies by kernel/ABI and must be handled by fetchers.

Test signals: filesystem magic, large block/file counts, fsid rendering, and statfs variants with and without flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/statfs64.c -->
# sources/test-tools/strace/src/statfs64.c

Purpose: decodes `statfs64`, including the user-provided structure size parameter.

Important APIs/types/functions: `SYS_FUNC(statfs64)`, `printpath`, `PRINT_VAL_U`, and `print_struct_statfs64`.

Control flow: entry prints pathname and size. Exit prints the output buffer by passing both buffer address and user size to the statfs64 printer.

State and persistence behavior: stateless.

Dependencies and integration points: used by architectures exposing `statfs64`; depends on common statfs64 printer and path decoding.

Risks: size argument controls how much the kernel wrote and what the printer may read; wrong size handling can misdecode compat ABIs.

Test signals: expected size, short/zero/oversized size, invalid buffer, and large statfs64 values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/statfs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/static_assert.h -->
# sources/test-tools/strace/src/static_assert.h

Purpose: portability wrapper for `static_assert` across compilers and C language levels.

Important APIs/types/functions: includes `assert.h`, maps to existing `static_assert` or `_Static_assert`, and provides a GNU-compatible extern-array fallback.

Control flow: preprocessor chooses the native/static assertion mechanism when available. If neither is available, the fallback creates an extern function declaration whose array size is invalid when the expression is false.

State and persistence behavior: compile-time only; no runtime state.

Dependencies and integration points: widely included by files that validate local ABI structs against kernel sizes.

Risks: fallback uses a declaration form and suppresses nested-extern warnings under GCC; portability to non-GNU compilers without static assertions is limited.

Test signals: build with C11 static assertions, compiler `_Static_assert`, and fallback configurations; verify both passing and intentionally failing assertions behave at compile time.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/static_assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/statmount.c -->
# sources/test-tools/strace/src/statmount.c

Purpose: decodes the modern `statmount` syscall request and variable-length mount-stat response.

Important APIs/types/functions: `print_quoted_cstring_sequence`, `print_mnt_id_req`, `print_statmount`, `SYS_FUNC(statmount)`, `PRINT_FIELD_CSTRING_OFFSET`, `PRINT_FIELD_CSTRING_SEQUENCE`, and xlat tables for statmount flags/masks, superblock flags, and mount propagation.

Control flow: entry prints a versioned `mnt_id_req`: first reads `size`, then fetches available fields, including namespace fd, mount id, parameter mask, optional namespace id, and nonzero unknown tail bytes. Exit fetches `struct statmount` up to caller buffer size, optionally fetches trailing string storage, and prints fields only when their mask bits are set. String fields are offsets into the trailing buffer; string sequences iterate null-terminated entries with truncation checks.

State and persistence behavior: stateless local copies. It reads at most one page of unknown request tail and caps string-buffer reads to `PATH_MAX * 3`.

Dependencies and integration points: depends on Linux mount UAPI, `fsmagic`, `mount_attr_attr`, sequence truncation helpers, and syscall table mapping for new mount APIs.

Risks: `statmount` is versioned and still evolving; mask-gated fields, offset strings, and trailing arrays are easy to misalign. Invalid offsets are printed numerically. New mask bits require printer updates and xlat additions.

Test signals: old/new `mnt_id_req` sizes, request tail bytes, all mask groups, invalid string offsets, truncated string sequences, option/security/uidmap/gidmap arrays, supported mask, flags, and short buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/statmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/statx.c -->
# sources/test-tools/strace/src/statx.c

Purpose: decodes `statx` inputs and the extended output `struct_statx`.

Important APIs/types/functions: `print_statx_timestamp`, `SYS_FUNC(statx)`, `struct_statx`, `struct_statx_timestamp`, `statx_masks`, `statx_attrs`, `at_statx_sync_types`, and `print_symbolic_mode_t`.

Control flow: entry prints dirfd, pathname, flags split into statx sync type plus generic `AT_*` flags, and requested mask. Exit fetches statx buffer, prints returned mask, block size in full mode, attributes, and then conditionally prints fields based on returned mask and attribute bits. Abbreviated mode prints core fields and `...`; full mode includes timestamps with human-readable comments, device ids, mount id, DIO alignment, subvolume, atomic write fields, and DIO read alignment.

State and persistence behavior: stateless local fetch of output buffer on exit.

Dependencies and integration points: uses local `statx.h` layout rather than relying solely on system headers, plus common path/fd/mode/time printers.

Risks: statx continues to grow; local struct layout and conditional field masks must track kernel UAPI. Attribute-gated atomic write fields depend on `STATX_ATTR_WRITE_ATOMIC`, while other fields depend on `stx_mask`.

Test signals: all major mask bits, abbrev/full modes, timestamp comments, atomic write attributes, DIO alignment/read alignment, sync-type flags mixed with generic flags, invalid output pointer, and unknown masks/attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/statx.h -->
# sources/test-tools/strace/src/statx.h

Purpose: local definition of `statx` timestamp and result structures for stable decoding across build hosts.

Important APIs/types/functions: `struct_statx_timestamp` and `struct_statx` with mask, block size, attributes, ownership, mode, inode, size, blocks, timestamps, device ids, mount id, DIO alignment, subvolume, atomic write fields, DIO read alignment, optimized atomic write size, and reserved space.

Control flow: header only; `statx.c` fetches and interprets this layout.

State and persistence behavior: none.

Dependencies and integration points: included by `statx.c`; supplements kernel/libc headers so strace can decode newer fields even on older build environments.

Risks: must exactly match Linux UAPI layout, including reserved padding. Adding fields in the wrong order breaks all downstream field decoding.

Test signals: compile-time layout checks where available, statx syscalls returning newer fields, and builds on older libc/kernel-header environments.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/statx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/strace-graph -->
# sources/test-tools/strace/src/strace-graph

Purpose: Perl utility that reads `strace -f` output and renders a process tree showing forks/clones/vforks, execs, and approximate elapsed times.

Important APIs/types/functions: global hashes `%unfinished`, `%running_fqname`, `%pr`; parsing helpers `parse_str`, `parse_one`, `parseargs`; trace handlers `handle_trace`, `handle_killed`; display helpers `straight_seq`, `first_exec`, `display_pid_trace`, and `display_trace`.

Control flow: the main loop strips a leading pid, optional timestamps, rejoins unfinished/resumed syscalls, ignores signal and normal-exit marker lines, handles killed markers, parses `call(args) = result` plus optional syscall duration, and passes events to `handle_trace`. `handle_trace` records successful exec argv, child process creation, and exits. `display_trace` climbs to the root parent and recursively prints an ASCII tree with elapsed time divided by a hardcoded slowdown scale.

State and persistence behavior: stores all observed process records in memory until EOF. Tracks running pid-to-qualified-name mapping using `pid-time` to distinguish pid reuse when timestamps exist.

Dependencies and integration points: expects strace text output, preferably with `-f`, `-q`, and sufficient string size. It is a standalone installed helper rather than part of libstrace.

Risks: parser is regex-based and supports only a subset of strace grammar. Complex nested structs, escaped strings, unfinished syscall mismatches, missing timestamps, pid reuse without timestamps, and locale/output format changes can produce warnings or wrong trees. The slowdown scale is fixed.

Test signals: traces with exec, fork/clone/vfork, nested children, unfinished/resumed syscalls, killed processes, timestamped and untimestamped formats, malformed lines, truncated strings, and pid reuse with timestamps.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/strace-graph -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/strace-log-merge -->
# sources/test-tools/strace/src/strace-log-merge

Purpose: shell utility that merges per-pid `strace -ff -tt[t]` log files into one timestamp-sorted stream.

Important APIs/types/functions: `show_usage`, `iterate_logfiles`, `process_suffix`, `process_logfile`, timestamp regex variables `dd`/`ds`, `sort`, `sed`, and `grep`.

Control flow: validates one argument or help. It scans `STRACE_LOG.*`, keeps only numeric positive suffixes, first computes the widest suffix for aligned pid prefixes, then emits sortable lines by extracting timestamps and adding the pid suffix. The combined stream is stable-numeric sorted on the synthetic timestamp key, stripped back to original line content with pid prefix, and empty lines removed.

State and persistence behavior: no persistent state; reads matching log files and writes merged output to stdout. Adds an extra newline after each file to tolerate missing final newlines.

Dependencies and integration points: intended for logs produced by `strace -ff -tt`, `-ttt`, or similar timestamp options. Uses POSIX shell plus standard `sed`, `sort`, `grep`, and `printf`.

Risks: timestamp extraction is format-sensitive; logs without expected timestamps yield an error. Numeric suffix filtering ignores non-pid auxiliary files. Sorting by numeric synthetic key can only be as precise as parsed timestamp fields.

Test signals: merge hh:mm:ss, hh:mm:ss.usec, and epoch.usec logs; missing final newline; nonnumeric suffix files; no matching logs; malformed/non-timestamped logs; and equal timestamps requiring stable sort.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/strace-log-merge -->
