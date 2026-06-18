# subset-b-009349 research

Grouped research report for strace io_uring and ioctl decoder tests under `sources/test-tools/strace/tests`. Every listed source file was read in full enough to classify either the primary implementation body or its macro/include wrapper. Sections preserve exact source paths for reconciliation into mirrored per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register.c -->
# sources/test-tools/strace/tests/io_uring_register.c

Purpose: `io_uring_register.c` exercises strace decoding of the io_uring_register syscall across old and current registration opcodes. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_io_uring_register, struct iovec, io_uring_probe, io_uring_restriction, io_uring_rsrc_register, io_uring_files_update, io_uring_buf_reg, io_uring_sync_cancel_reg, io_uring_file_index_range, io_uring_napi, io_uring_clock_register, io_uring_clone_buffers, io_uring_send_msg_ring, io_uring_region_desc, io_uring_query_hdr, and zero-copy RX control/query structures from linux/io_uring.h and linux/io_uring/query.h. Local include directives/macros observed in this source are `tests.h, scno.h, fcntl.h, inttypes.h, stdio.h, string.h, sys/socket.h, unistd.h, kernel_time_types.h, linux/io_uring.h, linux/io_uring/query.h` and `UAPI_LINUX_IO_URING_H_SKIP_LINUX_TIME_TYPES_H=#include <linux/io_uring.h>, ARR_ITEM=(arr_, idx_) ((arr_)[(idx_) % ARRAY_SIZE(arr_)])`. Locally visible function entry points include `sys_io_uring_register, print_rsrc_data, print_rsrc_tags, test_IORING_REGISTER_BUFFERS, test_IORING_REGISTER_FILES, test_IORING_REGISTER_FILES_UPDATE, test_IORING_REGISTER_PROBE, test_IORING_REGISTER_RESTRICTIONS, test_IORING_REGISTER_FILES2_BUFFERS2, test_IORING_REGISTER_FILES_UPDATE2_BUFFERS_UPDATE, test_IORING_REGISTER_IOWQ_AFF, test_IORING_REGISTER_IOWQ_MAX_WORKERS, test_IORING_REGISTER_RING_FDS, test_IORING_REGISTER_PBUF_RING, test_IORING_REGISTER_SYNC_CANCEL, test_IORING_REGISTER_FILE_ALLOC_RANGE, test_IORING_REGISTER_PBUF_STATUS, test_IORING_REGISTER_NAPI`.

Control flow: main opens /dev/null and /dev/full, builds tail-allocated valid and invalid argument objects, emits invalid opcode and no-argument opcode cases, then calls dedicated test_IORING_REGISTER_* helpers for buffers/files, resource tags, probes, restrictions, IOWQ, ring fds, pbuf rings, sync cancel, NAPI, clock, clone/send-message rings, ZCRX, resize, memory regions, and query chains. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `io_uring_register.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistent state; only process-local file descriptors, tail-allocated buffers, generated pointers, and the global errstr buffer. Success-injected builds add (INJECTED) to expected return strings and expose output-side structure decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, kernel_time_types.h, linux/io_uring.h, linux/io_uring/query.h, /proc/self/fd, /dev/null, /dev/full, tail_alloc helpers, fill_memory helpers, XLAT formatting macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: high churn in io_uring UAPI opcode numbers and structure layouts, architecture-dependent pointer widening through BIG_ADDR_MASK, truncation around DEFAULT_STRLEN, and different xlat rendering modes can all break expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected signal is exact stdout matching under strace for invalid pointers, known/unknown opcode names, fd path annotation, nested linked query truncation, reserved fields, and injected-return variants. This file has 2951 source lines and 103672 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/io_uring_register.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_setup.c -->
# sources/test-tools/strace/tests/io_uring_setup.c

Purpose: `io_uring_setup.c` checks strace decoding of the io_uring_setup syscall and struct io_uring_params. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_io_uring_setup, struct io_uring_params, sq_off/cq_off nested offsets, IORING_SETUP_* flags, IORING_FEAT_* feature flags. Local include directives/macros observed in this source are `tests.h, scno.h, fcntl.h, stdio.h, stdint.h, string.h, unistd.h, kernel_time_types.h, linux/io_uring.h, sys/stat.h, sys/types.h, print_fields.h` and `UAPI_LINUX_IO_URING_H_SKIP_LINUX_TIME_TYPES_H=#include <linux/io_uring.h>`. Locally visible function entry points include `sys_io_uring_setup, main`.

Control flow: sys_io_uring_setup wraps the raw syscall with poisoned upper arguments. main tests NULL, bad pointer, all-flags/reserved-field input, then zeroed normal parameter blocks with and without IORING_SETUP_ATTACH_WQ referencing /dev/full. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `io_uring_setup.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr records each syscall result and kernel-mutated params are printed only when setup succeeds. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/io_uring.h, kernel_time_types.h, print_fields.h, xlat/uring_setup_features.h, /proc/self/fd, /dev/full. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel/header drift for newly added setup flags, success path differences on hosts that allow io_uring_setup, and fd-path annotation dependence. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout verifies flag decoding, reserved arrays, wq_fd path display, anon_inode return rendering, and fallback pointer printing on failure. This file has 148 source lines and 4433 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/io_uring_setup.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-success.sh -->
# sources/test-tools/strace/tests/ioctl-success.sh

Purpose: `ioctl-success.sh` shell harness for ioctl decoder tests that need a successful ioctl via strace syscall injection. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are scno_tampering.sh, run_strace, match_diff, skip_, fail_, IOCTL_INJECT_START, IOCTL_INJECT_RETVAL, strace -e inject=ioctl:retval=...:when=... . Local include directives/macros observed in this source are `none in wrapper; inherited through included implementation` and `implementation defaults`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sources the common shell helper, sanity-runs ../$NAME expecting failure or skip, reruns it under strace with ioctl injection starting at the configured call number, captures expected output from the test binary, filters noisy early fd ioctl lines from the strace log, then diffs. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl-success.sh` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: persists only temporary harness outputs $EXP and $OUT; behavior is driven by environment variables and the selected binary name. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: test harness variables NAME, LOG, EXP, OUT, srcdir; executable under ../$NAME must accept skip count and injected retval arguments. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: brittle if the binary cannot lock onto the injected call, if fd setup emits extra ioctl lines outside the filter, or if the configured injection start is stale. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is match_diff equality between filtered strace output and the binary-generated expectation. This file has 31 source lines and 786 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl-success.sh_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-success.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-v.c -->
# sources/test-tools/strace/tests/ioctl-v.c

Purpose: `ioctl-v.c` generic verbose ioctl payload test for _IOC read/write direction and data-size decoding. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, _IOC, _IOR, _IOW, _IOWR, RVAL_EBADF, kernel_ulong_t. Local include directives/macros observed in this source are `tests.h, stdio.h, unistd.h, sys/ioctl.h` and `implementation defaults`. Locally visible function entry points include `main`.

Control flow: main uses an eight-byte byte array and issues zero-size read/write commands, read, write, bidirectional, _IOC_NONE-with-size, and bad-pointer cases, printing the exact verbose data representation expected from strace. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl-v.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local array contents are fixed and reused for expected input/output strings. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, sys/ioctl.h, unistd.h, stdio.h. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: depends on strace -v style data printing, _IOC encoding width, and correct handling of bad pointer versus readable local array. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout should show quoted byte strings for readable arguments and raw %#lx for invalid pointers. This file has 58 source lines and 1818 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl.c -->
# sources/test-tools/strace/tests/ioctl.c

Purpose: `ioctl.c` broad smoke test for ioctl command-number decoding across multiple Linux subsystems. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, TCGETS, MMTIMER_GETRES, VIDIOC_ENUMINPUT, HIDIOCGVERSION, HIDIOCGPHYS, EVIOCGBIT, mixer/MTD overlap, raw _IOC commands, ZFS_IOC_* aliases, BLKZNAME, KSTAT_IOC_CHAIN_ID. Local include directives/macros observed in this source are `tests.h, fcntl.h, stdio.h, stdint.h, unistd.h, termios.h, sys/ioctl.h, linux/hiddev.h, linux/input.h, linux/mmtimer.h, linux/videodev2.h` and `implementation defaults`. Locally visible function entry points include `main`.

Control flow: main issues ioctl calls on fd -1 against representative command numbers and prints the symbolic or fallback command form expected from strace. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local uint64_t and optional termios struct only supply stable pointers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, termios.h, sys/ioctl.h, linux/hiddev.h, linux/input.h, linux/mmtimer.h, linux/videodev2.h; TCGETS is skipped on POWERPC. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: alias collisions are intentional and can drift with headers; architecture-specific termios encoding and new command tables can alter printed names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact EBADF lines with expected aliases and generic _IOC fallback formatting. This file has 76 source lines and 2052 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_block--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_block--pidns-translation.c

Purpose: `ioctl_block--pidns-translation.c` block-device ioctl decoder test including scalar, pointer, partition, trace setup, and pid namespace translation cases. Wrapper chain: ioctl_block--pidns-translation.c -> ioctl_block.c. Variant effect: PIDNS_TRANSLATION enables pid namespace leader/pid translation expectations.

Important APIs/types/functions: Primary APIs and data surfaces are BLKBSZGET, BLKBSZSET, BLKPG, BLKDISCARD, BLKSECDISCARD, BLKZEROOUT, BLKTRACESETUP, BLKRRPART, BLKFLSBUF, BLKTRACESTART, BLKTRACESTOP, BLKTRACETEARDOWN, struct blkpg_ioctl_arg, blkpg_partition, blk_user_trace_setup. Local include directives/macros observed in this source are `ioctl_block.c` and `PIDNS_TRANSLATION=#include "ioctl_block.c"`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: PIDNS_TEST_INIT sets namespace context, TEST_NULL_ARG emits NULL cases, then main prints scalar settings, int pointer settings, uint64 pairs, BLKPG resize/add partition payloads, BLKTRACESETUP with getpid, argless commands through xlat_data, and an unknown 0x12 ioctl. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_block.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistent state; pidns helpers affect printed leader and pid translation text, tail allocations provide stable payload addresses. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, pidns.h, linux/fs.h, linux/blkpg.h, linux/blkzoned.h, linux/blktrace_api.h, xlat.h. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: pid namespace text is environment-sensitive, block UAPI structures may vary, and argless command classification must stay aligned with strace decoders. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers NULL handling, decoded arrays/structs, pid translation suffix, command names, and unknown _IOC fallback. This file has 3 source lines and 51 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_block--pidns-translation.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_block--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_block.c -->
# sources/test-tools/strace/tests/ioctl_block.c

Purpose: `ioctl_block.c` block-device ioctl decoder test including scalar, pointer, partition, trace setup, and pid namespace translation cases. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are BLKBSZGET, BLKBSZSET, BLKPG, BLKDISCARD, BLKSECDISCARD, BLKZEROOUT, BLKTRACESETUP, BLKRRPART, BLKFLSBUF, BLKTRACESTART, BLKTRACESTOP, BLKTRACETEARDOWN, struct blkpg_ioctl_arg, blkpg_partition, blk_user_trace_setup. Local include directives/macros observed in this source are `tests.h, pidns.h, errno.h, unistd.h, inttypes.h, stdio.h, string.h, sys/ioctl.h, linux/fs.h, linux/blkpg.h, linux/blkzoned.h, linux/blktrace_api.h` and `TEST_NULL_ARG=(cmd)						\`. Locally visible function entry points include `main`.

Control flow: PIDNS_TEST_INIT sets namespace context, TEST_NULL_ARG emits NULL cases, then main prints scalar settings, int pointer settings, uint64 pairs, BLKPG resize/add partition payloads, BLKTRACESETUP with getpid, argless commands through xlat_data, and an unknown 0x12 ioctl. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_block.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistent state; pidns helpers affect printed leader and pid translation text, tail allocations provide stable payload addresses. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, pidns.h, linux/fs.h, linux/blkpg.h, linux/blkzoned.h, linux/blktrace_api.h, xlat.h. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: pid namespace text is environment-sensitive, block UAPI structures may vary, and argless command classification must stay aligned with strace decoders. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers NULL handling, decoded arrays/structs, pid translation suffix, command names, and unknown _IOC fallback. This file has 171 source lines and 4922 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_block.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c

Purpose: `ioctl_counter-Xabbrev.c` COUNTER_* ioctl decoder test for Linux counter watch management and unknown counter command numbers. Wrapper chain: ioctl_counter-Xabbrev.c -> ioctl_counter.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, COUNTER_ADD_WATCH_IOCTL, COUNTER_ENABLE_EVENTS_IOCTL, COUNTER_DISABLE_EVENTS_IOCTL, struct counter_watch, counter component/scope/event enums, _IOC. Local include directives/macros observed in this source are `ioctl_counter.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main iterates all ioctl directions and sizes for unknown counter commands, then checks NULL, bad pointer, known watch, mixed known watch, unknown enum watch, and enable/disable no-argument commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_counter.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr captures each EBADF result and one tail-allocated counter_watch is mutated for cases. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/ioctl.h, linux/counter.h, XLAT_* mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: counter enum additions, platform _IOC type differences, and xlat raw/verbose/abbrev rendering changes affect expectations. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout validates command-number formatting, enum known/unknown rendering, bad pointer handling, and no-argument command decoding. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_counter-Xraw.c

Purpose: `ioctl_counter-Xraw.c` COUNTER_* ioctl decoder test for Linux counter watch management and unknown counter command numbers. Wrapper chain: ioctl_counter-Xraw.c -> ioctl_counter.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, COUNTER_ADD_WATCH_IOCTL, COUNTER_ENABLE_EVENTS_IOCTL, COUNTER_DISABLE_EVENTS_IOCTL, struct counter_watch, counter component/scope/event enums, _IOC. Local include directives/macros observed in this source are `ioctl_counter.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main iterates all ioctl directions and sizes for unknown counter commands, then checks NULL, bad pointer, known watch, mixed known watch, unknown enum watch, and enable/disable no-argument commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_counter.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr captures each EBADF result and one tail-allocated counter_watch is mutated for cases. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/ioctl.h, linux/counter.h, XLAT_* mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: counter enum additions, platform _IOC type differences, and xlat raw/verbose/abbrev rendering changes affect expectations. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout validates command-number formatting, enum known/unknown rendering, bad pointer handling, and no-argument command decoding. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_counter-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_counter-Xverbose.c

Purpose: `ioctl_counter-Xverbose.c` COUNTER_* ioctl decoder test for Linux counter watch management and unknown counter command numbers. Wrapper chain: ioctl_counter-Xverbose.c -> ioctl_counter.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, COUNTER_ADD_WATCH_IOCTL, COUNTER_ENABLE_EVENTS_IOCTL, COUNTER_DISABLE_EVENTS_IOCTL, struct counter_watch, counter component/scope/event enums, _IOC. Local include directives/macros observed in this source are `ioctl_counter.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main iterates all ioctl directions and sizes for unknown counter commands, then checks NULL, bad pointer, known watch, mixed known watch, unknown enum watch, and enable/disable no-argument commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_counter.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr captures each EBADF result and one tail-allocated counter_watch is mutated for cases. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/ioctl.h, linux/counter.h, XLAT_* mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: counter enum additions, platform _IOC type differences, and xlat raw/verbose/abbrev rendering changes affect expectations. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout validates command-number formatting, enum known/unknown rendering, bad pointer handling, and no-argument command decoding. This file has 3 source lines and 50 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_counter-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter.c -->
# sources/test-tools/strace/tests/ioctl_counter.c

Purpose: `ioctl_counter.c` COUNTER_* ioctl decoder test for Linux counter watch management and unknown counter command numbers. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, COUNTER_ADD_WATCH_IOCTL, COUNTER_ENABLE_EVENTS_IOCTL, COUNTER_DISABLE_EVENTS_IOCTL, struct counter_watch, counter component/scope/event enums, _IOC. Local include directives/macros observed in this source are `tests.h, scno.h, errno.h, inttypes.h, stdio.h, stdlib.h, string.h, unistd.h, linux/ioctl.h, linux/counter.h` and `implementation defaults`. Locally visible function entry points include `sys_ioctl, main`.

Control flow: main iterates all ioctl directions and sizes for unknown counter commands, then checks NULL, bad pointer, known watch, mixed known watch, unknown enum watch, and enable/disable no-argument commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_counter.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr captures each EBADF result and one tail-allocated counter_watch is mutated for cases. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/ioctl.h, linux/counter.h, XLAT_* mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: counter enum additions, platform _IOC type differences, and xlat raw/verbose/abbrev rendering changes affect expectations. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout validates command-number formatting, enum known/unknown rendering, bad pointer handling, and no-argument command decoding. This file has 132 source lines and 3842 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_counter.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_dm-v.c -->
# sources/test-tools/strace/tests/ioctl_dm-v.c

Purpose: `ioctl_dm-v.c` large device-mapper DM_* ioctl decoder test covering header validation, nested target specs/messages, strings, flags, and verbose truncation. Wrapper chain: ioctl_dm-v.c -> ioctl_dm.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are DM_VERSION, DM_REMOVE_ALL, DM_LIST_DEVICES, DM_LIST_VERSIONS, DM_DEV_CREATE/REMOVE/STATUS/WAIT/SUSPEND/ARM_POLL/SET_GEOMETRY/RENAME, DM_TABLE_CLEAR/DEPS/STATUS/LOAD, DM_TARGET_MSG, struct dm_ioctl, dm_target_spec, dm_target_msg. Local include directives/macros observed in this source are `ioctl_dm.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: helper init_s seeds dm_ioctl headers and init_dm_target_spec builds deterministic targets. main exercises invalid operations, unsupported ABI versions, short data sizes, unterminated names/uuids, flag decoding, nodev/dev commands, table-load target walking, invalid data_start/next values, target messages, geometry strings, rename strings, and final overlarge target_count. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_dm.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: uses global struct s plus tail-allocated dm_ioctl layouts; no persistent state. VERBOSE controls whether nested target/message/string payloads are expanded or replaced with ellipses. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/dm-ioctl.h, sys/ioctl.h, alignment macros, str129 fixture string, VERBOSE macro. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: DM UAPI layout/flag drift, alignment assumptions, max string length truncation, and verbose/non-verbose split can break expected text. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact EBADF output checks header field selection, flag xlat expansion, safe traversal of nested variable-length data, inaccessible pointer reporting, and verbose ellipsis behavior. This file has 3 source lines and 40 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_dm-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_dm-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_dm.c -->
# sources/test-tools/strace/tests/ioctl_dm.c

Purpose: `ioctl_dm.c` large device-mapper DM_* ioctl decoder test covering header validation, nested target specs/messages, strings, flags, and verbose truncation. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are DM_VERSION, DM_REMOVE_ALL, DM_LIST_DEVICES, DM_LIST_VERSIONS, DM_DEV_CREATE/REMOVE/STATUS/WAIT/SUSPEND/ARM_POLL/SET_GEOMETRY/RENAME, DM_TABLE_CLEAR/DEPS/STATUS/LOAD, DM_TARGET_MSG, struct dm_ioctl, dm_target_spec, dm_target_msg. Local include directives/macros observed in this source are `tests.h, errno.h, inttypes.h, stdio.h, stddef.h, string.h, sys/ioctl.h, linux/ioctl.h, linux/dm-ioctl.h` and `STR32="AbCdEfGhIjKlMnOpQrStUvWxYz012345", ALIGNED_SIZE=(s_, t_) \, ALIGNED_OFFSET=(t_, m_) \, FILL_DM_TARGET=(id, id_next) \, PRINT_DM_TARGET=(id) \`. Locally visible function entry points include `init_s, init_dm_target_spec, print_dm_target_spec, main`.

Control flow: helper init_s seeds dm_ioctl headers and init_dm_target_spec builds deterministic targets. main exercises invalid operations, unsupported ABI versions, short data sizes, unterminated names/uuids, flag decoding, nodev/dev commands, table-load target walking, invalid data_start/next values, target messages, geometry strings, rename strings, and final overlarge target_count. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_dm.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: uses global struct s plus tail-allocated dm_ioctl layouts; no persistent state. VERBOSE controls whether nested target/message/string payloads are expanded or replaced with ellipses. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/dm-ioctl.h, sys/ioctl.h, alignment macros, str129 fixture string, VERBOSE macro. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: DM UAPI layout/flag drift, alignment assumptions, max string length truncation, and verbose/non-verbose split can break expected text. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact EBADF output checks header field selection, flag xlat expansion, safe traversal of nested variable-length data, inaccessible pointer reporting, and verbose ellipsis behavior. This file has 749 source lines and 24560 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_dm.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_epoll-Xabbrev.c

Purpose: `ioctl_epoll-Xabbrev.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. Wrapper chain: ioctl_epoll-Xabbrev.c -> ioctl_epoll.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `ioctl_epoll.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 3 source lines and 47 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_epoll-Xraw.c

Purpose: `ioctl_epoll-Xraw.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. Wrapper chain: ioctl_epoll-Xraw.c -> ioctl_epoll.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `ioctl_epoll.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 3 source lines and 44 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_epoll-Xverbose.c

Purpose: `ioctl_epoll-Xverbose.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. Wrapper chain: ioctl_epoll-Xverbose.c -> ioctl_epoll.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `ioctl_epoll.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 3 source lines and 48 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_epoll-success-Xabbrev.c

Purpose: `ioctl_epoll-success-Xabbrev.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. Wrapper chain: ioctl_epoll-success-Xabbrev.c -> ioctl_epoll-success.c -> ioctl_epoll.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `ioctl_epoll-success.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 3 source lines and 55 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_epoll-success-Xraw.c

Purpose: `ioctl_epoll-success-Xraw.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. Wrapper chain: ioctl_epoll-success-Xraw.c -> ioctl_epoll-success.c -> ioctl_epoll.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `ioctl_epoll-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 3 source lines and 52 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_epoll-success-Xverbose.c

Purpose: `ioctl_epoll-success-Xverbose.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. Wrapper chain: ioctl_epoll-success-Xverbose.c -> ioctl_epoll-success.c -> ioctl_epoll.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `ioctl_epoll-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 3 source lines and 56 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success.c -->
# sources/test-tools/strace/tests/ioctl_epoll-success.c

Purpose: `ioctl_epoll-success.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. Wrapper chain: ioctl_epoll-success.c -> ioctl_epoll.c. Variant effect: INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `ioctl_epoll.c` and `INJECT_RETVAL=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll.c -->
# sources/test-tools/strace/tests/ioctl_epoll.c

Purpose: `ioctl_epoll.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `tests.h, scno.h, errno.h, inttypes.h, stdio.h, stdlib.h, string.h, unistd.h, linux/ioctl.h, linux/eventpoll.h` and `implementation defaults`. Locally visible function entry points include `sys_ioctl, main`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 173 source lines and 4195 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_evdev-Xabbrev.c

Purpose: `ioctl_evdev-Xabbrev.c` evdev ioctl decoder test for failure-side command and structure argument rendering. Wrapper chain: ioctl_evdev-Xabbrev.c -> ioctl_evdev.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `ioctl_evdev.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 3 source lines and 47 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_evdev-Xraw.c

Purpose: `ioctl_evdev-Xraw.c` evdev ioctl decoder test for failure-side command and structure argument rendering. Wrapper chain: ioctl_evdev-Xraw.c -> ioctl_evdev.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `ioctl_evdev.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 3 source lines and 44 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_evdev-Xverbose.c

Purpose: `ioctl_evdev-Xverbose.c` evdev ioctl decoder test for failure-side command and structure argument rendering. Wrapper chain: ioctl_evdev-Xverbose.c -> ioctl_evdev.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `ioctl_evdev.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 3 source lines and 48 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-Xabbrev.c

Purpose: `ioctl_evdev-success-Xabbrev.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-Xabbrev.c -> ioctl_evdev-success.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 55 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-Xraw.c

Purpose: `ioctl_evdev-success-Xraw.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-Xraw.c -> ioctl_evdev-success.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 52 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c

Purpose: `ioctl_evdev-success-Xverbose.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-Xverbose.c -> ioctl_evdev-success.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 56 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-v-Xabbrev.c

Purpose: `ioctl_evdev-success-v-Xabbrev.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-v-Xabbrev.c -> ioctl_evdev-success-v.c -> ioctl_evdev-success.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 57 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-v-Xraw.c

Purpose: `ioctl_evdev-success-v-Xraw.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-v-Xraw.c -> ioctl_evdev-success-v.c -> ioctl_evdev-success.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success-v.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 54 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-v-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-v-Xverbose.c

Purpose: `ioctl_evdev-success-v-Xverbose.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-v-Xverbose.c -> ioctl_evdev-success-v.c -> ioctl_evdev-success.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success-v.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 58 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-v-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-v.c

Purpose: `ioctl_evdev-success-v.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-v.c -> ioctl_evdev-success.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 51 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success.c

Purpose: `ioctl_evdev-success.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `tests.h, assert.h, inttypes.h, stdio.h, stdlib.h, sys/ioctl.h, linux/ioctl.h, linux/input.h, print_fields.h` and `NUM_WORDS=4`. Locally visible function entry points include `invoke_test_syscall, test_evdev, print_input_absinfo, print_input_id, print_mtslots, print_getbit, main`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 351 source lines and 9095 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_evdev-v-Xabbrev.c

Purpose: `ioctl_evdev-v-Xabbrev.c` evdev ioctl decoder test for failure-side command and structure argument rendering. Wrapper chain: ioctl_evdev-v-Xabbrev.c -> ioctl_evdev-v.c -> ioctl_evdev.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `ioctl_evdev-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_evdev-v-Xraw.c

Purpose: `ioctl_evdev-v-Xraw.c` evdev ioctl decoder test for failure-side command and structure argument rendering. Wrapper chain: ioctl_evdev-v-Xraw.c -> ioctl_evdev-v.c -> ioctl_evdev.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `ioctl_evdev-v.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-v-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_evdev-v-Xverbose.c

Purpose: `ioctl_evdev-v-Xverbose.c` evdev ioctl decoder test for failure-side command and structure argument rendering. Wrapper chain: ioctl_evdev-v-Xverbose.c -> ioctl_evdev-v.c -> ioctl_evdev.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `ioctl_evdev-v.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 3 source lines and 50 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-v-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v.c -->
# sources/test-tools/strace/tests/ioctl_evdev-v.c

Purpose: `ioctl_evdev-v.c` evdev ioctl decoder test for failure-side command and structure argument rendering. Wrapper chain: ioctl_evdev-v.c -> ioctl_evdev.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `ioctl_evdev.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 4 source lines and 97 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev.c -->
# sources/test-tools/strace/tests/ioctl_evdev.c

Purpose: `ioctl_evdev.c` evdev ioctl decoder test for failure-side command and structure argument rendering. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `tests.h, errno.h, inttypes.h, stdio.h, string.h, sys/ioctl.h, linux/ioctl.h, linux/input.h` and `TEST_NULL_ARG_EX=(cmd, str)					\, TEST_NULL_ARG=(cmd) TEST_NULL_ARG_EX(cmd, #cmd)`. Locally visible function entry points include `print_envelope, print_ffe_common, main`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 289 source lines and 8144 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-Xabbrev.c

Purpose: `ioctl_fiemap-Xabbrev.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-Xabbrev.c -> ioctl_fiemap.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 48 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-Xraw.c

Purpose: `ioctl_fiemap-Xraw.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-Xraw.c -> ioctl_fiemap.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 45 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-Xverbose.c

Purpose: `ioctl_fiemap-Xverbose.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-Xverbose.c -> ioctl_fiemap.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-Xabbrev.c

Purpose: `ioctl_fiemap-success-Xabbrev.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-Xabbrev.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 56 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-Xraw.c

Purpose: `ioctl_fiemap-success-Xraw.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-Xraw.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 53 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-Xverbose.c

Purpose: `ioctl_fiemap-success-Xverbose.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-Xverbose.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 57 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c

Purpose: `ioctl_fiemap-success-v-Xabbrev.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-v-Xabbrev.c -> ioctl_fiemap-success-v.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 58 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xraw.c

Purpose: `ioctl_fiemap-success-v-Xraw.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-v-Xraw.c -> ioctl_fiemap-success-v.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success-v.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 55 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xverbose.c

Purpose: `ioctl_fiemap-success-v-Xverbose.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-v-Xverbose.c -> ioctl_fiemap-success-v.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success-v.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 59 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-v.c

Purpose: `ioctl_fiemap-success-v.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-v.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 52 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success.c

Purpose: `ioctl_fiemap-success.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap.c` and `INJECT_RETVAL=42`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 51 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap.c -->
# sources/test-tools/strace/tests/ioctl_fiemap.c

Purpose: `ioctl_fiemap.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `tests.h, stdio.h, stdlib.h, sys/ioctl.h, linux/types.h, linux/fiemap.h, linux/fs.h` and `VALID_FM_FLAGS=0x7, INVALID_FM_FLAGS=0xfffffff8, VALID_FE_FLAGS=0x3f8f, INVALID_FE_FLAGS=0xffffc070`. Locally visible function entry points include `do_ioctl, do_ioctl_ptr, skip_ioctls, main`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 188 source lines and 5439 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-Xabbrev.c

Purpose: `ioctl_fs_0x15-Xabbrev.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-Xabbrev.c -> ioctl_fs_0x15.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-Xraw.c

Purpose: `ioctl_fs_0x15-Xraw.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-Xraw.c -> ioctl_fs_0x15.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-Xverbose.c

Purpose: `ioctl_fs_0x15-Xverbose.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-Xverbose.c -> ioctl_fs_0x15.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 50 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xabbrev.c

Purpose: `ioctl_fs_0x15-success-Xabbrev.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-success-Xabbrev.c -> ioctl_fs_0x15-success.c -> ioctl_fs_0x15.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15-success.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 57 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xraw.c

Purpose: `ioctl_fs_0x15-success-Xraw.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-success-Xraw.c -> ioctl_fs_0x15-success.c -> ioctl_fs_0x15.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 54 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xverbose.c

Purpose: `ioctl_fs_0x15-success-Xverbose.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-success-Xverbose.c -> ioctl_fs_0x15-success.c -> ioctl_fs_0x15.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 58 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-success.c

Purpose: `ioctl_fs_0x15-success.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-success.c -> ioctl_fs_0x15.c. Variant effect: INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15.c` and `INJECT_RETVAL=42`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 52 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15.c

Purpose: `ioctl_fs_0x15.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `tests.h, linux/fs.h, errno.h, stdio.h, stdlib.h, sys/ioctl.h` and `VALID_LBMD_FLAGS=0x3, VALID_LBMD_FLAGS_STR="LBMD_PI_CAP_INTEGRITY|LBMD_PI_CAP_REFTAG", INVALID_LBMD_FLAGS=0xfffffffc, VALID_LBMD_TYPE=0x1, VALID_LBMD_TYPE_STR="LBMD_PI_CSUM_IP", INVALID_LBMD_TYPE=0x8`. Locally visible function entry points include `do_ioctl, do_ioctl_ptr, skip_ioctls, main`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 275 source lines and 7645 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fs_f-Xabbrev.c

Purpose: `ioctl_fs_f-Xabbrev.c` FS_IOC{,32}_{G,S}ETFLAGS decoder test for legacy filesystem inode flags. Wrapper chain: ioctl_fs_f-Xabbrev.c -> ioctl_fs_f.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC32_GETFLAGS, FS_IOC32_SETFLAGS, FS_IOC_GETFLAGS, FS_IOC_SETFLAGS, FS_*_FL flags, _IO('f',0xff) fallback. Local include directives/macros observed in this source are `ioctl_fs_f.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main iterates command descriptors, skipping duplicate 32-bit/native aliases when equal, then tests NULL/0, bad pointer, invalid flag word for set commands, valid flag word for set commands, and pointer-only get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_f.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; one tail-allocated unsigned int is mutated for flags. There is no injected-return path in this file. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: architecture aliases between native and 32-bit commands, filesystem flag table additions, and xlat mode rendering changes. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates duplicate skipping, on-enter vs on-exit argument policy, known/unknown FS flag printing, and fallback command formatting. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_f-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fs_f-Xraw.c

Purpose: `ioctl_fs_f-Xraw.c` FS_IOC{,32}_{G,S}ETFLAGS decoder test for legacy filesystem inode flags. Wrapper chain: ioctl_fs_f-Xraw.c -> ioctl_fs_f.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC32_GETFLAGS, FS_IOC32_SETFLAGS, FS_IOC_GETFLAGS, FS_IOC_SETFLAGS, FS_*_FL flags, _IO('f',0xff) fallback. Local include directives/macros observed in this source are `ioctl_fs_f.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main iterates command descriptors, skipping duplicate 32-bit/native aliases when equal, then tests NULL/0, bad pointer, invalid flag word for set commands, valid flag word for set commands, and pointer-only get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_f.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; one tail-allocated unsigned int is mutated for flags. There is no injected-return path in this file. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: architecture aliases between native and 32-bit commands, filesystem flag table additions, and xlat mode rendering changes. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates duplicate skipping, on-enter vs on-exit argument policy, known/unknown FS flag printing, and fallback command formatting. This file has 3 source lines and 43 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_f-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fs_f-Xverbose.c

Purpose: `ioctl_fs_f-Xverbose.c` FS_IOC{,32}_{G,S}ETFLAGS decoder test for legacy filesystem inode flags. Wrapper chain: ioctl_fs_f-Xverbose.c -> ioctl_fs_f.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC32_GETFLAGS, FS_IOC32_SETFLAGS, FS_IOC_GETFLAGS, FS_IOC_SETFLAGS, FS_*_FL flags, _IO('f',0xff) fallback. Local include directives/macros observed in this source are `ioctl_fs_f.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main iterates command descriptors, skipping duplicate 32-bit/native aliases when equal, then tests NULL/0, bad pointer, invalid flag word for set commands, valid flag word for set commands, and pointer-only get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_f.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; one tail-allocated unsigned int is mutated for flags. There is no injected-return path in this file. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: architecture aliases between native and 32-bit commands, filesystem flag table additions, and xlat mode rendering changes. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates duplicate skipping, on-enter vs on-exit argument policy, known/unknown FS flag printing, and fallback command formatting. This file has 3 source lines and 47 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_f-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f.c -->
# sources/test-tools/strace/tests/ioctl_fs_f.c

Purpose: `ioctl_fs_f.c` FS_IOC{,32}_{G,S}ETFLAGS decoder test for legacy filesystem inode flags. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC32_GETFLAGS, FS_IOC32_SETFLAGS, FS_IOC_GETFLAGS, FS_IOC_SETFLAGS, FS_*_FL flags, _IO('f',0xff) fallback. Local include directives/macros observed in this source are `tests.h, linux/fs.h, errno.h, stdio.h, sys/ioctl.h` and `VALID_FLAGS=0xf2ffffff, INVALID_FLAGS=0xd000000`. Locally visible function entry points include `do_ioctl, do_ioctl_ptr, main`.

Control flow: main iterates command descriptors, skipping duplicate 32-bit/native aliases when equal, then tests NULL/0, bad pointer, invalid flag word for set commands, valid flag word for set commands, and pointer-only get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_f.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; one tail-allocated unsigned int is mutated for flags. There is no injected-return path in this file. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: architecture aliases between native and 32-bit commands, filesystem flag table additions, and xlat mode rendering changes. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates duplicate skipping, on-enter vs on-exit argument policy, known/unknown FS flag printing, and fallback command formatting. This file has 129 source lines and 3076 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_f.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c

Purpose: `ioctl_fs_x-Xabbrev.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-Xabbrev.c -> ioctl_fs_x.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-Xraw.c

Purpose: `ioctl_fs_x-Xraw.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-Xraw.c -> ioctl_fs_x.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 43 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-Xverbose.c

Purpose: `ioctl_fs_x-Xverbose.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-Xverbose.c -> ioctl_fs_x.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 47 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-success-Xabbrev.c

Purpose: `ioctl_fs_x-success-Xabbrev.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-success-Xabbrev.c -> ioctl_fs_x-success.c -> ioctl_fs_x.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x-success.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 54 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-success-Xraw.c

Purpose: `ioctl_fs_x-success-Xraw.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-success-Xraw.c -> ioctl_fs_x-success.c -> ioctl_fs_x.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 51 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-success-Xverbose.c

Purpose: `ioctl_fs_x-success-Xverbose.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-success-Xverbose.c -> ioctl_fs_x-success.c -> ioctl_fs_x.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 55 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-success.c

Purpose: `ioctl_fs_x-success.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-success.c -> ioctl_fs_x.c. Variant effect: INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x.c` and `INJECT_RETVAL=42`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x.c -->
# sources/test-tools/strace/tests/ioctl_fs_x.c

Purpose: `ioctl_fs_x.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `tests.h, linux/fs.h, errno.h, stdio.h, stdlib.h, sys/ioctl.h, test_fs_xflags.h` and `INVALID_FS_SHUTDOWN_FLAG=0x3`. Locally visible function entry points include `do_ioctl, do_ioctl_ptr, skip_ioctls, main`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 258 source lines and 7388 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_gpio-Xabbrev.c

Purpose: `ioctl_gpio-Xabbrev.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-Xabbrev.c -> ioctl_gpio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_gpio-Xraw.c

Purpose: `ioctl_gpio-Xraw.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-Xraw.c -> ioctl_gpio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 43 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_gpio-Xverbose.c

Purpose: `ioctl_gpio-Xverbose.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-Xverbose.c -> ioctl_gpio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 47 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success-Xabbrev.c

Purpose: `ioctl_gpio-success-Xabbrev.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success-Xabbrev.c -> ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-success.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 54 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success-Xraw.c

Purpose: `ioctl_gpio-success-Xraw.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success-Xraw.c -> ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 51 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success-Xverbose.c

Purpose: `ioctl_gpio-success-Xverbose.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success-Xverbose.c -> ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 55 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success-v-Xabbrev.c

Purpose: `ioctl_gpio-success-v-Xabbrev.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success-v-Xabbrev.c -> ioctl_gpio-success-v.c -> ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-success-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 56 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success-v-Xraw.c

Purpose: `ioctl_gpio-success-v-Xraw.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success-v-Xraw.c -> ioctl_gpio-success-v.c -> ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-success-v.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 53 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success-v-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success-v-Xverbose.c

Purpose: `ioctl_gpio-success-v-Xverbose.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success-v-Xverbose.c -> ioctl_gpio-success-v.c -> ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-success-v.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 57 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success-v-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success-v.c

Purpose: `ioctl_gpio-success-v.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success-v.c -> ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-success.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 50 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success.c -->
# sources/test-tools/strace/tests/ioctl_gpio-success.c

Purpose: `ioctl_gpio-success.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-success.c -> ioctl_gpio.c. Variant effect: INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio.c` and `INJECT_RETVAL=42`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_gpio-v-Xabbrev.c

Purpose: `ioctl_gpio-v-Xabbrev.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-v-Xabbrev.c -> ioctl_gpio-v.c -> ioctl_gpio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 48 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_gpio-v-Xraw.c

Purpose: `ioctl_gpio-v-Xraw.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-v-Xraw.c -> ioctl_gpio-v.c -> ioctl_gpio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-v.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 45 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-v-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_gpio-v-Xverbose.c

Purpose: `ioctl_gpio-v-Xverbose.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-v-Xverbose.c -> ioctl_gpio-v.c -> ioctl_gpio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio-v.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-v-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v.c -->
# sources/test-tools/strace/tests/ioctl_gpio-v.c

Purpose: `ioctl_gpio-v.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. Wrapper chain: ioctl_gpio-v.c -> ioctl_gpio.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `ioctl_gpio.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 3 source lines and 42 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio.c -->
# sources/test-tools/strace/tests/ioctl_gpio.c

Purpose: `ioctl_gpio.c` GPIO v1/v2 ioctl decoder test for chip, line info, handles, events, line values, and v2 config attributes. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are GPIO_GET_CHIPINFO_IOCTL, GPIO_GET_LINEINFO_IOCTL, GPIO_GET_LINEINFO_WATCH_IOCTL, GPIO_GET_LINEINFO_UNWATCH_IOCTL, GPIO_GET_LINEHANDLE_IOCTL, GPIO_GET_LINEEVENT_IOCTL, GPIOHANDLE_*_IOCTL, GPIO_V2_GET_LINEINFO_IOCTL, GPIO_V2_GET_LINE_IOCTL, GPIO_V2_LINE_*_IOCTL, gpiochip_info, gpioline_info, gpiohandle_request/data/config, gpioevent_request, gpio_v2_line_info/request/values/config/attribute. Local include directives/macros observed in this source are `tests.h, errno.h, inttypes.h, stdio.h, stdlib.h, string.h, sys/ioctl.h, linux/gpio.h` and `str_event_flags=XLAT_KNOWN(0x3, "GPIOEVENT_REQUEST_BOTH_EDGES"), str_handle_flags=XLAT_KNOWN(0x14, \, str_info_flags=XLAT_KNOWN(0xc, \, str_line_flags=XLAT_KNOWN(0x102, \, UNK_GPIO_FLAG=0x8000, str_handle_unk_flag=XLAT_UNKNOWN(UNK_GPIO_FLAG, "GPIOHANDLE_REQUEST_???"), str_info_unk_flag=XLAT_UNKNOWN(UNK_GPIO_FLAG, "GPIOLINE_FLAG_???"), str_line_unk_flag=XLAT_UNKNOWN(UNK_GPIO_FLAG, "GPIO_V2_LINE_FLAG_???")`. Locally visible function entry points include `do_ioctl, do_ioctl_ptr, test_print_gpiochip_info, test_print_gpioline_info, test_print_gpioline_info_unwatch, test_print_gpiohandle_request, test_print_gpioevent_request, test_print_gpiohandle_get_values, test_print_gpiohandle_set_values, test_print_gpiohandle_set_config, print_gpio_v2_line_attr, test_print_gpio_v2_line_info, test_print_gpio_v2_line_request, test_print_gpio_v2_line_get_values, test_print_gpio_v2_line_set_values, test_print_gpio_v2_line_set_config, main`.

Control flow: optional injection locks on GPIO_GET_CHIPINFO_IOCTL; main prints an unknown GPIO command, then calls focused helpers for each v1 and v2 ioctl. Helpers test NULL, bad pointers, known flags, unknown flags, padding, too-large line/attr counts, output-side fd fields, and value masks. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_gpio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, tail-allocated GPIO structs are mutated. VERBOSE expands full 64-line sequences; default mode truncates long sequences. INJECT_RETVAL marks success expectations. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/gpio.h, sys/ioctl.h, XLAT helpers, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: GPIO UAPI v1/v2 evolution, line/attribute max constants, padding display, and xlat/verbose mode splits are fragile. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates all covered GPIO structs, known/unknown flags, array truncation, padding visibility, output fd fields, and injection suffixes. This file has 733 source lines and 25391 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_gpio.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_hdio-Xabbrev.c

Purpose: `ioctl_hdio-Xabbrev.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-Xabbrev.c -> ioctl_hdio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_hdio-Xraw.c

Purpose: `ioctl_hdio-Xraw.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-Xraw.c -> ioctl_hdio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 43 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c

Purpose: `ioctl_hdio-Xverbose.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-Xverbose.c -> ioctl_hdio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 47 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success-Xabbrev.c

Purpose: `ioctl_hdio-success-Xabbrev.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success-Xabbrev.c -> ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-success.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 54 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success-Xraw.c

Purpose: `ioctl_hdio-success-Xraw.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success-Xraw.c -> ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 51 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success-Xverbose.c

Purpose: `ioctl_hdio-success-Xverbose.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success-Xverbose.c -> ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 55 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success-v-Xabbrev.c

Purpose: `ioctl_hdio-success-v-Xabbrev.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success-v-Xabbrev.c -> ioctl_hdio-success-v.c -> ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-success-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 56 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success-v-Xraw.c

Purpose: `ioctl_hdio-success-v-Xraw.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success-v-Xraw.c -> ioctl_hdio-success-v.c -> ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-success-v.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 53 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success-v-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success-v-Xverbose.c

Purpose: `ioctl_hdio-success-v-Xverbose.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success-v-Xverbose.c -> ioctl_hdio-success-v.c -> ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-success-v.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 57 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success-v-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success-v.c

Purpose: `ioctl_hdio-success-v.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success-v.c -> ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-success.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 50 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success.c -->
# sources/test-tools/strace/tests/ioctl_hdio-success.c

Purpose: `ioctl_hdio-success.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-success.c -> ioctl_hdio.c. Variant effect: INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio.c` and `INJECT_RETVAL=42`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_hdio-v-Xabbrev.c

Purpose: `ioctl_hdio-v-Xabbrev.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-v-Xabbrev.c -> ioctl_hdio-v.c -> ioctl_hdio.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 48 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_hdio-v-Xraw.c

Purpose: `ioctl_hdio-v-Xraw.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-v-Xraw.c -> ioctl_hdio-v.c -> ioctl_hdio.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-v.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 45 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-v-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_hdio-v-Xverbose.c

Purpose: `ioctl_hdio-v-Xverbose.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-v-Xverbose.c -> ioctl_hdio-v.c -> ioctl_hdio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio-v.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-v-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v.c -->
# sources/test-tools/strace/tests/ioctl_hdio-v.c

Purpose: `ioctl_hdio-v.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-v.c -> ioctl_hdio.c. Variant effect: VERBOSE expands nested structures, arrays, strings, or long returned buffers.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio.c` and `VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 42 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio.c -->
# sources/test-tools/strace/tests/ioctl_hdio.c

Purpose: `ioctl_hdio.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `tests.h, errno.h, stdio.h, stdlib.h, linux/hdreg.h, sys/ioctl.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h` and `implementation defaults`. Locally visible function entry points include `do_ioctl, do_ioctl_ptr, main`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 431 source lines and 11853 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_inotify.c -->
# sources/test-tools/strace/tests/ioctl_inotify.c

Purpose: `ioctl_inotify.c` inotify ioctl decoder test for INOTIFY_IOC_SETNEXTWD and unknown inotify command formatting. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, INOTIFY_IOC_SETNEXTWD, _IOC macros, int32_t watch-descriptor argument. Local include directives/macros observed in this source are `tests.h, inttypes.h, stdio.h, string.h, unistd.h, scno.h, linux/ioctl.h` and `implementation defaults`. Locally visible function entry points include `sys_ioctl, main`.

Control flow: main sends a crafted unknown inotify command, INOTIFY_IOC_SETNEXTWD+1, then INOTIFY_IOC_SETNEXTWD with a magic argument and prints expected generic or symbolic decoding. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_inotify.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; constants are local and the syscall is always against fd -1. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/ioctl.h; provides fallback definition for INOTIFY_IOC_SETNEXTWD. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: command fallback text depends on _IOC bit layout and host headers; signed truncation of magic to int is intentional. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected EBADF output validates unknown _IOC decomposition and signed integer argument printing for SETNEXTWD. This file has 61 source lines and 1622 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_inotify.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_inotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_kd-Xabbrev.c

Purpose: `ioctl_kd-Xabbrev.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-Xabbrev.c -> ioctl_kd.c. Variant effect: it is an include-only wrapper that selects the default/abbreviated compile of the implementation.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd.c` and `implementation defaults`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 2 source lines and 22 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_kd-Xraw.c

Purpose: `ioctl_kd-Xraw.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-Xraw.c -> ioctl_kd.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 41 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_kd-Xverbose.c

Purpose: `ioctl_kd-Xverbose.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-Xverbose.c -> ioctl_kd.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 45 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_kd-success-Xabbrev.c

Purpose: `ioctl_kd-success-Xabbrev.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success-Xabbrev.c -> ioctl_kd-success.c -> ioctl_kd.c. Variant effect: RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd-success.c` and `implementation defaults`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 2 source lines and 30 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_kd-success-Xraw.c

Purpose: `ioctl_kd-success-Xraw.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success-Xraw.c -> ioctl_kd-success.c -> ioctl_kd.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd-success.c` and `XLAT_RAW=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_kd-success-Xverbose.c

Purpose: `ioctl_kd-success-Xverbose.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success-Xverbose.c -> ioctl_kd-success.c -> ioctl_kd.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 53 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xabbrev.c

Purpose: `ioctl_kd-success-s1024-Xabbrev.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success-s1024-Xabbrev.c -> ioctl_kd-success-Xabbrev.c -> ioctl_kd-success.c -> ioctl_kd.c. Variant effect: RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output; DEFAULT_STRLEN=1024 broadens string/map truncation expectations.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd-success-Xabbrev.c` and `DEFAULT_STRLEN=1024`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 66 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xraw.c

Purpose: `ioctl_kd-success-s1024-Xraw.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success-s1024-Xraw.c -> ioctl_kd-success-Xraw.c -> ioctl_kd-success.c -> ioctl_kd.c. Variant effect: XLAT_RAW selects numeric/raw xlat rendering for command and enum values; RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output; DEFAULT_STRLEN=1024 broadens string/map truncation expectations.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd-success-Xraw.c` and `DEFAULT_STRLEN=1024`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 63 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xraw.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xverbose.c

Purpose: `ioctl_kd-success-s1024-Xverbose.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success-s1024-Xverbose.c -> ioctl_kd-success-Xverbose.c -> ioctl_kd-success.c -> ioctl_kd.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering; RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output; DEFAULT_STRLEN=1024 broadens string/map truncation expectations.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd-success-Xverbose.c` and `DEFAULT_STRLEN=1024`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 67 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024.c -->
# sources/test-tools/strace/tests/ioctl_kd-success-s1024.c

Purpose: `ioctl_kd-success-s1024.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success-s1024.c -> ioctl_kd-success.c -> ioctl_kd.c. Variant effect: RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output; DEFAULT_STRLEN=1024 broadens string/map truncation expectations.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd-success.c` and `DEFAULT_STRLEN=1024`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 58 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success-s1024.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success-s1024.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success.c -->
# sources/test-tools/strace/tests/ioctl_kd-success.c

Purpose: `ioctl_kd-success.c` large keyboard/display KD/KDG/KDS ioctl decoder test covering console sound, LEDs, keyboard maps, strings, fonts, unicode maps, color maps, and font operations. Wrapper chain: ioctl_kd-success.c -> ioctl_kd.c. Variant effect: RETVAL_INJECTED changes KD expectations from EBADF to injected successful return output.

Important APIs/types/functions: Primary APIs and data surfaces are KDGETLED/KDSETLED, KDGKBTYPE, KDADDIO/KDDELIO/KDENABIO/KDDISABIO, KDSETMODE/KDGETMODE, KDMAPDISP/KDUNMAPDISP, GIO/PIO_SCRNMAP, KDG/KDSKBMODE, KDG/KDSKBENT, KDG/KDSKBSENT, KDG/KDSKBDIACR, KDGET/SETKEYCODE, KDSIGACCEPT, KDKBDREP, GIO/PIO_FONT, KDG/KDSKBMETA, KDG/KDSKBLED, GIO/PIO_UNIMAP, PIO_UNIMAPCLR, GIO/PIO_UNISCRNMAP, GIO/PIO_FONTX, PIO_FONTRESET, GIO/PIO_CMAP, KDFONTOP, KDG/KDSKBDIACRUC. Local include directives/macros observed in this source are `ioctl_kd.c` and `RETVAL_INJECTED=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sys_ioctl wraps __NR_ioctl. Helper families check NULL/invalid pointers, screen maps, keyboard entries/strings/diacritics, keycodes, repeat settings, font buffers, unicode maps, screen maps, fontx, color maps, and unicode diacritics. main also tests scalar sound, tone, LED, mode, IO port, signal, meta, and font operation cases. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_kd.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; extensive tail-allocated buffers are filled with deterministic byte patterns. RETVAL_INJECTED changes failure expectations to = 42 (INJECTED); DEFAULT_STRLEN controls long string/map truncation; XLAT modes alter symbolic formatting. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/kd.h, linux/keyboard.h, signal.h, tail_alloc/fill_memory/print_quoted helpers, xlat macros, ioctl-success-style injection for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel keyboard header compatibility, missing kbdiacruc/kbdiacrsuc definitions, DEFAULT_STRLEN-dependent truncation, 32/64-bit argument formatting, and xlat table drift. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates a very broad KD surface, including pointer faults, known/unknown symbols, quoted strings/hex, map truncation, injected output-side fields, and s1024 string-length variants. This file has 3 source lines and 48 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_kd-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd-success.c -->
