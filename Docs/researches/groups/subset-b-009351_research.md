# subset-b-009351 research

Grouped source-tree-aligned research report for the exact strace test files assigned to subset B work item `subset-b-009351`. Each section preserves the source path in its title and is wrapped in deterministic markers for reconciliation into per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios.c -->
# sources/test-tools/strace/tests/ioctl_termios.c

Purpose: Exercises strace decoding of terminal termio, termios, and optional termios2 ioctl commands. It covers setters and getters for TCSETS*, TCGETS*, TCSETA*, TCGETA, TIOCSLCKTRMIOS, and TIOCGLCKTRMIOS, including command-name collisions on architectures where tty and sound ioctl numbers overlap.

Important APIs/types/functions: Uses `ioctl`, direct `openat` of `/dev/ptmx`, `struct termio`, `struct termios`, optional `struct termios2`, `kernel_ulong_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `fill_memory`, `fill_memory_ex`, `printxval`, and xlat tables `baud_options` and `term_line_discs`. Helper printers include `print_iflag`, `print_oflag`, `print_cflag`, `print_lflag`, `print_flags`, `print_termios_cc`, `print_termios2`, `print_termios`, `print_termio`, and `do_ioctl`.

Control flow: The program allocates tail-guarded structures, opens a real tty via `/dev/ptmx`, then iterates a table of command families. For each command it tests NULL, off-by-one, misaligned, and valid pointers. Setter commands populate the structure before the syscall so strace can print input data; getter commands issue the syscall first and print either decoded output or the raw pointer depending on return status. Setup variants intentionally use random fill, patterned fill, and deterministic flag/control-character values.

State/persistence behavior: It creates only process-local tty state through the opened ptmx descriptor and in-memory termios buffers. No persistent filesystem state is written. The expected output preserves errno across pre-syscall printing for getter cases, and the tty descriptor is needed to resolve ioctl collision names correctly.

Dependencies: Requires Linux tty/termios UAPI headers, syscall numbers from `scno.h`, strace test helpers, and architecture-specific macro availability such as `HAVE_STRUCT_TERMIOS2`, `HAVE_STRUCT_TERMIOS_C_ISPEED`, `IBSHIFT`, `CIBAUD`, and layout differences for Alpha, PowerPC, MIPS, SPARC, HPPA, and others.

Integration points: Validates strace's ioctl decoder, xlat rendering, structure field printers, verbose versus abbreviated control-character output, and architecture-specific tty ABI handling. It is also a regression test for ioctl number ambiguity when an invalid fd prevents type-based disambiguation.

Risks: Output is highly architecture-sensitive: control-character indexes, unknown flag masks, `XTABS` handling, input/output speed fields, and clashed ioctl names differ by platform. A kernel or libc header change can alter field availability or constants. The test also depends on `/dev/ptmx` being available.

Test signals: Expected output includes decoded bitsets for input/output/control/local flags, c_cc arrays in verbose builds, line disciplines, `sprintrc` return strings, invalid pointer fallbacks, and `+++ exited with 0 +++`. Failures usually indicate a tty ioctl decoder regression, bad arch conditional, or changed UAPI layout.

Source read signal: complete file read for this research pass; file size 1003 line(s), 22385 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tiocm.c -->
# sources/test-tools/strace/tests/ioctl_tiocm.c

Purpose: Tests decoding of modem-control TIOCM ioctls: `TIOCMGET`, `TIOCMBIS`, `TIOCMBIC`, and `TIOCMSET`.

Important APIs/types/functions: Uses `ioctl`, `sprintrc`, `kernel_ulong_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, and strace `XLAT_*` formatting macros for `TIOCM_*` flags. `do_ioctl` and `do_ioctl_ptr` centralize syscall execution and saved return formatting.

Control flow: For every command, the test issues NULL and faulting-pointer cases. For on-enter commands it passes invalid and valid modem flag words, expecting symbolic expansion such as `TIOCM_LE`, `TIOCM_DTR`, `TIOCM_RTS`, `TIOCM_CTS`, `TIOCM_CAR`, `TIOCM_DSR`, `TIOCM_OUT1`, `TIOCM_OUT2`, and `TIOCM_LOOP`; for the getter it expects only pointer printing on failure.

State/persistence behavior: All state is an in-memory `unsigned int` allocated at a guard page boundary. It uses fd `-1`, so no device state is mutated and all normal syscalls fail with EBADF.

Dependencies: Depends on tty ioctl constants from system headers and the strace test framework. MIPS has a different valid/invalid mask, handled by conditional `VALID_FLAGS` and `INVALID_FLAGS`.

Integration points: Exercises the ioctl decoder's distinction between input and output pointer semantics and its flag-table behavior under raw, abbreviated, and verbose xlat modes.

Risks: Architecture-specific modem-bit definitions can change output. Treating `TIOCMGET` as an on-enter argument would be a decoder bug because failed getters must not dereference the output buffer.

Test signals: Successful output prints NULL, fault address, unknown flag fallback, known flag expansion, `sprintrc` failures, and the final exit marker.

Source read signal: complete file read for this research pass; file size 104 line(s), 2377 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tiocm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi-success.c -->
# sources/test-tools/strace/tests/ioctl_ubi-success.c

Purpose: Compile-time wrapper for `ioctl_ubi.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, fault-injected success output for UBI ioctl decoder coverage for attach, eraseblock, volume, rename, resize, and property requests.

Important APIs/types/functions: The wrapper contributes `INJECT_RETVAL`=42 and then includes `ioctl_ubi.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_ubi.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_ubi.c`.

Dependencies: Depends on `ioctl_ubi.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 48 bytes, substantive behavior must be understood through `ioctl_ubi.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_ubi.c` under abbreviated/default xlat output, fault-injected success output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 48 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi.c -->
# sources/test-tools/strace/tests/ioctl_ubi.c

Purpose: Exercises decoding of UBI ioctl commands and UBI request structures, including no-argument commands, integer pointer commands, 64-bit integer pointer commands, and complex volume/eraseblock structures.

Important APIs/types/functions: Uses `ioctl`, `<mtd/ubi-user.h>`, `struct ubi_attach_req`, `ubi_leb_change_req`, `ubi_map_req`, `ubi_mkvol_req`, `ubi_rnvol_req`, `ubi_rsvol_req`, and `ubi_set_vol_prop_req`. Helpers `do_ioctl`, `do_ioctl_ptr`, optional `skip_ioctls`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `fill_memory`, `fill_memory_ex`, and `CLAMP` drive expected output construction.

Control flow: The program first handles optional fault-injection locking when `INJECT_RETVAL` is defined. It then tests no-arg UBI volume block ioctls, pointer-to-int commands, pointer-to-int64 commands, NULL and faulting pointers for structured requests, and filled valid structures for attach, LEB change, LEB map, make volume, rename volume, resize volume, and set volume property. Rename-volume coverage intentionally varies `count`, name length, embedded NUL bytes, and maximum-name boundary cases.

State/persistence behavior: The normal variant calls every ioctl on fd `-1`, so no UBI device state is touched. State is limited to deterministic in-memory request buffers and the global `errstr`. The success wrapper uses injected return values to exercise output-argument annotations such as updated UBI or volume ids without requiring a real device.

Dependencies: Depends on Linux UBI UAPI structs and constants, strace tail allocation helpers, and fault-injection test support when compiled through the success wrapper.

Integration points: Validates strace's UBI ioctl decoder, enum rendering for volume type, data type, flags, volume properties, string truncation, array decoding, NULL/fault pointer handling, and ioctl number clash reporting for a legacy `NET_REMOVE_IF` value.

Risks: UBI UAPI changes can add fields or constants. Name-length handling is easy to regress because the decoder must avoid reading beyond fixed UAPI limits while preserving ellipsis behavior. Injected-success output must stay synchronized with strace fault-injection semantics.

Test signals: Expected lines include decoded UBI structures, unknown `dtype`, volume-name truncation, `=>` result fields on injected success, and `+++ exited with 0 +++`.

Source read signal: complete file read for this research pass; file size 303 line(s), 8906 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_udmabuf.c -->
# sources/test-tools/strace/tests/ioctl_udmabuf.c

Purpose: Tests decoding of `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST` ioctl arguments for single and list-based DMA buffer creation.

Important APIs/types/functions: Uses `<linux/udmabuf.h>`, `struct udmabuf_create`, `struct udmabuf_create_list`, `struct udmabuf_create_item`, `ioctl`, `skip_if_unavailable`, and strace `strval32`/`strval64` fixtures.

Control flow: `main` verifies `/proc/self/fd/` availability, then `test_create` checks NULL and four populated `udmabuf_create` combinations. `test_create_list` allocates a variable-length structure sized with `offsetof(..., list)` plus four list entries, fills list items, varies top-level flags, and prints nested item arrays.

State/persistence behavior: It only reads `/proc/self/fd/` availability and uses fd `-1`, so there are no persistent kernel objects. The apparent fd `0</dev/null>` text is expected strace fd-path rendering, not a new persistent resource.

Dependencies: Requires a kernel header exposing UDMABUF ioctl structs and flags. It relies on strace test helpers for tail allocation and return formatting.

Integration points: Covers ioctl decoders that print memfd arguments with fd paths, flag xlat output for `UDMABUF_FLAGS_CLOEXEC`, unsigned widening of negative offsets/sizes, and variable-length array decoding.

Risks: Header availability and struct layout are relatively new, and list count handling can over-read if the decoder ignores size/count boundaries. Raw versus symbolic flag output must remain stable.

Test signals: Output should show NULL handling, four single-create structures, four create-list structures with nested list entries, EBADF return strings, and the final exit marker.

Source read signal: complete file read for this research pass; file size 124 line(s), 3123 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_udmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_uffdio.c -->
# sources/test-tools/strace/tests/ioctl_uffdio.c

Purpose: Exercises userfaultfd ioctl decoding for API negotiation, memory registration, copy, zeropage, wake, unregister, write-protect, continue, and poison requests.

Important APIs/types/functions: Uses `userfaultfd` via `syscall(__NR_userfaultfd, O_NONBLOCK)`, `ioctl`, `mmap`, `madvise`, `getpagesize`, `struct uffdio_api`, `uffdio_register`, `uffdio_copy`, `uffdio_zeropage`, `uffdio_range`, `uffdio_writeprotect`, `uffdio_continue`, and `uffdio_poison`. It also uses `xlat/uffd_api_features.h` to print negotiated features.

Control flow: First it runs every supported UFFDIO request against fd `-1` with NULL and zeroed structure pointers. It then creates a real nonblocking userfaultfd, negotiates `UFFDIO_API`, maps two anonymous pages, registers one page for missing faults, copies data into the registered page, tests invalid copy mode bits, zeropages, wakes, unregisters, write-protects, continues, and poisons.

State/persistence behavior: The only kernel state is a transient userfaultfd registration and anonymous memory mappings inside the process. The code avoids touching the registered missing-fault area except through userfaultfd ioctls to prevent a self-stall.

Dependencies: Requires `__NR_userfaultfd`, Linux userfaultfd UAPI headers, anonymous mmap support, and kernel support for the newer ioctls guarded by header constants. Uses strace helpers and xlat feature tables.

Integration points: Validates strace decoding of nested `uffdio_range`, feature/ioctl bitmasks, output fields such as `copy`, `zeropage`, `mapped`, and `updated`, and unknown mode-bit fallbacks.

Risks: Kernel feature availability varies; some calls can fail legitimately while still testing decoder formatting. Userfaultfd semantics are sensitive to accidental memory access in the registered range.

Test signals: Expected output includes EBADF cases, API feature/ioctl bitsets on success, pointer/range formatting, DONTWAKE/WRITEPROTECT/POISON modes, and final clean exit.

Source read signal: complete file read for this research pass; file size 261 line(s), 8975 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_uffdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-Xabbrev.c

Purpose: Compile-time wrapper for `ioctl_v4l2.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for negative-path V4L2 ioctl decoder coverage with failed ioctls and xlat-mode-sensitive output.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `ioctl_v4l2.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2.c`.

Dependencies: Depends on `ioctl_v4l2.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 24 bytes, substantive behavior must be understood through `ioctl_v4l2.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 24 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-Xraw.c

Purpose: Compile-time wrapper for `ioctl_v4l2.c`. It does not implement an independent test body; instead it selects raw xlat output for negative-path V4L2 ioctl decoder coverage with failed ioctls and xlat-mode-sensitive output.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ioctl_v4l2.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2.c`.

Dependencies: Depends on `ioctl_v4l2.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 43 bytes, substantive behavior must be understood through `ioctl_v4l2.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 43 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-Xverbose.c

Purpose: Compile-time wrapper for `ioctl_v4l2.c`. It does not implement an independent test body; instead it selects verbose xlat output for negative-path V4L2 ioctl decoder coverage with failed ioctls and xlat-mode-sensitive output.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ioctl_v4l2.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2.c`.

Dependencies: Depends on `ioctl_v4l2.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 47 bytes, substantive behavior must be understood through `ioctl_v4l2.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 47 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success-Xabbrev.c

Purpose: Compile-time wrapper for `ioctl_v4l2-success.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for injected-success V4L2 decoder coverage for output and bidirectional structures.

Important APIs/types/functions: The wrapper contributes `XLAT_ABBREV`=1 and then includes `ioctl_v4l2-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-success.c`.

Dependencies: Depends on `ioctl_v4l2-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 54 bytes, substantive behavior must be understood through `ioctl_v4l2-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-success.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 54 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success-Xraw.c

Purpose: Compile-time wrapper for `ioctl_v4l2-success.c`. It does not implement an independent test body; instead it selects raw xlat output for injected-success V4L2 decoder coverage for output and bidirectional structures.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ioctl_v4l2-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-success.c`.

Dependencies: Depends on `ioctl_v4l2-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 51 bytes, substantive behavior must be understood through `ioctl_v4l2-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-success.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 51 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success-Xverbose.c

Purpose: Compile-time wrapper for `ioctl_v4l2-success.c`. It does not implement an independent test body; instead it selects verbose xlat output for injected-success V4L2 decoder coverage for output and bidirectional structures.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ioctl_v4l2-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-success.c`.

Dependencies: Depends on `ioctl_v4l2-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 55 bytes, substantive behavior must be understood through `ioctl_v4l2-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-success.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 55 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xabbrev.c

Purpose: Compile-time wrapper for `ioctl_v4l2-success-v.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for verbose build of the injected-success V4L2 ioctl decoder.

Important APIs/types/functions: The wrapper contributes `XLAT_ABBREV`=1 and then includes `ioctl_v4l2-success-v.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-success-v.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-success-v.c`.

Dependencies: Depends on `ioctl_v4l2-success-v.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 56 bytes, substantive behavior must be understood through `ioctl_v4l2-success-v.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-success-v.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 56 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xraw.c

Purpose: Compile-time wrapper for `ioctl_v4l2-success-v.c`. It does not implement an independent test body; instead it selects raw xlat output for verbose build of the injected-success V4L2 ioctl decoder.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ioctl_v4l2-success-v.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-success-v.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-success-v.c`.

Dependencies: Depends on `ioctl_v4l2-success-v.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 53 bytes, substantive behavior must be understood through `ioctl_v4l2-success-v.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-success-v.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 53 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xverbose.c

Purpose: Compile-time wrapper for `ioctl_v4l2-success-v.c`. It does not implement an independent test body; instead it selects verbose xlat output for verbose build of the injected-success V4L2 ioctl decoder.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ioctl_v4l2-success-v.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-success-v.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-success-v.c`.

Dependencies: Depends on `ioctl_v4l2-success-v.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 57 bytes, substantive behavior must be understood through `ioctl_v4l2-success-v.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-success-v.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 57 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success-v.c

Purpose: Compile-time wrapper for `ioctl_v4l2-success.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, verbose structure-field output for injected-success V4L2 decoder coverage for output and bidirectional structures.

Important APIs/types/functions: The wrapper contributes `VERBOSE`=1 and then includes `ioctl_v4l2-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-success.c`.

Dependencies: Depends on `ioctl_v4l2-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 50 bytes, substantive behavior must be understood through `ioctl_v4l2-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-success.c` under abbreviated/default xlat output, verbose structure-field output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 50 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-success.c

Purpose: Injected-success V4L2 ioctl decoder test. It exercises output-argument and bidirectional-argument formatting for many V4L2 structs without depending on a real video device.

Important APIs/types/functions: Uses `ioctl`, `strtoul`/`strtol` for fault-injection lock-on arguments, V4L2 structs from `kernel_v4l2_types.h`, `fill_fmt`, `print_fmt`, and optional `test_v4l2_buffer_time32`. It covers `VIDIOC_QUERYCAP`, `VIDIOC_ENUM_FMT`, `VIDIOC_REQBUFS`, `VIDIOC_EXPBUF`, `VIDIOC_G/S/TRY_FMT`, buffer queue ioctls, framebuffer, stream parameters, standards, inputs, controls, tuners, crop, frame sizes/intervals, create buffers, extended control queries, and menu queries.

Control flow: `main` exits silently if run without injection parameters, otherwise it loops over `VIDIOC_QUERYCAP` until strace fault injection returns the requested non-negative value. After lock-on, it populates structures with deterministic patterns and issues each ioctl against fd `-1`; expected output appends `(INJECTED)` and includes decoded output fields as if the calls succeeded.

State/persistence behavior: No real video state is touched because fd `-1` and injected return values drive the success path. State is the filled structure memory, persistent static clip storage in `fill_fmt`, and output formatting controlled by compile-time `VERBOSE` and `XLAT_*` macros.

Dependencies: Requires strace fault-injection harness, V4L2 compatibility types, fcntl flag constants, optional time32 structures, and xlat mode macros. The executable must receive `NUM_SKIP INJECT_RETVAL`.

Integration points: Validates success-path ioctl decoding for nested structures, output updates, decoded capabilities, controls, buffer flags, timestamps, frame intervals, query dimensions, fourcc names, and verbose-only reserved fields.

Risks: Large combinatorial coverage means UAPI additions, enum renames, or struct layout changes can ripple through expected output. Injection lock-on must stay aligned with test driver options; otherwise the test fails before the decoder logic runs.

Test signals: Look for an initial injected `VIDIOC_QUERYCAP` lock line, decoded structures with `= <retval> (INJECTED)`, optional verbose reserved fields, raw/abbrev/verbose xlat differences, and the final exit marker.

Source read signal: complete file read for this research pass; file size 1768 line(s), 61755 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-v-Xabbrev.c

Purpose: Compile-time wrapper for `ioctl_v4l2-v.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for verbose build of the negative-path V4L2 ioctl decoder.

Important APIs/types/functions: The wrapper contributes `XLAT_ABBREV`=1 and then includes `ioctl_v4l2-v.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-v.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-v.c`.

Dependencies: Depends on `ioctl_v4l2-v.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 48 bytes, substantive behavior must be understood through `ioctl_v4l2-v.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-v.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 48 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-v-Xraw.c

Purpose: Compile-time wrapper for `ioctl_v4l2-v.c`. It does not implement an independent test body; instead it selects raw xlat output for verbose build of the negative-path V4L2 ioctl decoder.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ioctl_v4l2-v.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-v.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-v.c`.

Dependencies: Depends on `ioctl_v4l2-v.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 45 bytes, substantive behavior must be understood through `ioctl_v4l2-v.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-v.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 45 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-v-Xverbose.c

Purpose: Compile-time wrapper for `ioctl_v4l2-v.c`. It does not implement an independent test body; instead it selects verbose xlat output for verbose build of the negative-path V4L2 ioctl decoder.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ioctl_v4l2-v.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2-v.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2-v.c`.

Dependencies: Depends on `ioctl_v4l2-v.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 49 bytes, substantive behavior must be understood through `ioctl_v4l2-v.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2-v.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 49 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-v.c

Purpose: Compile-time wrapper for `ioctl_v4l2.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, verbose structure-field output for negative-path V4L2 ioctl decoder coverage with failed ioctls and xlat-mode-sensitive output.

Important APIs/types/functions: The wrapper contributes `VERBOSE`=1 and then includes `ioctl_v4l2.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2.c`.

Dependencies: Depends on `ioctl_v4l2.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 3 line(s) and 95 bytes, substantive behavior must be understood through `ioctl_v4l2.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2.c` under abbreviated/default xlat output, verbose structure-field output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 3 line(s), 95 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2.c -->
# sources/test-tools/strace/tests/ioctl_v4l2.c

Purpose: Negative-path V4L2 ioctl decoder test. It verifies strace formatting for unknown V4L2 ioctl numbers, unsupported known commands, and many supported command argument shapes when syscalls fail with EBADF.

Important APIs/types/functions: Uses `ioctl`, `kernel_v4l2_types.h`, `kernel_fcntl.h`, V4L2 structures such as `v4l2_format`, `v4l2_fmtdesc`, `kernel_v4l2_buffer_t`, `v4l2_requestbuffers`, `v4l2_framebuffer`, `v4l2_streamparm`, `v4l2_control`, `v4l2_tuner`, `v4l2_queryctrl`, `v4l2_ext_controls`, `v4l2_frmsizeenum`, `v4l2_frmivalenum`, `v4l2_create_buffers`, `v4l2_exportbuffer`, and `v4l2_querymenu`. Helpers include `fourcc`, `init_v4l2_format`, `dprint_ioctl_v4l2`, and the `print_ioctl_v4l2` macro.

Control flow: The test allocates a filled page, brute-forces unknown `_IOC` values with V4L2 type `'V'` while skipping known VT/VBox conflicts, prints unsupported commands with raw arguments, then runs a long sequence of known commands with NULL, faulting, minimal, and filled structures. `init_v4l2_format` populates each buffer type union arm so `S_FMT` and `TRY_FMT` cover pix, multiplanar, overlay, VBI, sliced VBI, SDR, and metadata layouts.

State/persistence behavior: All calls use fd `-1`, so no video device is required and no kernel device state changes. State is deterministic in tail-allocated buffers, page-end fault probes, and compile-time xlat mode macros.

Dependencies: Requires the strace kernel V4L2 compatibility headers, ioctl and fcntl constants, endian conditionals, optional time32 buffer types, and xlat macros controlling raw/abbrev/verbose output.

Integration points: Tests the V4L2 ioctl decoder, fourcc rendering, nested union selection by `type`, flag and enum xlat rendering, output truncation for ext-control arrays, and behavior differences under `XLAT_RAW`, default abbreviated, and `XLAT_VERBOSE` builds.

Risks: V4L2 UAPI evolves quickly; new command numbers or enum values can change unknown/unsupported expectations. Structure layout and endian-dependent fourcc output are regression-prone. Because the test uses failed syscalls, the decoder must not treat all pointer arguments as successful output buffers.

Test signals: Expected output is large and includes unknown `_IOC` lines, supported command names, EBADF return markers, symbolic or raw xlat output according to wrapper mode, and `+++ exited with 0 +++`.

Source read signal: complete file read for this research pass; file size 1382 line(s), 48611 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog-success-v.c -->
# sources/test-tools/strace/tests/ioctl_watchdog-success-v.c

Purpose: Compile-time wrapper for `ioctl_watchdog-success.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, verbose structure-field output for injected-success watchdog ioctl decoder coverage.

Important APIs/types/functions: The wrapper contributes `VERBOSE`=1 and then includes `ioctl_watchdog-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_watchdog-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_watchdog-success.c`.

Dependencies: Depends on `ioctl_watchdog-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 54 bytes, substantive behavior must be understood through `ioctl_watchdog-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_watchdog-success.c` under abbreviated/default xlat output, verbose structure-field output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 54 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog-success.c -->
# sources/test-tools/strace/tests/ioctl_watchdog-success.c

Purpose: Compile-time wrapper for `ioctl_watchdog.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, fault-injected success output for watchdog ioctl decoder coverage.

Important APIs/types/functions: The wrapper contributes `INJECT_RETVAL`=42 and then includes `ioctl_watchdog.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_watchdog.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_watchdog.c`.

Dependencies: Depends on `ioctl_watchdog.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 53 bytes, substantive behavior must be understood through `ioctl_watchdog.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_watchdog.c` under abbreviated/default xlat output, fault-injected success output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 53 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog.c -->
# sources/test-tools/strace/tests/ioctl_watchdog.c

Purpose: Tests decoding of Linux watchdog `WDIOC*` ioctl commands, including support-query structures, integer getter/setter commands, option flags, keepalive, and unknown watchdog ioctl numbers.

Important APIs/types/functions: Uses `ioctl`, `<linux/watchdog.h>`, `struct watchdog_info`, xlat table `watchdog_ioctl_cmds`, `do_ioctl`, `do_ioctl_ptr`, optional `INJECT_RETVAL` lock-on logic, and compile-time `VERBOSE` for detailed identity printing.

Control flow: With injection enabled, the program loops on `WDIOC_GETSUPPORT` until the injected return is observed. It then allocates and fills `watchdog_info`, tries support decoding, iterates simple integer getters, tests timeout setters, decodes `WDIOC_SETOPTIONS` for known and unknown `WDIOS_*` bits, emits `WDIOC_KEEPALIVE`, and tests an unknown `_IOC(_IOC_NONE, 'W', 0xff, 0)` command.

State/persistence behavior: Normal operation uses fd `-1`, so it creates no watchdog state. In-memory buffers and `errstr` carry state between syscall and printf. The success wrappers use injection only.

Dependencies: Linux watchdog UAPI headers, strace xlat macros, and fault-injection support for success variants.

Integration points: Validates ioctl command-name xlat lookup, watchdog option/identity structure decoding, integer pointer rendering, verbose truncation behavior, and injected-success `=>` handling.

Risks: Watchdog option flags can grow; verbose and abbreviated variants must agree on which fields are elided. Injection argument handling is a separate failure mode.

Test signals: Expected output includes support structure or pointer fallback, simple getter/setter lines, `WDIOS_*` flags, keepalive with no argument, unknown ioctl formatting, injected markers in success builds, and final exit.

Source read signal: complete file read for this research pass; file size 169 line(s), 4288 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_winsize.c -->
# sources/test-tools/strace/tests/ioctl_winsize.c

Purpose: Tests decoding of terminal window-size ioctls `TIOCGWINSZ` and `TIOCSWINSZ`.

Important APIs/types/functions: Uses `ioctl`, `struct winsize`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `fill_memory`, and `sprintrc`.

Control flow: Issues NULL getter and setter calls, then uses a tail-allocated `winsize` and an immediately faulting pointer. It expects failed getter output to remain a pointer and setter output to decode `{ws_row, ws_col, ws_xpixel, ws_ypixel}` on entry.

State/persistence behavior: Uses fd `-1`, so no tty state is changed. All data is local memory.

Dependencies: Requires tty ioctl constants and the strace test helper library.

Integration points: Small regression test for ioctl direction semantics on terminal window-size structures.

Risks: Misclassifying `TIOCGWINSZ` as input or dereferencing output buffers on failed syscalls would produce wrong output.

Test signals: Lines for NULL, fault pointer, raw output pointer, decoded setter struct, and clean exit.

Source read signal: complete file read for this research pass; file size 43 line(s), 1052 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_winsize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioperm.c -->
# sources/test-tools/strace/tests/ioperm.c

Purpose: Tests strace decoding of the `ioperm` syscall on architectures where `__NR_ioperm` exists.

Important APIs/types/functions: Uses direct `syscall(__NR_ioperm, ...)`, `kernel_ulong_t` fixture values, `sprintrc`, and `SKIP_MAIN_UNDEFINED`.

Control flow: Calls `ioperm` once with deliberately oversized/bogus `from`, `num`, and `turn_on` values, prints low-width argument formatting and the syscall result, then exits.

State/persistence behavior: The bogus request is expected to fail, so no I/O permission bitmap state is granted. There is no persistent state.

Dependencies: Architecture syscall availability through `scno.h` and Linux permission checks.

Integration points: Verifies scalar syscall argument decoding and skip behavior on unsupported architectures.

Risks: On unusual kernels the failure errno may vary, but formatting should remain stable. Running as privileged code still uses nonsensical ranges.

Test signals: One `ioperm(...) = ...` line or a skip build when the syscall number is unavailable.

Source read signal: complete file read for this research pass; file size 32 line(s), 527 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioperm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/iopl.c -->
# sources/test-tools/strace/tests/iopl.c

Purpose: Tests strace decoding of the `iopl` syscall on architectures exposing `__NR_iopl`.

Important APIs/types/functions: Uses `syscall(__NR_iopl, level)`, `kernel_ulong_t`, `sprintrc`, and `SKIP_MAIN_UNDEFINED`.

Control flow: Performs a single bogus `iopl` call with a wide constant, prints the truncated level as strace should see it, and exits.

State/persistence behavior: The invalid privilege-level request should fail; no persistent process I/O privilege state is expected.

Dependencies: Architecture syscall availability and normal kernel privilege enforcement.

Integration points: Covers scalar argument formatting for legacy x86-style I/O privilege syscalls.

Risks: Privilege-sensitive syscalls must not accidentally succeed in a way that changes the test process state; the bogus value mitigates that.

Test signals: One decoded `iopl(...)` line or skip on unsupported targets.

Source read signal: complete file read for this research pass; file size 30 line(s), 415 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/iopl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio--pidns-translation.c -->
# sources/test-tools/strace/tests/ioprio--pidns-translation.c

Purpose: Compile-time wrapper for `ioprio.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, PID namespace translation for ioprio syscall decoder coverage.

Important APIs/types/functions: The wrapper contributes `PIDNS_TRANSLATION`=#include "ioprio.c" and then includes `ioprio.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioprio.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioprio.c`.

Dependencies: Depends on `ioprio.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 46 bytes, substantive behavior must be understood through `ioprio.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioprio.c` under abbreviated/default xlat output, PID namespace translation. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 46 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio-Xabbrev.c -->
# sources/test-tools/strace/tests/ioprio-Xabbrev.c

Purpose: Compile-time wrapper for `ioprio.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for ioprio syscall decoder coverage.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `ioprio.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioprio.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioprio.c`.

Dependencies: Depends on `ioprio.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 20 bytes, substantive behavior must be understood through `ioprio.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioprio.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 20 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio-Xraw.c -->
# sources/test-tools/strace/tests/ioprio-Xraw.c

Purpose: Compile-time wrapper for `ioprio.c`. It does not implement an independent test body; instead it selects raw xlat output for ioprio syscall decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ioprio.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioprio.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioprio.c`.

Dependencies: Depends on `ioprio.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 39 bytes, substantive behavior must be understood through `ioprio.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioprio.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 39 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio-Xverbose.c -->
# sources/test-tools/strace/tests/ioprio-Xverbose.c

Purpose: Compile-time wrapper for `ioprio.c`. It does not implement an independent test body; instead it selects verbose xlat output for ioprio syscall decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ioprio.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioprio.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioprio.c`.

Dependencies: Depends on `ioprio.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 43 bytes, substantive behavior must be understood through `ioprio.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioprio.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 43 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio.c -->
# sources/test-tools/strace/tests/ioprio.c

Purpose: Tests decoding of `ioprio_get` and `ioprio_set`, including process and process-group selectors, priority class/value formatting, invalid selectors, and optional PID namespace translation.

Important APIs/types/functions: Uses `syscall(__NR_ioprio_get)`, `syscall(__NR_ioprio_set)`, `getpid`, `getpgid`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, and xlat table `ioprio_class`.

Control flow: The program prints a bogus `ioprio_get`, a real process `ioprio_get`, an `ioprio_set` for the current process group with `IOPRIO_CLASS_NONE`, and a bogus `ioprio_set` with a malformed priority. Output branches on `XLAT_RAW`, `XLAT_VERBOSE`, and abbreviated mode.

State/persistence behavior: It may attempt to set the process group's I/O priority, but the chosen class/value and permission context are test-local. PID namespace mode only affects printed pid annotations.

Dependencies: Requires both ioprio syscalls, pid namespace helper support, and the ioprio xlat table.

Integration points: Validates strace syscall decoders, xlat verbosity modes, priority bit packing via `IOPRIO_PRIO_VALUE`, and pid namespace translation rendering.

Risks: Kernel permission rules or cgroup/scheduler behavior can alter return codes. Namespace annotations differ when compiled through the PIDNS wrapper.

Test signals: Expected lines include unknown selector fallback, current PID/PGID annotations, optional decoded return priority, and final `+++ exited with 0 +++` with pidns leader prefix.

Source read signal: complete file read for this research pass; file size 134 line(s), 3312 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-Xabbrev.c -->
# sources/test-tools/strace/tests/ip_local_port_range-Xabbrev.c

Purpose: Compile-time wrapper for `ip_local_port_range.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for IP_LOCAL_PORT_RANGE sockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_ABBREV`=1 and then includes `ip_local_port_range.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_local_port_range.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_local_port_range.c`.

Dependencies: Depends on `ip_local_port_range.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 55 bytes, substantive behavior must be understood through `ip_local_port_range.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_local_port_range.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 55 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-Xraw.c -->
# sources/test-tools/strace/tests/ip_local_port_range-Xraw.c

Purpose: Compile-time wrapper for `ip_local_port_range.c`. It does not implement an independent test body; instead it selects raw xlat output for IP_LOCAL_PORT_RANGE sockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ip_local_port_range.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_local_port_range.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_local_port_range.c`.

Dependencies: Depends on `ip_local_port_range.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 52 bytes, substantive behavior must be understood through `ip_local_port_range.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_local_port_range.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 52 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-Xverbose.c -->
# sources/test-tools/strace/tests/ip_local_port_range-Xverbose.c

Purpose: Compile-time wrapper for `ip_local_port_range.c`. It does not implement an independent test body; instead it selects verbose xlat output for IP_LOCAL_PORT_RANGE sockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ip_local_port_range.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_local_port_range.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_local_port_range.c`.

Dependencies: Depends on `ip_local_port_range.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 56 bytes, substantive behavior must be understood through `ip_local_port_range.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_local_port_range.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 56 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ip_local_port_range-success-Xabbrev.c

Purpose: Compile-time wrapper for `ip_local_port_range-success.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for injected-success IP_LOCAL_PORT_RANGE sockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_ABBREV`=1 and then includes `ip_local_port_range-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_local_port_range-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_local_port_range-success.c`.

Dependencies: Depends on `ip_local_port_range-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 63 bytes, substantive behavior must be understood through `ip_local_port_range-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_local_port_range-success.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 63 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success-Xraw.c -->
# sources/test-tools/strace/tests/ip_local_port_range-success-Xraw.c

Purpose: Compile-time wrapper for `ip_local_port_range-success.c`. It does not implement an independent test body; instead it selects raw xlat output for injected-success IP_LOCAL_PORT_RANGE sockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ip_local_port_range-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_local_port_range-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_local_port_range-success.c`.

Dependencies: Depends on `ip_local_port_range-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 60 bytes, substantive behavior must be understood through `ip_local_port_range-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_local_port_range-success.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 60 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success-Xverbose.c -->
# sources/test-tools/strace/tests/ip_local_port_range-success-Xverbose.c

Purpose: Compile-time wrapper for `ip_local_port_range-success.c`. It does not implement an independent test body; instead it selects verbose xlat output for injected-success IP_LOCAL_PORT_RANGE sockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ip_local_port_range-success.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_local_port_range-success.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_local_port_range-success.c`.

Dependencies: Depends on `ip_local_port_range-success.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 64 bytes, substantive behavior must be understood through `ip_local_port_range-success.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_local_port_range-success.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 64 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success.c -->
# sources/test-tools/strace/tests/ip_local_port_range-success.c

Purpose: Compile-time wrapper for `ip_local_port_range.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, fault-injected success output for IP_LOCAL_PORT_RANGE sockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `INJSTR`=" (INJECTED)" and then includes `ip_local_port_range.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_local_port_range.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_local_port_range.c`.

Dependencies: Depends on `ip_local_port_range.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 62 bytes, substantive behavior must be understood through `ip_local_port_range.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_local_port_range.c` under abbreviated/default xlat output, fault-injected success output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 62 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range.c -->
# sources/test-tools/strace/tests/ip_local_port_range.c

Purpose: Tests socket option decoding for Linux `IP_LOCAL_PORT_RANGE`, including the packed low/high 16-bit port range annotation.

Important APIs/types/functions: Uses `setsockopt`, `getsockopt`, `SOL_IP`, fallback definition of `IP_LOCAL_PORT_RANGE`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `TAIL_ALLOC_OBJECT_CONST_ARR`, `print_quoted_hex`, and xlat mode macros.

Control flow: Iterates thirteen packed range values. For each, it exercises negative length, zero length, short length, faulting optval, normal 4-byte optval, 5-byte length, and 8-byte oversized buffer for both setter and getter paths. The success wrapper injects `INJSTR` into every expected return line.

State/persistence behavior: The test uses fd `0` and does not create a socket in this file; expected failures or injected success keep state local. The `ports` and `big_ports` buffers are overwritten for each case.

Dependencies: Requires socket APIs, IPv4 level constants, and strace xlat macros. The option number is locally defined when absent from host headers.

Integration points: Validates strace sockopt decoders for size-sensitive integer options, packed range comments like `12345..`, raw/verbose/abbrev output, and injected-success formatting.

Risks: If run with an inherited fd 0 that is a valid IPv4 socket, return codes may differ, but decoder output is still the focus. Port-range comment formatting is easy to regress when raw mode is active.

Test signals: Many `setsockopt`/`getsockopt` lines with `[0x... /* range */]`, quoted short buffers, pointer fallback for failed getters, optional `(INJECTED)`, and clean exit.

Source read signal: complete file read for this research pass; file size 185 line(s), 5694 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_mreq.c -->
# sources/test-tools/strace/tests/ip_mreq.c

Purpose: Tests decoding of IPv4 and IPv6 multicast membership socket options using `struct ip_mreq` and `struct ipv6_mreq`.

Important APIs/types/functions: Uses `inet_pton`, `socket`, `setsockopt`, `ifindex_lo`, `IP_ADD_MEMBERSHIP`, `IP_DROP_MEMBERSHIP`, `IPV6_ADD_MEMBERSHIP`, `IPV6_DROP_MEMBERSHIP`, `IPV6_JOIN_ANYCAST`, and `IPV6_LEAVE_ANYCAST`.

Control flow: Builds IPv4 and IPv6 multicast request structures, opens an IPv4 datagram socket on fd 0, then for each option tests negative length, one-byte-short length, faulting optval, exact structure length, and `INT_MAX` oversized length.

State/persistence behavior: The test may join/drop multicast groups on the temporary socket, but all state is process/socket scoped and disappears at exit. It closes fd 0 before opening the socket to stabilize printed fd values.

Dependencies: Requires IPv4 and IPv6 multicast constants plus loopback interface lookup. It skips when host headers do not expose required options or `lo` is unavailable.

Integration points: Validates sockopt structure decoders for IPv4 addresses, IPv6 addresses, interface indexes, and exact/oversized length behavior.

Risks: Network namespace configuration and IPv6 support can affect availability. Interface-index string output is environment-dependent through `IFINDEX_LO_STR`.

Test signals: Expected output includes pointer failures, decoded `inet_addr`/`inet_pton` structures, loopback ifindex, and final exit.

Source read signal: complete file read for this research pass; file size 142 line(s), 3834 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_mreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol-Xabbrev.c -->
# sources/test-tools/strace/tests/ip_protocol-Xabbrev.c

Purpose: Compile-time wrapper for `ip_protocol.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for IP_PROTOCOL getsockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_ABBREV`=1 and then includes `ip_protocol.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_protocol.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_protocol.c`.

Dependencies: Depends on `ip_protocol.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 47 bytes, substantive behavior must be understood through `ip_protocol.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_protocol.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 47 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol-Xraw.c -->
# sources/test-tools/strace/tests/ip_protocol-Xraw.c

Purpose: Compile-time wrapper for `ip_protocol.c`. It does not implement an independent test body; instead it selects raw xlat output for IP_PROTOCOL getsockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ip_protocol.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_protocol.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_protocol.c`.

Dependencies: Depends on `ip_protocol.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 44 bytes, substantive behavior must be understood through `ip_protocol.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_protocol.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 44 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol-Xverbose.c -->
# sources/test-tools/strace/tests/ip_protocol-Xverbose.c

Purpose: Compile-time wrapper for `ip_protocol.c`. It does not implement an independent test body; instead it selects verbose xlat output for IP_PROTOCOL getsockopt decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ip_protocol.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ip_protocol.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ip_protocol.c`.

Dependencies: Depends on `ip_protocol.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 48 bytes, substantive behavior must be understood through `ip_protocol.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ip_protocol.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 48 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol.c -->
# sources/test-tools/strace/tests/ip_protocol.c

Purpose: Tests `getsockopt` decoding for Linux `IP_PROTOCOL`, including known and unknown protocol numbers under injected-success formatting.

Important APIs/types/functions: Uses `getsockopt`, `SOL_IP`, fallback `IP_PROTOCOL`, `socklen_t`, tail-allocated integer buffers, `print_quoted_hex`, and xlat macros.

Control flow: Iterates `IPPROTO_RAW` and an unknown protocol value. For each it tests negative, zero, short, faulting, normal, 5-byte, and 8-byte option lengths, printing either pointer fallback or decoded `[IPPROTO_*]` output.

State/persistence behavior: No socket is created here; fd `0` is used and the file hardcodes `(INJECTED)` in expected output. State is limited to `protocol`, `big_protocol`, and `len`.

Dependencies: Requires socket headers and the strace sockopt decoder. The option number is defined locally when missing.

Integration points: Covers get-only socket option decoding, xlat verbosity behavior for protocol constants, short-buffer hex rendering, and injected-success expected output.

Risks: Without injection the real fd type may influence return codes; the test suite normally controls this through strace fault injection.

Test signals: Lines should show `IPPROTO_RAW`, `IPPROTO_???`, quoted short buffers, `(INJECTED)`, and clean exit.

Source read signal: complete file read for this research pass; file size 109 line(s), 2932 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.c -->
# sources/test-tools/strace/tests/ipc.c

Purpose: Tests decoding of the legacy multiplexed `ipc` syscall and verifies that strace can split selected calls into SysV IPC names such as `semctl` and `msgrcv`.

Important APIs/types/functions: Uses `syscall(__NR_ipc)`, `<linux/ipc.h>`, fallback `SEMCTL` and `MSGRCV` constants, `ipc_call`, `ipc_call0`, `tail_alloc`, and `sprintrc`.

Control flow: Builds an encoded first argument from high garbage bits, IPC version, and call number. It first checks whether a `SEMCTL` call with a faulting pointer is decoded as `semctl`, iterates several raw call numbers with version 0 and 42, then conditionally tests versioned `SEMCTL` and `MSGRCV` output depending on kernel behavior.

State/persistence behavior: Uses faulting pointers and invalid arguments, so no SysV IPC objects are created. All state is local arguments and errno.

Dependencies: Requires `__NR_ipc` and Linux IPC headers; otherwise the file compiles to a skip test. s390 argument count formatting is handled specially.

Integration points: Validates the legacy ipc multiplexer decoder and its version-bit interpretation before per-family SysV IPC tests run.

Risks: The legacy syscall is architecture-specific and unavailable on many targets. Kernel behavior around version encoding determines which branch is printed.

Test signals: Expected output includes raw `ipc(...)` lines, decoded `semctl` EFAULT, optional `msgrcv`, and final exit.

Source read signal: complete file read for this research pass; file size 102 line(s), 2195 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.sh -->
# sources/test-tools/strace/tests/ipc.sh

Purpose: Shell harness for the `ipc` decoder test. It runs the compiled program and compares strace's `-eipc` output against program-generated expectations.

Important APIs/types/functions: Sources `init.sh`, calls `run_prog`, `run_strace -eipc`, writes expected output to `$EXP`, and validates with `match_grep`.

Control flow: The script runs the program once discarding stdout, then runs strace with IPC filtering and any passed arguments, redirects expected output, and greps the strace log against it.

State/persistence behavior: Uses the test framework's temporary `$LOG` and `$EXP` files. It creates no persistent repository state.

Dependencies: Depends on strace test harness shell functions and the compiled `ipc` test executable.

Integration points: Connects the C-side expected-output generator to the strace invocation layer for the legacy IPC multiplexer.

Risks: Harness variables must be initialized by `init.sh`; changing stdout/stderr handling in the C test or framework can break matching.

Test signals: Successful run exits 0 after `match_grep`; mismatches indicate decoder output drift.

Source read signal: complete file read for this research pass; file size 16 line(s), 282 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg-Xabbrev.c -->
# sources/test-tools/strace/tests/ipc_msg-Xabbrev.c

Purpose: Compile-time wrapper for `ipc_msg.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for SysV message queue control decoder coverage.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `ipc_msg.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_msg.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_msg.c`.

Dependencies: Depends on `ipc_msg.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 21 bytes, substantive behavior must be understood through `ipc_msg.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_msg.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 21 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg-Xraw.c -->
# sources/test-tools/strace/tests/ipc_msg-Xraw.c

Purpose: Compile-time wrapper for `ipc_msg.c`. It does not implement an independent test body; instead it selects raw xlat output for SysV message queue control decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ipc_msg.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_msg.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_msg.c`.

Dependencies: Depends on `ipc_msg.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 40 bytes, substantive behavior must be understood through `ipc_msg.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_msg.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 40 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg-Xverbose.c -->
# sources/test-tools/strace/tests/ipc_msg-Xverbose.c

Purpose: Compile-time wrapper for `ipc_msg.c`. It does not implement an independent test body; instead it selects verbose xlat output for SysV message queue control decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ipc_msg.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_msg.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_msg.c`.

Dependencies: Depends on `ipc_msg.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 44 bytes, substantive behavior must be understood through `ipc_msg.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_msg.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 44 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg.c -->
# sources/test-tools/strace/tests/ipc_msg.c

Purpose: Tests SysV message queue syscall decoding for `msgget` and `msgctl` commands, including metadata structures and Linux-specific info/stat commands.

Important APIs/types/functions: Uses `msgget`, `msgctl`, `struct msqid_ds`, `struct msginfo`, `atexit`, `cleanup`, `print_msginfo`, `print_msqid_ds`, and xlat strings for resource flags and IPC/msg commands.

Control flow: It prints a bogus `msgget`, creates a private queue, registers cleanup, optionally tests bogus commands and bogus addresses depending on glibc/version guards, reads and sets `IPC_STAT`/`IPC_SET`, prints `IPC_INFO`, `MSG_INFO`, `MSG_STAT`, and `MSG_STAT_ANY` when available, then cleanup removes the queue.

State/persistence behavior: Creates one private message queue and removes it via `atexit(cleanup)`. State persists only for the test process lifetime; cleanup output is part of expected matching.

Dependencies: Depends on SysV message queue support, glibc behavior guards, `resource_flags` xlat data, and raw/verbose/abbrev macro variants.

Integration points: Validates strace SysV message decoders, regex-friendly expected output via escaped parentheses/braces, IPC_64 optional rendering, time/permission fields, and command xlat modes.

Risks: libc may intercept invalid commands or dereference bogus pointers on some ABIs; the compile-time guards intentionally skip unsafe cases. Kernel limits and permissions may affect info commands.

Test signals: Expected output includes queue creation/removal, decoded permissions, message stats, optional bogus command/address lines, and xlat-mode-specific command names.

Source read signal: complete file read for this research pass; file size 263 line(s), 7690 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf-Xabbrev.c -->
# sources/test-tools/strace/tests/ipc_msgbuf-Xabbrev.c

Purpose: Compile-time wrapper for `ipc_msgbuf.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for SysV message payload decoder coverage.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `ipc_msgbuf.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_msgbuf.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_msgbuf.c`.

Dependencies: Depends on `ipc_msgbuf.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 24 bytes, substantive behavior must be understood through `ipc_msgbuf.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_msgbuf.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 24 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf-Xraw.c -->
# sources/test-tools/strace/tests/ipc_msgbuf-Xraw.c

Purpose: Compile-time wrapper for `ipc_msgbuf.c`. It does not implement an independent test body; instead it selects raw xlat output for SysV message payload decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ipc_msgbuf.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_msgbuf.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_msgbuf.c`.

Dependencies: Depends on `ipc_msgbuf.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 43 bytes, substantive behavior must be understood through `ipc_msgbuf.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_msgbuf.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 43 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf-Xverbose.c -->
# sources/test-tools/strace/tests/ipc_msgbuf-Xverbose.c

Purpose: Compile-time wrapper for `ipc_msgbuf.c`. It does not implement an independent test body; instead it selects verbose xlat output for SysV message payload decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ipc_msgbuf.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_msgbuf.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_msgbuf.c`.

Dependencies: Depends on `ipc_msgbuf.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 47 bytes, substantive behavior must be understood through `ipc_msgbuf.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_msgbuf.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 47 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf.c -->
# sources/test-tools/strace/tests/ipc_msgbuf.c

Purpose: Tests message payload decoding for `msgsnd` and `msgrcv`, including message type, text strings, and receive flags.

Important APIs/types/functions: Uses `msgget`, `msgsnd`, `msgrcv`, `msgctl`, direct syscall support through `scno.h`, fixed `text_string`, `cleanup`, and helper routines around a small message buffer.

Control flow: Creates a private message queue, sends a known string payload, receives it with controlled size/type/flags, prints expected decoded buffer contents, and removes the queue during cleanup.

State/persistence behavior: Creates one SysV message queue and one queued message during the test, both scoped to the process and cleaned up explicitly.

Dependencies: Requires SysV message queues, syscall number support, and strace helpers. Xlat wrappers alter flag rendering.

Integration points: Complements `ipc_msg.c` by exercising message payload buffer decoding rather than only control structures.

Risks: Queue creation can fail under tight IPC limits. Payload string length and NUL handling must match the decoder's quoted-string behavior.

Test signals: Output includes `msgget`, `msgsnd`, `msgrcv` with `STRACE_STRING`, cleanup, and final exit.

Source read signal: complete file read for this research pass; file size 101 line(s), 2521 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xabbrev.c -->
# sources/test-tools/strace/tests/ipc_sem-Xabbrev.c

Purpose: Compile-time wrapper for `ipc_sem.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for SysV semaphore decoder coverage.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `ipc_sem.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_sem.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_sem.c`.

Dependencies: Depends on `ipc_sem.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 21 bytes, substantive behavior must be understood through `ipc_sem.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_sem.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 21 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xraw.c -->
# sources/test-tools/strace/tests/ipc_sem-Xraw.c

Purpose: Compile-time wrapper for `ipc_sem.c`. It does not implement an independent test body; instead it selects raw xlat output for SysV semaphore decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ipc_sem.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_sem.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_sem.c`.

Dependencies: Depends on `ipc_sem.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 40 bytes, substantive behavior must be understood through `ipc_sem.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_sem.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 40 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xverbose.c -->
# sources/test-tools/strace/tests/ipc_sem-Xverbose.c

Purpose: Compile-time wrapper for `ipc_sem.c`. It does not implement an independent test body; instead it selects verbose xlat output for SysV semaphore decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ipc_sem.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_sem.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_sem.c`.

Dependencies: Depends on `ipc_sem.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 44 bytes, substantive behavior must be understood through `ipc_sem.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_sem.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 44 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem.c -->
# sources/test-tools/strace/tests/ipc_sem.c

Purpose: Tests SysV semaphore decoding for `semget` and `semctl`, including semaphore metadata and Linux info/stat commands.

Important APIs/types/functions: Uses `semget`, `semctl`, local `union semun`, `struct semid_ds`, `struct seminfo`, `cleanup`, `print_semid_ds`, `print_sem_info`, and resource flag xlat strings.

Control flow: Prints a bogus `semget`, creates a private semaphore set, registers cleanup, optionally tests a bogus command, prints `IPC_INFO` and `SEM_INFO`, reads `IPC_STAT`, writes `IPC_SET`, and prints `SEM_STAT`. `SEM_STAT_ANY` is intentionally disabled due libc argument-passing bugs noted in comments.

State/persistence behavior: Creates one semaphore set and removes it with `IPC_RMID` through `atexit`. No state should remain after successful exit.

Dependencies: Requires SysV semaphore support, glibc guard behavior for invalid commands, and strace xlat tables for resource flags and IPC command names.

Integration points: Verifies semctl argument decoding across raw/verbose/abbrev xlat modes, optional `IPC_64` rendering, and structure field extraction.

Risks: libc wrappers differ for unsupported commands; semaphore limits can prevent object creation. The disabled `SEM_STAT_ANY` branch documents a known libc interface hazard.

Test signals: Expected output includes bogus and private `semget`, info/stat structures, `IPC_SET`, cleanup line, and no final explicit exit marker in this file.

Source read signal: complete file read for this research pass; file size 241 line(s), 6931 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm-Xabbrev.c -->
# sources/test-tools/strace/tests/ipc_shm-Xabbrev.c

Purpose: Compile-time wrapper for `ipc_shm.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for SysV shared-memory decoder coverage.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `ipc_shm.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_shm.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_shm.c`.

Dependencies: Depends on `ipc_shm.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 21 bytes, substantive behavior must be understood through `ipc_shm.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_shm.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 21 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm-Xraw.c -->
# sources/test-tools/strace/tests/ipc_shm-Xraw.c

Purpose: Compile-time wrapper for `ipc_shm.c`. It does not implement an independent test body; instead it selects raw xlat output for SysV shared-memory decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ipc_shm.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_shm.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_shm.c`.

Dependencies: Depends on `ipc_shm.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 40 bytes, substantive behavior must be understood through `ipc_shm.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_shm.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 40 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm-Xverbose.c -->
# sources/test-tools/strace/tests/ipc_shm-Xverbose.c

Purpose: Compile-time wrapper for `ipc_shm.c`. It does not implement an independent test body; instead it selects verbose xlat output for SysV shared-memory decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `ipc_shm.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_shm.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_shm.c`.

Dependencies: Depends on `ipc_shm.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 44 bytes, substantive behavior must be understood through `ipc_shm.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_shm.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 44 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm.c -->
# sources/test-tools/strace/tests/ipc_shm.c

Purpose: Tests SysV shared-memory decoding for `shmget` and `shmctl`, including huge-page flags, metadata structures, attach/detach fields, and Linux info/stat commands.

Important APIs/types/functions: Uses `shmget`, `shmctl`, `struct shmid_ds`, `struct shm_info`, `struct shminfo`, cleanup with `IPC_RMID`, xlat table `shm_resource_flags`, and helpers that print decoded structures.

Control flow: Builds bogus keys/flags including `SHM_HUGETLB`, `SHM_NORESERVE`, and huge-page shift bits, creates a private shared-memory segment, conditionally checks bogus command/address behavior, prints IPC/stat/info variants, updates permissions through `IPC_SET`, and removes the segment during cleanup.

State/persistence behavior: Creates one SysV shared-memory segment and removes it with `atexit(cleanup)`. No persistent memory object should remain after a normal run.

Dependencies: Requires SysV shared memory, UAPI flag availability with local fallbacks, glibc-version guards, and xlat data for shared-memory resource flags.

Integration points: Validates strace formatting of shared-memory flags, huge-page expressions, permission/time fields, process ids, attachment counts, and command xlat modes.

Risks: libc invalid-command behavior varies; system IPC limits or permissions can skip/fail setup. Huge-page flag formatting is easy to regress because it mixes named bits with shifted size encodings.

Test signals: Expected output includes bogus `shmget`, private segment id, decoded `shmctl` structures, cleanup, and xlat-mode-specific command rendering.

Source read signal: complete file read for this research pass; file size 323 line(s), 9494 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/is_linux_mips_n64.c -->
# sources/test-tools/strace/tests/is_linux_mips_n64.c

Purpose: Minimal architecture probe used by the strace testsuite to report whether the current build is Linux MIPS n64.

Important APIs/types/functions: Uses preprocessor architecture checks, `printf`, and `SKIP_MAIN_UNDEFINED("MIPS")` for non-MIPS builds.

Control flow: On MIPS it prints a true/false style result based on ABI macros; on non-MIPS it compiles to a skip test.

State/persistence behavior: No runtime state beyond stdout.

Dependencies: Compiler-defined MIPS ABI macros and the strace test framework.

Integration points: Provides a small feature probe for tests that need MIPS n64-specific expectations.

Risks: Toolchain macro naming changes could misclassify the ABI.

Test signals: A simple printed result on MIPS or skip on other architectures.

Source read signal: complete file read for this research pass; file size 25 line(s), 368 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/is_linux_mips_n64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.c -->
# sources/test-tools/strace/tests/k_sockopt.c

Purpose: Tests raw kernel socket option syscall entry points by invoking architecture-specific syscall numbers for `getsockopt` and `setsockopt`.

Important APIs/types/functions: Uses `syscall`, `__NR_socketcall`-style numbering abstractions from `scno.h`, constants `SC_getsockopt` and `SC_setsockopt`, `fill`/`bad` kernel_ulong fixtures, and shared declarations from `k_sockopt.h`.

Control flow: Builds deliberately malformed scalar and pointer arguments, invokes the raw get/set sockopt syscall forms, and prints expected formatting for level, optname, optval, optlen, and return code.

State/persistence behavior: No real socket state is created; bogus descriptors and pointers drive failure-path decoding.

Dependencies: Depends on kernel syscall ABI availability for direct socket options and the companion header for function prototypes/macros.

Integration points: Covers lower-level socket option syscall decoding separate from libc `getsockopt`/`setsockopt` wrappers.

Risks: Socketcall multiplexing differs by architecture, and direct syscall numbers may be unavailable on some targets.

Test signals: Expected output is a compact set of failed raw sockopt syscall lines.

Source read signal: complete file read for this research pass; file size 61 line(s), 1407 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.h -->
# sources/test-tools/strace/tests/k_sockopt.h

Purpose: Shared header for kernel socket option tests.

Important APIs/types/functions: Declares the shared testing interface and constants consumed by `k_sockopt.c` without pulling in unrelated test logic.

Control flow: Header-only file; there is no runtime control flow. It is included by the C test at compile time.

State/persistence behavior: No runtime state. Any state is in constants/macros compiled into including tests.

Dependencies: Coupled to the strace test framework and raw socket option syscall tests.

Integration points: Keeps declarations in one place for raw kernel socket option coverage.

Risks: Prototype drift between header and C file would cause build failures or wrong syscall argument types.

Test signals: Successful compilation of `k_sockopt.c` is the primary signal.

Source read signal: complete file read for this research pass; file size 24 line(s), 684 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/k_sockopt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp-y--pidns-translation.c -->
# sources/test-tools/strace/tests/kcmp-y--pidns-translation.c

Purpose: Compile-time wrapper for `kcmp-y.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, PID namespace translation for verbose-fd kcmp decoder coverage.

Important APIs/types/functions: The wrapper contributes `PIDNS_TRANSLATION`=#include "kcmp-y.c" and then includes `kcmp-y.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `kcmp-y.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `kcmp-y.c`.

Dependencies: Depends on `kcmp-y.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 46 bytes, substantive behavior must be understood through `kcmp-y.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `kcmp-y.c` under abbreviated/default xlat output, PID namespace translation. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 46 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp-y--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp-y.c -->
# sources/test-tools/strace/tests/kcmp-y.c

Purpose: Compile-time wrapper for `kcmp.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for kcmp syscall decoder coverage.

Important APIs/types/functions: The wrapper contributes `VERBOSE_FD`=1, `SKIP_IF_PROC_IS_UNAVAILABLE`=skip_if_unavailable("/proc/self/fd/") and then includes `kcmp.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `kcmp.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `kcmp.c`.

Dependencies: Depends on `kcmp.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 4 line(s) and 114 bytes, substantive behavior must be understood through `kcmp.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `kcmp.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 4 line(s), 114 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp.c -->
# sources/test-tools/strace/tests/kcmp.c

Purpose: Tests decoding of the `kcmp` syscall, including PID arguments, comparison types, fd arguments, and `KCMP_EPOLL_TFD` pointer decoding.

Important APIs/types/functions: Uses `syscall(__NR_kcmp)`, `open`, `dup2`, `close`, `struct kcmp_epoll_slot`, `PIDNS_TEST_INIT`, `pidns_pid2str`, `printpidfd`, and `do_kcmp`.

Control flow: Opens `/dev/null` and `/dev/zero` into stable fds 23 and 42, closes fd 0, runs invalid type/pid cases, tests `KCMP_FILE` with bogus and real fds, prints all simple `KCMP_*` types, and tests `KCMP_EPOLL_TFD` with NULL/faulting pointers plus three filled slot structures.

State/persistence behavior: Process-local file descriptors are opened and duplicated. No persistent filesystem state is modified.

Dependencies: Requires `__NR_kcmp`, Linux `kcmp.h`, pid namespace helpers, and optionally `/proc/self/fd/` for verbose fd-path wrappers.

Integration points: Validates strace's kcmp decoder, fd path annotation in verbose mode, pid namespace translation, optional pointer decoding for epoll slots, and unknown-type fallback.

Risks: Kernel permission restrictions can change errno. `/dev/null`, `/dev/zero`, and `/proc/self/fd/` availability affect wrapper variants.

Test signals: Output includes invalid fallback, all known comparison type names, decoded fd paths when verbose wrapper is used, epoll slot structures, pidns prefixes, and final exit.

Source read signal: complete file read for this research pass; file size 209 line(s), 5140 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kern_features.c -->
# sources/test-tools/strace/tests/kern_features.c

Purpose: Tests decoding of the SPARC-specific `kern_features` syscall and its feature-bit return value.

Important APIs/types/functions: Uses `raw_syscall_0(__NR_kern_features, &err)`, `test_kern_features`, `KERN_FEATURE_MIXED_MODE_STACK` expected strings, fault-injected return values, and `SKIP_MAIN_UNDEFINED`.

Control flow: For each requested injected return number, the helper performs the raw syscall, prints either an errno failure or a decoded bitmask selected from a table of expected return values.

State/persistence behavior: No persistent state; the syscall is a feature query and the test only formats return values.

Dependencies: Requires SPARC syscall availability and raw syscall helper support. The test is skipped elsewhere.

Integration points: Validates return-value decoding rather than argument decoding, which is a distinct strace path.

Risks: Feature bits can grow beyond the single named bit used here. Raw syscall calling conventions differ by architecture.

Test signals: Output maps injected return values to `KERN_FEATURE_MIXED_MODE_STACK` plus unknown-bit fallbacks or skips when unsupported.

Source read signal: complete file read for this research pass; file size 99 line(s), 2030 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kern_features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timespec.h -->
# sources/test-tools/strace/tests/kernel_old_timespec.h

Purpose: Compatibility header defining the old Linux kernel `timespec` layout used by strace tests that need pre-time64 ABI structures.

Important APIs/types/functions: Provides a small kernel-facing structure definition with old-width seconds/nanoseconds fields. It is a header-only artifact and exports no functions.

Control flow: There is no runtime control flow. Including C tests use the type at compile time to build syscall or ioctl argument fixtures.

State/persistence behavior: No state is stored. The header only affects compiled structure layout.

Dependencies: Coupled to strace's compatibility type conventions and tests that must be independent of host libc's modern `struct timespec`.

Integration points: Used by time ABI tests to keep expected output stable across 32-bit, 64-bit, and time64-capable hosts.

Risks: Field-width mistakes would make tests validate the wrong ABI layout. Because it intentionally models an old kernel ABI, replacing it with libc `timespec` would be incorrect.

Test signals: Successful compilation of dependent tests and stable old-timespec field decoding.

Source read signal: complete file read for this research pass; file size 20 line(s), 406 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timespec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timex.h -->
# sources/test-tools/strace/tests/kernel_old_timex.h

Purpose: Compatibility header defining the old Linux kernel `timex`-related layout needed by strace tests for legacy time adjustment ABIs.

Important APIs/types/functions: Provides header-only type definitions for old-kernel time fields. It exports no runtime functions.

Control flow: No runtime control flow; including tests instantiate the compatibility structure and pass it to syscall decoders.

State/persistence behavior: No persistent or runtime state. The header controls compile-time data layout only.

Dependencies: Depends on strace's kernel compatibility type strategy and consumers that require old time ABI layouts instead of host libc definitions.

Integration points: Supports time/timex syscall tests where decoder correctness depends on exact old-kernel field order and widths.

Risks: Any mismatch with the kernel ABI produces false confidence in decoder tests. Host header substitution would make cross-architecture output unstable.

Test signals: Dependent tests compile and print old-timex fields consistently.

Source read signal: complete file read for this research pass; file size 25 line(s), 530 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_old_timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xabbrev.c -->
# sources/test-tools/strace/tests/kernel_version-Xabbrev.c

Purpose: Compile-time wrapper for `kernel_version.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for BPF/kernel-version formatting coverage.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `kernel_version.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `kernel_version.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `kernel_version.c`.

Dependencies: Depends on `kernel_version.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 28 bytes, substantive behavior must be understood through `kernel_version.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `kernel_version.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 28 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xraw.c -->
# sources/test-tools/strace/tests/kernel_version-Xraw.c

Purpose: Compile-time wrapper for `kernel_version.c`. It does not implement an independent test body; instead it selects raw xlat output for BPF/kernel-version formatting coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `kernel_version.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `kernel_version.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `kernel_version.c`.

Dependencies: Depends on `kernel_version.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 47 bytes, substantive behavior must be understood through `kernel_version.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `kernel_version.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 47 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xverbose.c -->
# sources/test-tools/strace/tests/kernel_version-Xverbose.c

Purpose: Compile-time wrapper for `kernel_version.c`. It does not implement an independent test body; instead it selects verbose xlat output for BPF/kernel-version formatting coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `kernel_version.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `kernel_version.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `kernel_version.c`.

Dependencies: Depends on `kernel_version.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 51 bytes, substantive behavior must be understood through `kernel_version.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `kernel_version.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 51 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version.c -->
# sources/test-tools/strace/tests/kernel_version.c

Purpose: Tests strace's `KERNEL_VERSION(a,b,c)` formatting by using BPF syscall attributes that carry kernel-version fields.

Important APIs/types/functions: Uses `syscall(__NR_bpf)`, `union bpf_attr`, `print_bpf_attr`, `bpf_commands` xlat, `PRINT_FIELD_U`, and `sprintrc`.

Control flow: Fills a BPF program-load attribute with deterministic values, varies the command and kernel version fields, invokes the syscall, and prints expected decoded BPF attributes including kernel version representation.

State/persistence behavior: Syscalls are expected to fail; no BPF programs persist. State is the local `bpf_attr` buffer and global `errstr`.

Dependencies: Requires `__NR_bpf`, strace BPF attribute compatibility headers, and xlat mode wrappers.

Integration points: Exercises generic kernel-version pretty-printer through a real syscall decoder path.

Risks: BPF UAPI field layout and validation can change, though failed-call formatting should remain stable.

Test signals: Lines show BPF command xlat, decoded `kern_version=KERNEL_VERSION(...)` or raw variants, errors, and final exit.

Source read signal: complete file read for this research pass; file size 115 line(s), 2289 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_file_load.c -->
# sources/test-tools/strace/tests/kexec_file_load.c

Purpose: Tests decoding of `kexec_file_load`, including fd arguments, command-line pointer/length combinations, and file-load flags.

Important APIs/types/functions: Uses `syscall(__NR_kexec_file_load)`, local `struct strval`, command-line buffers from `tail_memdup`, `snprintf`, and flag strings for `KEXEC_FILE_*`.

Control flow: Iterates three flag cases and seven command-line pointer/length cases, including NULL, faulting end pointer, truncated long strings, exact NUL-inclusive and NUL-exclusive short strings, and overlong lengths. Each call prints fd truncation, length, command-line rendering, flags, and return code.

State/persistence behavior: No kernel image is loaded because bogus fds and permissions make calls fail. Memory buffers are local.

Dependencies: Requires `__NR_kexec_file_load`; otherwise skipped. Pointer-width conditionals control high-bit flag printing.

Integration points: Validates strace string argument decoding with explicit length, fd scalar rendering, and kexec file flag xlat.

Risks: Privilege-sensitive syscall must stay in failure path. Pointer width changes affect expected flag prefixes.

Test signals: Matrix of `kexec_file_load(...)` lines with quoted command lines, NULL/pointer fallbacks, flag names, and clean exit.

Source read signal: complete file read for this research pass; file size 107 line(s), 2949 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_file_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_load.c -->
# sources/test-tools/strace/tests/kexec_load.c

Purpose: Tests decoding of the older `kexec_load` syscall, especially segment-array truncation and architecture/operation flags.

Important APIs/types/functions: Uses `syscall(__NR_kexec_load)`, local `struct segm`, `tail_alloc`, `fill_memory`, and `struct strval` flag fixtures.

Control flow: Allocates seventeen segment descriptors, fills them with deterministic data, then issues calls for NULL/zero arguments, bogus segment pointers, full arrays, arrays that should be truncated with ellipsis, tail subarrays, and multiple flag combinations.

State/persistence behavior: Bogus entry points, segment pointers, and missing privilege keep the syscall from loading a kernel. Only local memory is modified.

Dependencies: Requires syscall number availability, pointer-size conditionals, and kexec flag constants in strace expectations.

Integration points: Validates array-of-struct decoding, ellipsis and fault-pointer annotations, kexec architecture flag printing, and scalar argument formatting.

Risks: Segment count truncation rules are easy to regress. As with all kexec tests, accidental success would be dangerous, so bogus inputs are essential.

Test signals: Output includes NULL case, raw pointer cases, decoded segment arrays with `...`, named kexec flags, and final exit.

Source read signal: complete file read for this research pass; file size 142 line(s), 4554 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl-Xabbrev.c -->
# sources/test-tools/strace/tests/keyctl-Xabbrev.c

Purpose: Compile-time wrapper for `keyctl.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output for keyctl syscall decoder coverage for commands, key ids, strings, buffers, capabilities, DH/KDF parameters, and xlat modes.

Important APIs/types/functions: The wrapper contributes no local macro definitions and then includes `keyctl.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `keyctl.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `keyctl.c`.

Dependencies: Depends on `keyctl.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 1 line(s) and 20 bytes, substantive behavior must be understood through `keyctl.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `keyctl.c` under abbreviated/default xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 1 line(s), 20 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl-Xraw.c -->
# sources/test-tools/strace/tests/keyctl-Xraw.c

Purpose: Compile-time wrapper for `keyctl.c`. It does not implement an independent test body; instead it selects raw xlat output for keyctl syscall decoder coverage for commands, key ids, strings, buffers, capabilities, DH/KDF parameters, and xlat modes.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `keyctl.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `keyctl.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `keyctl.c`.

Dependencies: Depends on `keyctl.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 39 bytes, substantive behavior must be understood through `keyctl.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `keyctl.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 39 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl-Xverbose.c -->
# sources/test-tools/strace/tests/keyctl-Xverbose.c

Purpose: Compile-time wrapper for `keyctl.c`. It does not implement an independent test body; instead it selects verbose xlat output for keyctl syscall decoder coverage for commands, key ids, strings, buffers, capabilities, DH/KDF parameters, and xlat modes.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `keyctl.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `keyctl.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `keyctl.c`.

Dependencies: Depends on `keyctl.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 43 bytes, substantive behavior must be understood through `keyctl.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `keyctl.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 43 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/keyctl-Xverbose.c -->
