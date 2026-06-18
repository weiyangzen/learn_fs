# subset-b-009350 research

Grouped research report for strace ioctl decoder tests in `sources/test-tools/strace/tests`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd.c -->
# sources/test-tools/strace/tests/ioctl_kd.c

Purpose: exhaustive strace test for Linux keyboard/display (`KD*`, `KDG*`, `KDS*`, `GIO_*`, `PIO_*`) ioctl decoding. It drives invalid fd `-1` plus crafted pointers and payloads so expected output can be compared against strace's decoder without requiring a real console device.

Important APIs/types/functions: Uses raw `syscall(__NR_ioctl)` through `sys_ioctl`, `linux/kd.h`, `linux/keyboard.h`, `struct kbentry`, `kbsentry`, `kbdiacrs`, `kbkeycode`, `kbd_repeat`, `unimapdesc`, `consolefontdesc`, `console_font_op`, and fallback `kbdiacruc/kbdiacrsuc` definitions. Helper functions cover null/invalid pointer handling, screen maps, key entries, function-key strings, diacritics, keycodes, repeat rates, font buffers, unicode maps, color maps, and Unicode diacritics.

Control flow: optional injection setup locks onto an injected `KDGETLED` return. `main` first probes unknown `K` ioctl numbers, then emits grouped decoder checks for speaker/tone commands, LEDs, keyboard type/mode/meta/LEDs, I/O permissions, display mode, screen/font/unicode maps, key tables, signal acceptance, `PIO_UNIMAPCLR`, `KDFONTOP`, and diacritic Unicode tables. Helpers intentionally place buffers at page tails and vary `DEFAULT_STRLEN`, pointer alignment, write/read direction, and known/unknown xlat values.

State and persistence behavior: all state is process-local allocated test memory; no console state should change because calls use fd `-1`. Under syscall injection the same buffers model successful read/write ioctl output so strace must print dereferenced structs and before/after arrows correctly.

Dependencies/integration points: depends on strace test helpers (`tail_alloc`, fill/print helpers, xlat macros, `scno.h`) and kernel UAPI headers. It integrates with strace's xlat modes, syscall injection tests, string truncation logic, pointer fault decoding, and platform word-size formatting.

Risks and test signals: high risk of brittle expected strings because kernel headers, xlat tables, `DEFAULT_STRLEN`, word size, and injected-success behavior all affect output. Test success is exact emitted output ending in `+++ exited with 0 +++`; failures indicate decoder regressions for console ioctls, enum expansion, buffer truncation, or read/write argument classification.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run-v.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run-v.c

Purpose: verbose-mode variant of the KVM run test. It defines `VERBOSE 1` before including `ioctl_kvm_run.c`, expanding register, segment, CPUID, and `kvm_run` structure output beyond the abbreviated base mode.

Important APIs/types/functions: Inherits all KVM APIs from `ioctl_kvm_run_common.c`, especially `/dev/kvm`, `KVM_GET_*`, `KVM_SET_*`, `KVM_RUN`, `struct kvm_regs`, `kvm_sregs`, `kvm_cpuid2`, and `kvm_run`. The local API surface is only the compile-time `VERBOSE` macro.

Control flow: compilation routes through `ioctl_kvm_run.c` into the common implementation; runtime is identical to the base KVM test but all `#if VERBOSE` branches print full segment registers, all general registers, CPUID entries, and richer exit payload fields.

State and persistence behavior: creates a transient VM, VCPU, mmaped guest page, and `kvm_run` mapping. No durable state is written; verbose mode changes only expected trace text.

Dependencies/integration points: requires KVM headers, x86, `/dev/kvm`, and `/proc/self/fd`. Integrates with strace verbose decoder output contracts.

Risks and test signals: verbose expected output is more sensitive to kernel-provided CPUID and register layouts. Passing output confirms strace can print non-abbreviated KVM ioctl structures and exits.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run.c

Purpose: base KVM run test wrapper. It includes `ioctl_kvm_run_common.c` with default abbreviated formatting to exercise real `/dev/kvm` ioctl decoding and `KVM_RUN` exit rendering.

Important APIs/types/functions: The implementation is in the included common file: `KVM_GET_API_VERSION`, `KVM_CHECK_EXTENSION`, `KVM_CREATE_VM`, `KVM_SET_USER_MEMORY_REGION`, `KVM_CREATE_VCPU`, `KVM_GET_VCPU_MMAP_SIZE`, `KVM_GET/SET_SREGS`, `KVM_SET_REGS`, `KVM_GET_SUPPORTED_CPUID`, `KVM_SET_CPUID2`, and `KVM_RUN`.

Control flow: compile-time inclusion supplies `main`. At runtime it opens `/dev/kvm`, creates a VM/VCPU, maps guest memory and the `kvm_run` area, configures CPUID and registers, copies a tiny x86 real-mode program, and loops through KVM exits until HLT.

State and persistence behavior: all state is transient kernel KVM state plus anonymous memory mappings. The test verifies state transitions visible through ioctls, not disk persistence.

Dependencies/integration points: requires Linux KVM UAPI, x86, accessible `/dev/kvm`, mmap, and strace fd-path decoding. It is skipped when prerequisites or compatible kernel features are absent.

Risks and test signals: environment-sensitive because KVM availability and permissions vary. Passing output confirms abbreviated decoding of KVM setup ioctls, CPUID arrays, register structs, and `KVM_RUN` exit data.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu.c

Purpose: KVM run variant focused on auxiliary fd string behavior when old kernels expose VCPU fds as `anon_inode:kvm-vcpu` without a `:0` suffix. It customizes the common test to print an explicit VCPU auxstr check.

Important APIs/types/functions: Defines `KVM_NO_CPUID_CALLBACK`, includes `ioctl_kvm_run_common.c`, and provides `print_KVM_RUN` plus a helper that formats expected `KVM_RUN` output with the current `vcpu_dev` string. It uses the same KVM ioctls and `struct kvm_run` data as the common test.

Control flow: common `main` detects whether `/proc/self/fd/<vcpu>` matches `anon_inode:kvm-vcpu:0`; if not, it trims the device string and invokes the callback. The variant's `print_KVM_RUN` checks the auxstr attached to VCPU fd output while the VM exit loop runs.

State and persistence behavior: transient VM/VCPU state only. The extra state is the mutable `vcpu_dev` expected-name buffer in common code.

Dependencies/integration points: integrates `/proc/self/fd` readlink behavior, strace fd auxstr rendering, and KVM `KVM_RUN` decoding.

Risks and test signals: kernel-version sensitive because VCPU fd names differ. The signal is stable expected output for `KVM_RUN` whether or not the kernel provides a CPUID suffix in the anon inode name.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu_more.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu_more.c

Purpose: extension of the VCPU auxstr KVM run variant that adds a `print_KVM_RUN_MORE` hook for additional `kvm_run` exit detail checks.

Important APIs/types/functions: Defines `print_KVM_RUN_MORE` before including `ioctl_kvm_run_auxstr_vcpu.c`, then implements extra printing functions after inclusion. It depends on `struct kvm_run`, KVM exit fields, and the same `vcpu_dev`/fd auxstr paths as the included variant.

Control flow: included common code performs VM setup and the exit loop. When `print_KVM_RUN` is called, this variant's extra hook observes before/after `kvm_run` data and prints additional expected fragments for IO/MMIO exit decoding.

State and persistence behavior: transient KVM and memory-mapped state only. The additional hook consumes snapshots of the shared `kvm_run` mapping captured before each `KVM_RUN`.

Dependencies/integration points: tests the integration between KVM exit data, strace's auxstr fd formatting, and macro-injected expected-output helpers.

Risks and test signals: sensitive to exact exit sequence from the embedded x86 program. Passing output confirms that richer VCPU auxstr/exit rendering remains stable under the specialized variant.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_auxstr_vcpu_more.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_common.c -->
# sources/test-tools/strace/tests/ioctl_kvm_run_common.c

Purpose: shared implementation for KVM ioctl decoding tests. It builds a tiny x86 guest, drives real KVM ioctls, and prints expected strace output for VM creation, memory mapping, register setup, CPUID handling, and `KVM_RUN` exits.

Important APIs/types/functions: Uses `kvm_ioctl`/`KVM_IOCTL`, `print_kvm_segment`, `print_kvm_sregs`, `print_kvm_regs`, `run_kvm`, `vcpu_dev_should_have_cpuid`, and `print_cpuid_ioctl`. Key UAPI types are `kvm_userspace_memory_region`, `kvm_sregs`, `kvm_regs`, `kvm_run`, `kvm_cpuid2`, and `kvm_cpuid_entry2`.

Control flow: `main` checks `/proc/self/fd`, opens `/dev/kvm`, verifies API version and memory capability, creates VM and VCPU, maps guest memory to page frame one, maps the VCPU run page, probes supported CPUID, sets CPUID twice, tests EFAULT for NULL CPUID, then calls `run_kvm`. `run_kvm` reads/modifies segment registers, sets general registers, copies the embedded real-mode assembly, repeatedly calls `KVM_RUN`, validates IO/MMIO/HLT exits, and calls variant-provided `print_KVM_RUN`.

State and persistence behavior: maintains page size, expected device strings, anonymous guest memory, mmaped shared `kvm_run` state, and kernel VM/VCPU objects. It intentionally mutates `run->mmio.data[0]` before a read continuation so strace can decode before-state data. Nothing persists after process exit.

Dependencies/integration points: gated on KVM headers, specific structs, and x86. Depends on `/dev/kvm`, mmap, `/proc/self/fd`, xlat CPUID flags, and optional macro hooks `VERBOSE`, `KVM_NO_CPUID_CALLBACK`, and variant `print_KVM_RUN`.

Risks and test signals: high environmental risk from missing KVM, permissions, nested virtualization, or kernel naming differences. Test signal is exact stdout plus skip behavior; failures expose KVM ioctl decoder regressions, auxstr mismatches, or changed VM exit semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kvm_run_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc-success.c -->
# sources/test-tools/strace/tests/ioctl_lirc-success.c

Purpose: syscall-injection success variant for LIRC ioctl decoding. It defines `INJECT_RETVAL 42` and includes the base LIRC test so read-style ioctls are decoded as if the kernel returned success.

Important APIs/types/functions: Inherits `do_ioctl`, LIRC command constants, and unsigned-int argument decoding from `ioctl_lirc.c`. The only local API is the `INJECT_RETVAL` macro.

Control flow: the included `main` first consumes a `NUM_SKIP` argument and loops on `LIRC_GET_FEATURES` until the injected return appears. Then it runs the normal LIRC command matrix with success-only sections enabled for get operations.

State and persistence behavior: process-local integer buffer only. Injection affects expected `sprintrc` text and lets strace print dereferenced output buffers.

Dependencies/integration points: integrates strace syscall injection harness with `linux/lirc.h` xlat decoding.

Risks and test signals: requires the runner to pass the correct injection skip count. Passing output confirms successful LIRC get-ioctl value and flag decoding under injected return values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc.c -->
# sources/test-tools/strace/tests/ioctl_lirc.c

Purpose: tests decoding of Linux infrared remote control (`LIRC_*`) ioctls, covering set commands, mode enums, feature flags, timeout queries, and unknown commands.

Important APIs/types/functions: Uses `do_ioctl`, `linux/lirc.h`, `LIRC_SET_*`, `LIRC_GET_*`, `LIRC_MODE_*`, `LIRC_CAN_*`, and an allocated `unsigned int` argument. Under `INJECT_RETVAL`, it verifies injected success before dereferencing read buffers.

Control flow: optional injection lock loop scans `LIRC_GET_FEATURES`. The main path fills one integer buffer with representative values and calls each set ioctl, printing decoded scalar or xlat values. In injected mode it also calls read ioctls with crafted feature/mode/timeout values and a deliberately shifted pointer. It finishes with an unknown `_IO('i', 0xff)` command.

State and persistence behavior: no device state changes because fd is `-1`; all state is one test integer and injected-return bookkeeping.

Dependencies/integration points: depends on `linux/lirc.h`, strace xlat tables for LIRC modes/features, syscall injection, and `sprintrc`.

Risks and test signals: kernel header aliases can make output mention another command (`IPMICTL_SET_MAINTENANCE_MODE_CMD`, `I2OVALIDATE`). Passing output confirms set/read direction classification, enum/flag formatting, unknown command fallback, and injected-success buffer decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-nv.c -->
# sources/test-tools/strace/tests/ioctl_loop-nv.c

Purpose: abbreviated non-verbose loop-device ioctl variant. It defines `ABBREV 1` before including `ioctl_loop.c`, forcing complex loop structs to print as pointers.

Important APIs/types/functions: Inherits loop ioctls and types from `ioctl_loop.c`: `loop_info`, `loop_info64`, `loop_config`, `LOOP_*`, `LO_FLAGS_*`, and `LO_CRYPT_*`. Local behavior is controlled by `ABBREV`.

Control flow: runtime follows the base test's unknown command, `LOOP_SET_FD`, info, status64, configure, block-size, direct-io, and control ioctl coverage, but `print_loop_info*` and `print_loop_config` choose pointer output.

State and persistence behavior: process-local structs only; invalid fd prevents loop device mutation.

Dependencies/integration points: exercises strace `-X abbrev`-like expected output for loop structs.

Risks and test signals: passing output confirms abbreviation mode suppresses struct expansion while still naming loop ioctl commands correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-nv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-v.c -->
# sources/test-tools/strace/tests/ioctl_loop-v.c

Purpose: verbose loop-device ioctl variant. It defines `VERBOSE 1` before including `ioctl_loop.c`, enabling full legacy and 64-bit loop struct field printing.

Important APIs/types/functions: Inherits `print_loop_info`, `print_loop_info64`, `print_loop_config`, `struct loop_info`, `loop_info64`, `loop_config`, and `LOOP_*` commands from the base file.

Control flow: same ioctl sequence as `ioctl_loop.c`; verbose branches add device/inode/rdevice, crypt name/key, init arrays, reserved fields, and full 64-bit info fields.

State and persistence behavior: invalid fd and local structs only. Verbose mode changes expected text, not runtime side effects.

Dependencies/integration points: validates strace verbose output for loop ioctls and `makedev` formatting.

Risks and test signals: sensitive to struct layout and word-size formatting. Passing output confirms verbose decoder coverage for loop status/configuration structs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop.c -->
# sources/test-tools/strace/tests/ioctl_loop.c

Purpose: tests decoding of loop device ioctl commands, including legacy `loop_info`, modern `loop_info64`, `loop_config`, control commands, unknown commands, flags, encryption fields, and file descriptor/scalar arguments.

Important APIs/types/functions: Uses raw `sys_ioctl`, `print_loop_info`, `print_loop_info64`, `print_loop_config`, `linux/loop.h`, `print_fields.h`, `major/minor`, `struct loop_info`, `loop_info64`, `loop_config`, `LOOP_SET_FD`, `LOOP_GET_STATUS`, `LOOP_SET_STATUS64`, `LOOP_CONFIGURE`, `LOOP_CTL_*`, and xlat strings for flags/encryption.

Control flow: `main` allocates loop structs, prints unknown loop command decoding, tests scalar commands such as `LOOP_SET_FD`, fills legacy and 64-bit info structs with crafted names, offsets, flags, encryption values, and reserved fields, then checks get/set status variants, clear fd, block size, direct IO, configure, and loop-control commands.

State and persistence behavior: no real loop device is touched because fd is `-1`; all values come from stack/tail-allocated test structs. Macro modes `ABBREV` and `VERBOSE` alter field expansion.

Dependencies/integration points: depends on Linux loop UAPI, strace xlat tables, `scno.h`, and helper macros. Integrates with output modes for pointer abbreviation, verbose field printing, and ioctl-number fallback.

Risks and test signals: loop UAPI grows over time, so reserved/unknown decoding is fragile. Passing output confirms command recognition, flag/encryption xlat behavior, struct string truncation, 32/64-bit field formatting, and `loop_config` nested decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd-success.c -->
# sources/test-tools/strace/tests/ioctl_mtd-success.c

Purpose: injected-success variant for MTD ioctl decoding. It defines `INJECT_RETVAL 42` and includes `ioctl_mtd.c`.

Important APIs/types/functions: Inherits all MTD helpers and UAPI structs from the base file; local effect is enabling success-return branches and injected `sprintrc` text.

Control flow: included `main` locks onto an injected MTD ioctl return, then executes the base MTD command matrix with read-style structs printed as successful outputs instead of pointers.

State and persistence behavior: local tail-allocated MTD structs only; injection simulates kernel writes without a device.

Dependencies/integration points: integrates strace injection with `mtd/mtd-abi.h` decoder coverage.

Risks and test signals: requires correct injection arguments. Passing output confirms successful MTD struct decoding paths, not just EBADF pointer fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd.c -->
# sources/test-tools/strace/tests/ioctl_mtd.c

Purpose: tests Memory Technology Device ioctl decoding across info, erase, OOB, region, OTP, ECC, bad-block, and 64-bit variants.

Important APIs/types/functions: Uses `do_ioctl`/`do_ioctl_ptr`, `mtd/mtd-abi.h`, `linux/ioctl.h`, MTD structs such as `mtd_info_user`, `erase_info_user`, `erase_info_user64`, `mtd_oob_buf`, `mtd_oob_buf64`, `region_info_user`, `otp_info`, `mtd_write_req`, and command constants like `MEMGETINFO`, `MEMERASE`, `MEMREADOOB`, `MEMWRITEOOB`, `MEMGETREGIONINFO`, `OTP*`, `ECCGET*`, and `MEMWRITE`.

Control flow: optional injection lock is followed by null/bad-pointer probes, crafted struct calls for read/write commands, scalar offset tests for bad-block operations, region/OTP arrays, ECC statistics/layout, and fallback unknown command decoding. The file uses helper arrays to cover known and unknown enum/flag combinations.

State and persistence behavior: all state is local test memory. Invalid fd prevents real flash operations; injected success enables output-buffer decoding.

Dependencies/integration points: depends on MTD UAPI availability, strace xlat tables, Linux version conditionals for newer commands, and syscall injection.

Risks and test signals: header-version variability and command aliases can affect expected strings. Passing output confirms direction-aware MTD struct decoding, 64-bit field handling, enum/flag expansion, and pointer fallback behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nbd.c -->
# sources/test-tools/strace/tests/ioctl_nbd.c

Purpose: tests Network Block Device ioctl command decoding, including command names, flag xlat values, scalar sizes/timeouts, and unknown command fallback.

Important APIs/types/functions: Uses `linux/nbd.h`, `xlat/nbd_ioctl_cmds.h`, `xlat/nbd_ioctl_flags.h`, `ioctl`, `open`, and NBD constants including `NBD_SET_SOCK`, `NBD_SET_BLKSIZE`, `NBD_SET_SIZE`, `NBD_DO_IT`, `NBD_CLEAR_SOCK`, `NBD_CLEAR_QUE`, `NBD_PRINT_DEBUG`, `NBD_SET_SIZE_BLOCKS`, `NBD_DISCONNECT`, `NBD_SET_TIMEOUT`, `NBD_SET_FLAGS`, `NBD_SET_TAG`, and `NBD_SET_DESCRIPTION`.

Control flow: opens `/dev/null` or uses invalid fds to produce stable EBADF/EINVAL-style output, calls each NBD command with representative integer, pointer, and string arguments, prints flag combinations, and emits unknown `_IO` command text.

State and persistence behavior: no NBD device state is persisted; invalid or harmless fds make this a decoder-only test.

Dependencies/integration points: integrates NBD UAPI command and flag xlat tables with strace ioctl decoding.

Risks and test signals: aliases and kernel header changes can alter names. Passing output confirms command recognition, scalar/string argument formatting, and unknown NBD ioctl fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid--pidns-translation.c

Purpose: pid-namespace translation variant for `NS_GET_{PID,TGID}_{FROM,IN}_PIDNS` decoding. It defines `PIDNS_TRANSLATION` before including `ioctl_nsfs-ns_get_pid.c`.

Important APIs/types/functions: Inherits pidns helper APIs (`PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`), `NS_GET_PID_FROM_PIDNS`, `NS_GET_TGID_FROM_PIDNS`, `NS_GET_PID_IN_PIDNS`, and `NS_GET_TGID_IN_PIDNS`.

Control flow: the included test prints a leader marker before ioctl lines and emits an initial `NS_GET_USERNS` synchronization probe, then runs the base PIDNS get/in/from ioctl cases.

State and persistence behavior: no persistent state; pid namespace mappings are runtime-only observations of the current process and namespace fd.

Dependencies/integration points: integrates strace pid namespace translation output with nsfs ioctl decoding and `/proc/self/ns/pid`.

Risks and test signals: sensitive to pid namespace availability and expected translated PID suffixes. Passing output confirms translated argument and return PID rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid.c -->
# sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid.c

Purpose: tests nsfs PID/TGID translation ioctls for mapping process IDs to or from a pid namespace.

Important APIs/types/functions: Uses `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `syscall(__NR_gettid)`, `/proc/self/ns/pid`, and `linux/nsfs.h` commands `NS_GET_PID_FROM_PIDNS`, `NS_GET_TGID_FROM_PIDNS`, `NS_GET_PID_IN_PIDNS`, and `NS_GET_TGID_IN_PIDNS`.

Control flow: initializes pidns test state, optionally emits pidns translation leader synchronization, first calls all four commands on fd `-1` with synthetic ids, then opens `/proc/self/ns/pid` and repeats with actual TGID/TID values, appending translated-id strings where appropriate.

State and persistence behavior: uses current process pid/tid and namespace fd only; no persistent mutations.

Dependencies/integration points: depends on `/proc`, `linux/nsfs.h`, strace pid namespace helpers, and syscall-number definitions.

Risks and test signals: output depends on pid namespace test harness and whether opening namespace fd succeeds. Passing output confirms command names, argument vs return translation placement, and pidns leader formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_mnt_get.c -->
# sources/test-tools/strace/tests/ioctl_nsfs-ns_mnt_get.c

Purpose: tests mount namespace id ioctls `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, and `NS_MNT_GET_PREV`.

Important APIs/types/functions: Uses `/proc/self/ns/mnt`, `linux/nsfs.h`, `linux/ioctl.h`, `struct mnt_ns_info`, `uint64_t` namespace ids, and `ioctl` command variants for mount namespace information and traversal.

Control flow: probes invalid fd and bad pointers, opens the current mount namespace, calls info/next/prev commands with crafted or real buffers, prints successful namespace ids or fallback error strings, and closes the fd.

State and persistence behavior: reads namespace metadata only; no persistent changes. Output state is the current mount namespace id and related traversal result if the kernel supports the ioctls.

Dependencies/integration points: depends on `/proc/self/ns/mnt`, nsfs UAPI availability, and strace decoding of nested namespace-id structs.

Risks and test signals: kernel support for these newer ioctls may vary. Passing output confirms correct command naming, pointer handling, id formatting, and graceful behavior on unsupported kernels.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_mnt_get.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs.c -->
# sources/test-tools/strace/tests/ioctl_nsfs.c

Purpose: tests generic namespace file descriptor ioctls: user namespace lookup, parent namespace lookup, namespace type, owner UID, and mount namespace id.

Important APIs/types/functions: Uses `test_no_namespace`, `test_clone`, `child`, `test_user_namespace`, `clone`/`__clone2`, `CLONE_NEWUSER`, `/proc/<pid>/ns/user`, `/proc/self/ns/mnt`, and `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, `NS_GET_OWNER_UID`, `NS_GET_MNTNS_ID`.

Control flow: first calls namespace ioctls on fd `-1` and optionally on current mount namespace. Then creates a child in a new user namespace using a pipe for lifetime control, opens the child's user namespace fd, queries userns/parent/type/owner uid, releases the child, and waits for clean exit.

State and persistence behavior: creates transient child process and user namespace; no persistent state. Namespace fds are opened and closed during the test.

Dependencies/integration points: requires clone/user namespace support, `/proc`, `linux/nsfs.h`, and strace's namespace type/uid/id decoders.

Risks and test signals: user namespace creation can be disabled, causing partial skip-like behavior. Passing output confirms nsfs command names, fd-return formatting, CLONE_NEWUSER type xlat, and owner UID pointer decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf-success.c -->
# sources/test-tools/strace/tests/ioctl_perf-success.c

Purpose: injected-success test for successful `PERF_EVENT_IOC_ID` and `PERF_EVENT_IOC_QUERY_BPF` decoding. It focuses on read-style perf ioctls whose interesting output only appears when syscall injection makes the invalid-fd calls look successful.

Important APIs/types/functions: Uses `linux/perf_event.h`, `ioctl`, `PERF_EVENT_IOC_ID`, `PERF_EVENT_IOC_QUERY_BPF`, `uint64_t` id storage, a four-element `uint32_t` query buffer, `assert`, `sprintrc`, and injected return arguments `NUM_SKIP`/`INJECT_RETVAL`.

Control flow: exits quietly when run without injection arguments. Otherwise it parses skip count and expected nonnegative injected retval, loops on `PERF_EVENT_IOC_ID` until injection is observed, then asserts injected success for NULL, EFAULT, and populated `PERF_EVENT_IOC_ID` pointers. It repeats the pattern for `PERF_EVENT_IOC_QUERY_BPF`, covering NULL, EFAULT, truncated `{ids_len, ...}`, `{ids_len, prog_cnt, ids=ptr}`, and arrays with two or more program ids.

State and persistence behavior: no perf fd is valid; syscall injection simulates success and lets strace decode the local id/query buffers as output. No perf event state is created.

Dependencies/integration points: integrates perf UAPI xlat decoding with strace syscall injection.

Risks and test signals: requires exact injection configuration and stable query-buffer layout. Passing output confirms success-return formatting for perf id and BPF-query ioctls, including pointer fallback and bounded id-array printing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf.c -->
# sources/test-tools/strace/tests/ioctl_perf.c

Purpose: tests baseline decoding of perf event ioctl commands on invalid descriptors, focusing on command names, scalar arguments, pointers, strings, and unknown command fallback.

Important APIs/types/functions: Uses raw `syscall(__NR_ioctl)`, `linux/perf_event.h`, `scno.h`, `PERF_EVENT_IOC_ENABLE`, `DISABLE`, `REFRESH`, `RESET`, `PERIOD`, `SET_OUTPUT`, `SET_FILTER`, `ID`, `SET_BPF`, `PAUSE_OUTPUT`, `QUERY_BPF`, and `MODIFY_ATTRIBUTES`.

Control flow: constructs representative scalar values, filter strings, pointers at page tails, and unknown commands. Each ioctl is issued on fd `-1` and the test prints the expected EBADF line with proper command and argument rendering.

State and persistence behavior: local buffers only; no perf event state is created.

Dependencies/integration points: depends on perf UAPI and strace xlat command tables. Integrates with syscall-number portability and string/pointer decoders.

Risks and test signals: command availability varies with headers. Passing output confirms perf ioctl name recognition, command-specific argument interpretation, and fallback for unknown perf ioctl numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xabbrev.c

Purpose: abbreviated-xlat injected-success variant for `PIDFD_GET_INFO`. It defines `XLAT_ABBREV 1` and includes the injected-success wrapper.

Important APIs/types/functions: Inherits `INJECT_RETVAL 42`, `struct pidfd_info`, mask constants, and injected decode checks from `ioctl_pidfd_get_info.c`.

Control flow: compilation applies abbreviated xlat formatting to the success path. Runtime locks onto injected `PIDFD_GET_INFO`, then prints crafted masks, pid/cred/cgroup/exit/coredump/support fields with abbreviated xlat strings.

State and persistence behavior: local `pidfd_info` buffer only; no real pidfd is required in the injected path.

Dependencies/integration points: combines strace injection and `-X abbrev` xlat output contracts.

Risks and test signals: fragile to xlat formatting changes. Passing output confirms abbreviated pidfd info masks and coredump masks under success decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xraw.c

Purpose: raw-xlat injected-success variant for `PIDFD_GET_INFO`. It defines `XLAT_RAW 1` and includes the success wrapper.

Important APIs/types/functions: Inherits all `PIDFD_GET_INFO` injected decode scenarios from `ioctl_pidfd_get_info.c`; local effect is raw numeric xlat rendering.

Control flow: after injection lock, all crafted `pidfd_info` masks and versioned command sizes are printed with raw numeric values instead of symbolic-first names.

State and persistence behavior: local buffer and injected return state only.

Dependencies/integration points: validates strace `-X raw` behavior for pidfd info commands and masks.

Risks and test signals: exact numeric command encodings and mask values are the signal. Passing output confirms raw xlat mode does not lose field decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xverbose.c

Purpose: verbose-xlat injected-success variant for `PIDFD_GET_INFO`. It defines `XLAT_VERBOSE 1` and includes the success wrapper.

Important APIs/types/functions: Inherits `PIDFD_GET_INFO` command structs, masks, and injected `pidfd_info` scenarios from the base implementation.

Control flow: same injected success path as `ioctl_pidfd_get_info-success.c`, with verbose xlat formatting that includes symbolic names and numeric values for commands and masks.

State and persistence behavior: local buffer only; injection simulates successful kernel writes.

Dependencies/integration points: validates `-X verbose` output for pidfd info decoder fields.

Risks and test signals: sensitive to symbol names and numeric encodings. Passing output confirms verbose xlat mode for pidfd info and coredump masks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info-success.c

Purpose: injected-success wrapper for `PIDFD_GET_INFO`. It defines `INJECT_RETVAL 42` and includes the base pidfd info test.

Important APIs/types/functions: Inherits `do_ioctl_fd`, `skip_ioctls`, `injected_pidfd_get_info_decode_checks`, `struct pidfd_info`, mask constants, and versioned command encodings from `ioctl_pidfd_get_info.c`.

Control flow: with injection arguments, the included `main` skips until `PIDFD_GET_INFO` returns the injected value, then runs the synthetic decoder matrix for masks, versioned struct sizes, pid/creds/cgroup/exit/coredump/signal/code/support fields.

State and persistence behavior: no real pidfd is needed; all output data is explicitly written into a local `pidfd_info` buffer.

Dependencies/integration points: exercises strace syscall injection and pidfd info UAPI xlat tables.

Risks and test signals: requires correct injection setup. Passing output confirms success-path parsing of every known `pidfd_info` field and legacy struct-size variants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_get_info.c

Purpose: tests decoding of the `PIDFD_GET_INFO` ioctl, including real pidfd calls and an extensive injected-success matrix for all known masks and struct-size versions.

Important APIs/types/functions: Uses `syscall(__NR_pidfd_open)`, `ioctl`, `struct pidfd_info`, `linux/pidfd.h`, `PIDFD_INFO_*`, `PIDFD_COREDUMP_*`, `PIDFD_GET_INFO`, undersize/oversize `_IOC` command encodings, `do_ioctl_fd`, `print_pidfd_info`, `skip_ioctls`, and `injected_pidfd_get_info_decode_checks`.

Control flow: non-injected mode opens a pidfd for self, checks invalid fd, EFAULT pointer, undersized command, oversized command, and normal command with `PIDFD_INFO_PID`, printing returned masks and optional creds/cgroup fields. Injected mode optionally exits when no args are supplied, otherwise locks onto injected return and runs crafted cases for unknown/all masks, pid, creds, cgroupid, supported mask, exit status decoding, coredump masks, coredump signal/code, all-known combined mask, and version 0/1/2 command sizes.

State and persistence behavior: non-injected mode creates a transient pidfd for the current process; injected mode mutates only local `pidfd_info`. No persistent state.

Dependencies/integration points: depends on recent pidfd UAPI, syscall-number support, signal/status decoding, xlat modes, and syscall injection.

Risks and test signals: kernel support may be absent or return different supported masks; injected path protects decoder coverage from kernel variability. Passing output confirms pidfd info command sizing, mask-driven field selection, exit/coredump formatting, and xlat mode compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_get_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_namespace.c -->
# sources/test-tools/strace/tests/ioctl_pidfd_namespace.c

Purpose: tests `PIDFD_GET_*_NAMESPACE` ioctl command decoding for all namespace selectors exposed by `linux/pidfd.h`, plus an unknown pidfd ioctl fallback.

Important APIs/types/functions: Uses `ioctl`, `linux/pidfd.h`, `do_ioctl`, `sprintrc`, `struct strval32`, and command constants `PIDFD_GET_CGROUP_NAMESPACE`, `PIDFD_GET_IPC_NAMESPACE`, `PIDFD_GET_MNT_NAMESPACE`, `PIDFD_GET_NET_NAMESPACE`, `PIDFD_GET_PID_NAMESPACE`, `PIDFD_GET_PID_FOR_CHILDREN_NAMESPACE`, `PIDFD_GET_TIME_NAMESPACE`, `PIDFD_GET_TIME_FOR_CHILDREN_NAMESPACE`, `PIDFD_GET_USER_NAMESPACE`, `PIDFD_GET_UTS_NAMESPACE`, and `_IOC(_IOC_NONE, 0xff, 0xfe, 0xfd)`.

Control flow: builds a command table and an argument table containing `0` and `0xfacefeeddeadbeef`. For each command/argument pair it calls `ioctl(-1, cmd, arg)` and prints the command through `XLAT_SEL`, the raw argument as hex, and the `sprintrc` result. It ends with the standard strace test marker.

State and persistence behavior: no pidfd or namespace fd is opened; all calls use fd `-1`, so the test has no kernel namespace side effects. The only mutable state is the last `errstr`.

Dependencies/integration points: depends on pidfd namespace UAPI constants and strace xlat decoding for pidfd namespace command names.

Risks and test signals: header availability for newer namespace selectors can vary. Passing output confirms command-name recognition, raw argument formatting, and unknown pidfd ioctl fallback on EBADF paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_pidfd_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_ptp-Xabbrev.c

Purpose: abbreviated-xlat variant for PTP ioctl decoding. It defines `XLAT_ABBREV 1` and includes the base PTP test.

Important APIs/types/functions: Inherits all PTP command coverage from `ioctl_ptp.c`; local behavior changes xlat rendering through `XLAT_ABBREV`.

Control flow: runtime is the base `test_no_device` matrix with abbreviated symbolic output for commands, flags, clock ids, and enum values.

State and persistence behavior: local PTP structs only; fd `-1` avoids device state.

Dependencies/integration points: validates strace abbreviated xlat mode for PTP decoders.

Risks and test signals: exact xlat format is the signal. Passing output confirms PTP fields remain decoded under abbreviated xlat settings.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_ptp-Xraw.c

Purpose: raw-xlat variant for PTP ioctl decoding. It defines `XLAT_RAW 1` before including the base test.

Important APIs/types/functions: Inherits PTP UAPI structs and command matrix from `ioctl_ptp.c`; raw mode changes command and flag formatting.

Control flow: base PTP no-device tests run with raw numeric xlat output, including unknown command sweeps and all major PTP struct families.

State and persistence behavior: no persistent state; local buffers and invalid fd only.

Dependencies/integration points: validates strace raw xlat behavior for PTP ioctl commands and flags.

Risks and test signals: command numeric encodings are sensitive to header definitions. Passing output confirms raw mode does not bypass struct decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_ptp-Xverbose.c

Purpose: verbose-xlat variant for PTP ioctl decoding. It defines `XLAT_VERBOSE 1` before including `ioctl_ptp.c`.

Important APIs/types/functions: Inherits the base PTP test and uses verbose xlat formatting for commands, flags, clock ids, and enum values.

Control flow: same no-device PTP matrix as the base file, but expected output includes both numeric and symbolic information where xlat macros support it.

State and persistence behavior: local structs only; no PTP device is opened.

Dependencies/integration points: validates strace `-X verbose` output with PTP-specific decoders.

Risks and test signals: fragile to xlat naming changes. Passing output confirms verbose xlat formatting across the PTP command surface.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success-Xabbrev.c

Purpose: abbreviated-xlat injected-success PTP variant. It defines `XLAT_ABBREV 1` and includes `ioctl_ptp-success.c`.

Important APIs/types/functions: Inherits `INJECT_RETVAL 42` and all PTP test helpers from the base file.

Control flow: locks onto injected `PTP_CLOCK_GETCAPS`, then runs the PTP matrix with success-style read buffers and abbreviated xlat formatting.

State and persistence behavior: local PTP buffers only; injected return simulates successful reads.

Dependencies/integration points: combines syscall injection, PTP decoder coverage, and abbreviated xlat output.

Risks and test signals: requires injection arguments and stable xlat names. Passing output confirms abbreviated success-path PTP decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success-Xraw.c

Purpose: raw-xlat injected-success PTP variant. It defines `XLAT_RAW 1` and includes the success wrapper.

Important APIs/types/functions: Inherits PTP structures, command matrix, and `INJECT_RETVAL 42` behavior from `ioctl_ptp.c` via `ioctl_ptp-success.c`.

Control flow: after injection lock, every PTP read/write scenario prints raw numeric xlat values while still showing successful output-buffer decoding.

State and persistence behavior: local test buffers only; injection simulates kernel success.

Dependencies/integration points: validates raw xlat mode with PTP success-path decoding.

Risks and test signals: numeric command encodings and struct layouts are the expected-output contract. Passing output confirms raw mode plus injected reads remain coherent.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success-Xverbose.c

Purpose: verbose-xlat injected-success PTP variant. It defines `XLAT_VERBOSE 1` and includes `ioctl_ptp-success.c`.

Important APIs/types/functions: Inherits all base PTP helpers and `INJECT_RETVAL 42`; local effect is verbose xlat rendering.

Control flow: injection setup locks onto `PTP_CLOCK_GETCAPS`, then the full PTP matrix runs with read buffers decoded as successes and verbose command/flag xlat strings.

State and persistence behavior: local PTP structs only; no real device state.

Dependencies/integration points: combines strace injection, PTP decoder coverage, and verbose xlat formatting.

Risks and test signals: sensitive to xlat table wording and header values. Passing output confirms verbose PTP success-path decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success.c -->
# sources/test-tools/strace/tests/ioctl_ptp-success.c

Purpose: syscall-injection success wrapper for PTP ioctl decoding. It defines `INJECT_RETVAL 42` and includes `ioctl_ptp.c`.

Important APIs/types/functions: Inherits `sys_ioctl`, `test_no_device`, and all PTP UAPI struct coverage from the base file.

Control flow: the included `main` requires a skip count, loops on `PTP_CLOCK_GETCAPS` until the injected return appears, then runs the base PTP no-device matrix with `errstr` annotated as injected and read-style structs printed as if successful.

State and persistence behavior: local test memory only; injection simulates device success.

Dependencies/integration points: validates strace syscall injection with PTP ioctl decoders.

Risks and test signals: injection setup must match expected retval. Passing output confirms success branches for caps, sys offsets, precise/extended timestamps, pin descriptors, and other PTP structs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp.c -->
# sources/test-tools/strace/tests/ioctl_ptp.c

Purpose: comprehensive PTP clock ioctl decoder test covering capabilities, external timestamp, periodic output, PPS, system offset, pin functions, precise timestamps, extended timestamps, unknown commands, xlat modes, and injected success.

Important APIs/types/functions: Uses `sys_ioctl`, `print_lltime`, `check_bad_ptr`, `test_no_device`, PTP structs `ptp_clock_caps`, `ptp_sys_offset`, `ptp_sys_offset_extended`, `ptp_sys_offset_precise`, `ptp_extts_request`, `ptp_perout_request`, `ptp_pin_desc`, and xlat tables for external timestamp flags, periodic output flags, pin functions, and clock ids.

Control flow: optional injection lock loops on `PTP_CLOCK_GETCAPS`. `test_no_device` sweeps unknown PTP command numbers and directions, probes NULL/bad pointers, then exercises `PTP_CLOCK_GETCAPS{,2}`, `PTP_EXTTS_REQUEST{,2}`, `PTP_PEROUT_REQUEST{,2}`, `PTP_ENABLE_PPS{,2}`, `PTP_SYS_OFFSET{,2}`, `PTP_PIN_[GS]ETFUNC{,2}`, `PTP_SYS_OFFSET_PRECISE{,2,_CYCLES}`, and `PTP_SYS_OFFSET_EXTENDED{,2,_CYCLES}` with crafted timestamps, flags, reservations, and truncation boundaries.

State and persistence behavior: all state is allocated test structs; fd `-1` avoids device state. Injected mode simulates successful output fields and before/after decoding.

Dependencies/integration points: depends on `linux/ptp_clock.h`, xlat tables, time formatting helpers, xlat mode macros, and syscall injection.

Risks and test signals: time-width differences, header versions, reserved-field policies, and xlat modes create many expected-output variants. Passing output confirms PTP command recognition, nested timestamp formatting, array truncation, flags/enums, pointer handling, and success/error direction behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_random.c -->
# sources/test-tools/strace/tests/ioctl_random.c

Purpose: tests random-device ioctl decoding for entropy counters, entropy addition, pool reset/clear/reseed, and unknown random ioctl commands.

Important APIs/types/functions: Uses `linux/random.h`, `struct rand_pool_info`, `RNDGETENTCNT`, `RNDADDTOENTCNT`, `RNDADDENTROPY`, `RNDZAPENTCNT`, `RNDCLEARPOOL`, `RNDRESEEDCRNG`, and `xlat/random_ioctl_cmds.h`.

Control flow: initializes a `rand_pool_info` union with `entropy_count=3`, `buf_size=8`, and buffer `"12345678"`, then calls each random ioctl on fd `-1`, printing pointer or dereferenced argument forms. It finishes with an unknown `_IO('R', 0xff)` command.

State and persistence behavior: no random pool state is modified due to invalid fd; only local union and integer state exist.

Dependencies/integration points: validates strace random ioctl xlat tables and variable-length `rand_pool_info` decoding.

Risks and test signals: command aliases can affect names. Passing output confirms entropy buffer decoding, pointer classification, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-success.c -->
# sources/test-tools/strace/tests/ioctl_rtc-success.c

Purpose: injected-success variant for RTC ioctl decoding. It defines `INJECT_RETVAL 42` and includes `ioctl_rtc.c`.

Important APIs/types/functions: Inherits RTC command arrays, `struct rtc_time`, `rtc_wkalrm`, `rtc_pll_info`, `rtc_param`, and helper functions from the base file.

Control flow: included `main` first locks onto injected `RTC_AIE_OFF`, then runs all RTC command groups with successful read-path decoding and injected return text.

State and persistence behavior: local RTC structs only; injection simulates successful kernel writes to output buffers.

Dependencies/integration points: validates syscall injection with RTC decoder output.

Risks and test signals: requires correct injection skip count. Passing output confirms RTC read-ioctl struct expansion under success conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-v.c -->
# sources/test-tools/strace/tests/ioctl_rtc-v.c

Purpose: verbose RTC ioctl variant. It defines `VERBOSE 1` before including `ioctl_rtc.c`.

Important APIs/types/functions: Inherits all RTC helpers from the base file; verbose mode mainly affects `print_rtc_time`, adding weekday, yearday, and daylight-saving fields.

Control flow: same command matrix as `ioctl_rtc.c`, with verbose time struct output for alarm, read/set time, and wake alarm commands.

State and persistence behavior: local RTC structs only; invalid fd prevents hardware changes.

Dependencies/integration points: validates strace verbose expected output for RTC time structures.

Risks and test signals: field values come from deterministic fill patterns. Passing output confirms verbose RTC time field rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc.c -->
# sources/test-tools/strace/tests/ioctl_rtc.c

Purpose: comprehensive RTC ioctl decoder test covering no-argument commands, scalar/pointer long commands, time/alarm/wake alarm structs, PLL info, voltage-low flags, NVRAM alias, and generic `RTC_PARAM_{GET,SET}`.

Important APIs/types/functions: Uses `do_ioctl`, `do_ioctl_ptr`, `skip_ioctls`, `print_rtc_time`, `linux/rtc.h`, fallback `struct rtc_param`, `RTC_AIE_*`, `RTC_PIE_*`, `RTC_UIE_*`, `RTC_WIE_*`, `RTC_EPOCH_*`, `RTC_IRQP_*`, `RTC_ALM_*`, `RTC_RD_TIME`, `RTC_SET_TIME`, `RTC_WKALM_*`, `RTC_PLL_*`, `RTC_VL_*`, and `RTC_PARAM_*`.

Control flow: optional injection locks on `RTC_AIE_OFF`. The main path iterates no-arg, scalar, pointer-long, and pointer command arrays; probes NULL and EFAULT-style pointers; fills and prints `rtc_time`, `rtc_wkalrm`, and `rtc_pll_info`; tests voltage-low flag combinations; emits `NVRAM_INIT`; then runs `RTC_PARAM_GET/SET` with crafted params for features, correction, backup switch mode, and unknown params.

State and persistence behavior: local test buffers only. Invalid fd prevents RTC device changes; injection enables successful read-output forms.

Dependencies/integration points: depends on RTC UAPI, feature/backup-switch xlat tables, verbose macro, and syscall injection.

Risks and test signals: newer RTC params and feature bits vary by headers. Passing output confirms direction-aware RTC struct decoding, verbose time formatting, feature/flag xlat handling, and unknown param fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_scsi.c -->
# sources/test-tools/strace/tests/ioctl_scsi.c

Purpose: tests legacy SCSI generic ioctl command decoding outside the `SG_IO` v3/v4 focused tests.

Important APIs/types/functions: Guarded by `HAVE_SCSI_SG_H`; uses `scsi/sg.h`, xlat `scsi_sg_commands.h`, and macros for no-arg, NULL-arg, int-by-value, and int-by-pointer command forms. It covers commands such as sg driver id/version, timeout, reserved size, low DMA, scatter-gather tables, queue depth, command queuing, dxfer, and other `SG_*` controls.

Control flow: compiles to a skip main when SCSI headers are unavailable. Otherwise it allocates integer buffers, issues each command on fd `-1`, and prints command-specific expected EBADF output with decoded scalar or pointer arguments.

State and persistence behavior: local integers only; invalid fd prevents SCSI device state changes.

Dependencies/integration points: depends on SCSI generic UAPI and strace xlat tables.

Risks and test signals: header availability and command deprecation can affect coverage. Passing output confirms names and argument shapes for classic SCSI generic ioctls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_seccomp--pidns-translation.c

Purpose: pid-namespace translation variant for seccomp user notification ioctl decoding. It defines `PIDNS_TRANSLATION` and includes `ioctl_seccomp.c`.

Important APIs/types/functions: Inherits `SECCOMP_IOCTL_NOTIF_*`, `struct seccomp_notif`, `seccomp_notif_resp`, `seccomp_notif_addfd`, and pidns helper printing from the base file.

Control flow: base seccomp matrix runs with pidns leader output and translated PID suffixes for notification `pid` fields.

State and persistence behavior: transient local structs and opened `/dev/null`/`/dev/zero` fds only.

Dependencies/integration points: integrates pid namespace translation with seccomp ioctl decoder output.

Risks and test signals: pid namespace harness affects expected prefixes and pid annotations. Passing output confirms seccomp notification pids are translated in the right fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-success.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-success.c

Purpose: injected-success variant for seccomp user notification ioctl decoding. It defines `INJECT_RETVAL 1` and includes the base seccomp test.

Important APIs/types/functions: Inherits all seccomp notification structs and command coverage from `ioctl_seccomp.c`; injection changes `INJ_STR` and success branches.

Control flow: included `main` can early-exit without injection args; otherwise it locks onto injected `SECCOMP_IOCTL_NOTIF_RECV`, then executes unknown command, receive/send/id-valid/addfd/set-flags cases as success-return output.

State and persistence behavior: local structs and two controlled fds for `/dev/null` and `/dev/zero`; injection simulates successful notification operations.

Dependencies/integration points: validates strace injection for seccomp ioctl decoders.

Risks and test signals: injection retval is `1`, not `42`, so harness configuration matters. Passing output confirms success-path struct before/after rendering for seccomp notifications.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xabbrev.c

Purpose: combined seccomp variant enabling fd path printing (`-y`), injected success, pid namespace translation, and abbreviated xlat output.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `ioctl_seccomp-y-success--pidns-translation.c`, which layers `PIDNS_TRANSLATION`, `INJECT_RETVAL 1`, and `PRINT_PATHS`.

Control flow: base seccomp matrix runs after injection lock with pidns leaders, fd paths for addfd source descriptors, and abbreviated xlat strings.

State and persistence behavior: local seccomp structs plus controlled `/dev/null` and `/dev/zero` fds.

Dependencies/integration points: exercises combined strace options: injection, `-y`, pidns translation, and `-X abbrev`.

Risks and test signals: compounded formatting modes make expected output brittle. Passing output confirms these options compose correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xraw.c

Purpose: combined seccomp variant for fd paths, injected success, pidns translation, and raw xlat output.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes the `-y` success pidns wrapper, inheriting seccomp notification commands and structs.

Control flow: executes the base seccomp matrix with injected success and raw numeric command/flag values while preserving fd path and pid translation decorations.

State and persistence behavior: local structs and controlled fds only.

Dependencies/integration points: validates composition of `-X raw`, `-y`, pidns translation, and syscall injection.

Risks and test signals: raw numeric encodings must match headers. Passing output confirms raw mode does not break fd-path or pidns annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xverbose.c

Purpose: combined seccomp variant for fd paths, injected success, pidns translation, and verbose xlat output.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes the layered `ioctl_seccomp-y-success--pidns-translation.c` wrapper.

Control flow: base seccomp notification tests run with injected success, path-annotated fds, translated PIDs, and verbose command/flag xlat formatting.

State and persistence behavior: local notification/addfd structs and `/dev/null`/`/dev/zero` fds only.

Dependencies/integration points: validates combined strace option behavior for seccomp ioctls.

Risks and test signals: output is highly formatting-sensitive. Passing output confirms verbose xlat coexists with fd-path and pidns decorations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation.c

Purpose: seccomp wrapper combining pid namespace translation with the `-y` injected-success variant.

Important APIs/types/functions: Defines `PIDNS_TRANSLATION` and includes `ioctl_seccomp-y-success.c`, which itself enables `INJECT_RETVAL 1` and fd path printing.

Control flow: included base test runs after injection lock; output includes pidns leaders/suffixes and source fd path annotations in `SECCOMP_IOCTL_NOTIF_ADDFD`.

State and persistence behavior: local structs and controlled fds only; no real seccomp listener is required due to injection.

Dependencies/integration points: composes pidns translation, fd-path rendering, and injection in seccomp ioctl expected output.

Risks and test signals: expected text depends on `/proc/self/fd` availability and pidns harness. Passing output confirms combined annotations are placed correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xabbrev.c

Purpose: fd-path plus injected-success seccomp variant with abbreviated xlat output.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `ioctl_seccomp-y-success.c`, inheriting seccomp user notification structs and commands.

Control flow: base seccomp test runs in success mode with fd path annotations and abbreviated xlat command/flag strings.

State and persistence behavior: local structs and controlled fds only.

Dependencies/integration points: validates `-y`, injection, and `-X abbrev` together.

Risks and test signals: sensitive to both fd path availability and xlat wording. Passing output confirms option composition.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xabbrev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xraw.c

Purpose: fd-path plus injected-success seccomp variant with raw xlat output.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes `ioctl_seccomp-y-success.c`.

Control flow: runs the seccomp success matrix with raw numeric command/flag output while printing fd paths for addfd source descriptors.

State and persistence behavior: local structs and controlled fds only.

Dependencies/integration points: validates `-y`, injection, and `-X raw` composition.

Risks and test signals: numeric command encodings are header-sensitive. Passing output confirms raw mode and fd-path annotations both work.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xverbose.c

Purpose: fd-path plus injected-success seccomp variant with verbose xlat output.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes `ioctl_seccomp-y-success.c`.

Control flow: executes the base seccomp notification matrix in injected success mode, printing fd paths and verbose xlat strings.

State and persistence behavior: local notification/addfd structs plus opened `/dev/null` and `/dev/zero` descriptors.

Dependencies/integration points: validates `-y`, injection, and `-X verbose` output composition.

Risks and test signals: exact output is formatting-sensitive. Passing output confirms verbose xlat does not interfere with path-annotated fd fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xverbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success.c

Purpose: injected-success wrapper for the fd-path (`-y`) seccomp ioctl test.

Important APIs/types/functions: Defines `INJECT_RETVAL 1` and includes `ioctl_seccomp-y.c`, which sets `PRINT_PATHS` and `/proc/self/fd` availability checks.

Control flow: after injection lock, the base seccomp test runs with successful return strings and fd path annotations in addfd output.

State and persistence behavior: local seccomp structs and controlled descriptors; injection simulates seccomp listener success.

Dependencies/integration points: combines syscall injection and strace fd-path output.

Risks and test signals: requires `/proc/self/fd` and injection args. Passing output confirms success-path seccomp decoding with `srcfd=<path>` annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y.c

Purpose: fd-path (`-y`) variant of seccomp ioctl decoding. It enables path printing and skips when `/proc/self/fd/` is unavailable.

Important APIs/types/functions: Defines `PRINT_PATHS 1`, `SKIP_IF_PROC_IS_UNAVAILABLE`, and includes `ioctl_seccomp.c`. Inherited key structs are `seccomp_notif`, `seccomp_notif_resp`, and `seccomp_notif_addfd`.

Control flow: base seccomp test runs normally but `PATH_FMT` includes `<%s>` for `srcfd` fields, so controlled fds 0 and 42 print `/dev/null` and `/dev/zero` in addfd cases.

State and persistence behavior: opens and duplicates `/dev/null` and `/dev/zero` to deterministic fds; otherwise local structs only.

Dependencies/integration points: integrates seccomp ioctl decoding with strace fd-path annotation behavior.

Risks and test signals: depends on `/proc/self/fd` and deterministic fd duplication. Passing output confirms `-y` paths are included only where expected.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp.c -->
# sources/test-tools/strace/tests/ioctl_seccomp.c

Purpose: comprehensive decoder test for seccomp user notification ioctls: receive, send, id-valid, addfd, set-flags, unknown commands, pid namespace translation, fd path output, and injected success.

Important APIs/types/functions: Uses `sys_ioctl`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `linux/seccomp.h`, `struct seccomp_notif`, `seccomp_notif_resp`, `seccomp_notif_addfd`, `SECCOMP_IOCTL_NOTIF_RECV`, `SEND`, `ID_VALID`, `ADDFD`, `SET_FLAGS`, audit arch xlat tables, and fd/path macros.

Control flow: prints a synchronized starting marker, optionally locks onto injected success, sweeps unknown seccomp ioctl directions/sizes, then tests `NOTIF_RECV` with NULL, bad pointer, zeroed and populated notifications including syscall args and audit arch variants. It tests `NOTIF_SEND` responses, `NOTIF_ID_VALID` and wrong-direction command, sets up deterministic fds for `/dev/null` and `/dev/zero`, tests `NOTIF_ADDFD` with flags and fd paths, and finishes with `NOTIF_SET_FLAGS`.

State and persistence behavior: process-local notification structs plus fd table manipulation for descriptors 0 and 42. No real seccomp listener state is required on invalid fd; injection simulates success.

Dependencies/integration points: depends on seccomp UAPI, audit arch definitions, pid namespace helpers, fd path availability, kernel fcntl flags, xlat modes, and syscall injection.

Risks and test signals: many formatting dimensions interact: xlat mode, pidns translation, fd paths, injection, arch-specific syscall numbers, and `/proc` availability. Passing output confirms strace correctly decodes nested seccomp notification structs, signed errors, flags, fds, PIDs, syscall metadata, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v3.c -->
# sources/test-tools/strace/tests/ioctl_sg_io_v3.c

Purpose: tests SCSI generic `SG_IO` v3 (`struct sg_io_hdr`) decoding, including interface id validation, transfer directions, flags, iovec/data buffers, residual counts, status fields, and info flags.

Important APIs/types/functions: Guarded by `HAVE_SCSI_SG_H`; uses `scsi/sg.h`, `sys/uio.h`, `struct sg_io_hdr`, `SG_IO`, `SG_DXFER_*`, `SG_FLAG_*`, `SG_INFO_*`, `TAIL_ALLOC_OBJECT`, `fill_memory`, and iovec arrays.

Control flow: tests NULL, EFAULT, wrong interface id, partial interface id, then a valid `'S'` header with filled fields. It prints separate cases for TO_DEV, FROM_DEV, iovec transfers, direct byte buffers, TO_FROM_DEV before/after buffer display, flags combinations, residual truncation, status and driver/host fields.

State and persistence behavior: local SG header, iovec, and buffer memory only; invalid fd prevents device I/O.

Dependencies/integration points: depends on SCSI SG headers and strace SG_IO v3 decoder.

Risks and test signals: only compiles when `scsi/sg.h` is available. Passing output confirms direction-sensitive buffer decoding, iovec truncation, flags/info xlat, and fallback for invalid interface ids.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v4.c -->
# sources/test-tools/strace/tests/ioctl_sg_io_v4.c

Purpose: tests SCSI generic `SG_IO` v4 (`struct sg_io_v4`) decoding used by block SCSI generic interfaces.

Important APIs/types/functions: Uses `linux/bsg.h`, `struct sg_io_v4`, `SG_IO`, protocol/subprotocol fields, request/response/dout/din pointers, iovec counts, flags, info, durations, residual fields, and SCSI xlat command support.

Control flow: probes NULL, EFAULT, invalid guard, partial guard, then valid guard `'Q'` with crafted protocol, subprotocol, request/response pointers, iovec/direct transfer buffers, dout/din transfer lengths, residuals, flags, status, and info fields.

State and persistence behavior: local v4 header and buffers only; invalid fd prevents real SCSI I/O.

Dependencies/integration points: validates strace SG_IO v4 decoder against Linux BSG UAPI and iovec printing helpers.

Risks and test signals: struct layout and flags are header-sensitive. Passing output confirms guard/protocol decoding, request/response pointer fields, bidirectional transfer formatting, residual handling, and flags/info expansion.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock.c -->
# sources/test-tools/strace/tests/ioctl_sock.c

Purpose: broad socket ioctl decoder test for generic file/socket ownership commands and networking `SIOC*`/`ifreq` commands.

Important APIs/types/functions: Uses `socket(AF_INET, SOCK_STREAM, 0)`, `do_ioctl`, `test_ptr`, `test_int`, `test_str`, `test_ifreq`, `struct ifreq`, `sockaddr_in`, `ifmap`, `FIOGETOWN/FIOSETOWN`, `SIOCGPGRP/SIOCSPGRP`, `SIOCATMARK`, route/ARP/RARP/bridge/bond/VLAN/ethtool/MII/hwtstamp commands, and many `SIOCGIF*`/`SIOCSIF*` variants.

Control flow: opens an AF_INET socket, then `test_ptr` probes NULL and bad pointers for a long command list plus unknown `_IO(0x89, 0xff)`. `test_int` checks int pointer commands on a real socket. `test_str` checks bridge name string truncation. `test_ifreq` builds macro-generated source cases for integer, flag, string, address, hardware address, and map union members, emits EFAULT and structured `ifreq` output, queries loopback ifindex/name, and tests bridge add/delete interface by index.

State and persistence behavior: creates one transient socket and local `ifreq` structs. Set-style ioctls are mostly issued on fd `-1`, avoiding network configuration changes; real socket queries read loopback metadata.

Dependencies/integration points: depends on networking headers, loopback interface assumptions, `IFINDEX_LO_STR`, sockaddr and flag xlat tables, and optional command macros from current headers.

Risks and test signals: command availability and loopback naming/index can vary. Passing output confirms pointer handling, ifreq union member selection, string truncation, sockaddr/hwaddr/map formatting, and interface-index/name decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock_gifconf.c -->
# sources/test-tools/strace/tests/ioctl_sock_gifconf.c

Purpose: focused test for `SIOCGIFCONF` decoding of `struct ifconf` and returned `struct ifreq` arrays.

Important APIs/types/functions: Uses `socket`, `ioctl`, `struct ifconf`, `struct ifreq`, `sockaddr_in`, `SIOCGIFCONF`, `print_ifc_len`, and `print_ifconf`. `MAX_STRLEN` is set to 1 to force compact array output.

Control flow: opens an AF_INET socket, allocates an ifconf and buffers, probes NULL and bad pointers, calls `SIOCGIFCONF` with zero/positive lengths and NULL/non-NULL buffers, and prints length changes plus decoded first interface address entries when the call succeeds.

State and persistence behavior: reads interface configuration only; local buffers hold kernel output. No network configuration is modified.

Dependencies/integration points: depends on available AF_INET socket, network interfaces, and strace `ifconf` array decoder.

Risks and test signals: output may vary by interface set, but expected harness constrains printed length/count. Passing output confirms `ifc_len` before/after handling, NULL buffer behavior, array truncation, and sockaddr decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock_gifconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tee.c -->
# sources/test-tools/strace/tests/ioctl_tee.c

Purpose: tests Trusted Execution Environment (`TEE_IOC_*`) ioctl decoding, including version, shared memory allocation/registration, open/invoke/cancel/close session, supplementary receive, and parameter arrays.

Important APIs/types/functions: Uses `linux/tee.h`, `struct tee_ioctl_version_data`, `tee_ioctl_shm_alloc_data`, `tee_ioctl_shm_register_data`, `tee_ioctl_buf_data`, `tee_ioctl_open_session_arg`, `tee_ioctl_invoke_arg`, `tee_ioctl_cancel_arg`, `tee_ioctl_supp_recv_arg`, `tee_ioctl_param`, UUID helpers, `CHK_NULL`, `CHK_BUF`, and generated buffer-with-params structs.

Control flow: calls each TEE ioctl on invalid fd with NULL, bad, and crafted buffers. It fills UUIDs, session ids, command ids, cancellation ids, shared memory ids/sizes/flags, and 14 params spanning none/value/memref temp/registered modes with known and unknown attribute bits. It checks both input-only and before/after forms depending on ioctl direction.

State and persistence behavior: local stack/tail-allocated TEE structs only; invalid fd avoids TEE device state.

Dependencies/integration points: depends on TEE UAPI and strace xlat tables for TEE implementation ids, gen caps, shm flags, and param attrs.

Risks and test signals: TEE struct layouts and attribute flags can change. Passing output confirms nested buffer decoding, UUID formatting, param-array truncation, flag/enumeration expansion, and pointer fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios-v.c -->
# sources/test-tools/strace/tests/ioctl_termios-v.c

Purpose: verbose variant of the termios ioctl decoder test. It defines `VERBOSE 1` and includes `ioctl_termios.c`.

Important APIs/types/functions: Inherits the base termios ioctl matrix and termios/termios2/winsize/serial-related structures from `ioctl_termios.c`; local behavior is compile-time verbose formatting.

Control flow: runtime follows the base termios test but takes verbose branches for structure fields and flag sets, producing expanded expected output for terminal attributes and related ioctls.

State and persistence behavior: local test buffers and invalid fds dominate; verbose mode changes only printed expectations.

Dependencies/integration points: integrates strace verbose output mode with terminal ioctl decoders and platform termios headers.

Risks and test signals: depends on the included base file outside this group and platform-specific termios definitions. Passing output confirms verbose terminal ioctl structure rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_termios-v.c -->
