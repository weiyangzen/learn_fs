# subset-b-006838 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_tablet.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_tablet.py

Purpose: this pytest module exercises Linux HID tablet/stylus handling through synthetic UHID devices. It validates pen proximity/contact state machines, barrel-button behavior, invert/eraser behavior, reported distance through `ABS_DISTANCE`, and several real-device descriptor regressions. The file also covers devices that require HID-BPF fixups, such as XP-Pen and Huion tablets.

Important APIs, types, and functions: `BtnTouch`, `ToolType`, and `BtnPressed` encode evdev-level button/tool concepts. `PenState` is the central state machine; `from_evdev()` reconstructs state from an evdev device, `apply()` validates event sequences between sync reports, and the static transition factories provide legal, tolerated, and intentionally broken transition scenarios. `Pen` is the mutable report-value carrier. `PenDigitizer` extends `base.UHIDTestDevice`, selects fields from parsed HID descriptors, converts a `Pen` into HID reports via `create_report()`, and stubs feature `get_report()` / `set_report()`. `BaseTest.TestTablet` supplies the reusable pytest tests. Device subclasses such as `GXTP_pen`, `XPPen_ArtistPro16Gen2_28bd_095b`, `XPPen_Artist24_28bd_093a`, `Huion_Kamvas_Pro_19_256c_006b`, and `Wacom_2d1f_014b` model quirks by adjusting report data or injecting intermediate states.

Control flow: each concrete `Test*` class implements `create_device()` with a descriptor and bus/vendor/product tuple. The base fixture creates the UHID device, then parametrized tests drive `_test_states()`: start out of range, optionally scribble coordinates, move the synthetic pen into each requested `PenState`, submit a HID report, collect evdev events with `next_sync_events()`, and verify both final evdev state and every intermediate state between `SYN_REPORT`s. Skip markers gate button, invert, and Z/distance tests on descriptor usages.

State and persistence: state is in-process and per-device. `Pen` retains current values plus `_old_values` so out-of-range reports can zero fields and later restore coordinates/pressure. Some device classes retain `previous_state` or `prev_tip_state` to emulate firmware history. There is no on-disk persistence.

Dependencies and integration points: depends on pytest, libevdev, hid-tools parsing/report creation, `base.UHIDTestDevice`, `base.HidBpf`, and the Linux UHID/evdev stack. HID-BPF objects named in `hid_bpfs` integrate with driver-side descriptor/event fixes.

Risks: transition checks are strict and can flag intentional kernel behavior changes; large inline descriptors are hard to audit; device emulation logic can mask descriptor bugs; `validate_transitions()` has a suspicious tail path where remaining events reuse the last `sync_events` slice rather than the unsynced `events` list. Tests also rely on specific evdev names/usages.

Test signals: pass signals include expected `BTN_TOOL_PEN`/`BTN_TOOL_RUBBER`, `BTN_TOUCH`, barrel buttons, coordinates, and `ABS_DISTANCE` values. Failures indicate invalid state transitions, duplicate tool/touch/button events, missing expected usages, unsupported HID-BPF behavior, or wrong final evdev state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_tablet.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_usb_crash.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_usb_crash.py

Purpose: this small pytest module is a crash regression harness. It creates UHID-emulated devices that claim `BUS_USB` identity and verifies that bound HID drivers do not dereference real USB-only structures when the backing device is actually UHID.

Important APIs, types, and functions: `USBDev` extends `base.UHIDTestDevice` with a minimal mouse report descriptor, an overridden `is_ready()` that avoids waiting for udev-created evdev nodes, and `get_evdev()` returning a sentinel because this test cares about kernel survival rather than input events. `TestUSBDevice.new_uhdev()` consumes a generated `usbVidPid` fixture, loads the named kernel module, and returns `USBDev(input_info=(3, vid, pid))`. `test_creation()` is intentionally just `assert True`.

Control flow: `conftest.py` supplies `(module, vid, pid)` parameter tuples. The fixture loads the candidate module and creates the fake USB UHID device. If driver probing crashes or taints the kernel, shared fixtures such as `check_taint` and the test environment catch it. The test body only asserts that execution reached user space after device creation.

State and persistence: state is limited to fixture attributes `module`, `vid`, and `pid`, the loaded kernel module, and the live UHID device. No persistent files are written.

Dependencies and integration points: integrates with pytest, the local HID selftest `base` framework, kernel module loading, UHID, and the generated `usbVidPid` fixture. The report descriptor is a generic relative mouse descriptor with three buttons and X/Y axes.

Risks: success is mostly negative evidence; if crash/taint detection is disabled, the test can pass despite missing coverage. The fake descriptor is deliberately simple, so it may not exercise deeper driver paths beyond probe and basic parsing. The typo in the comment does not affect behavior.

Test signals: any kernel crash, machine freeze, taint, module-load failure, or UHID creation failure is the meaningful failure. A normal pytest pass means fake USB UHID creation did not hit the known crash class for that module/device tuple.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_usb_crash.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_wacom_generic.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_wacom_generic.py

Purpose: this pytest module tests the Wacom driver's generic HID code path, meaning Wacom-like devices decoded from descriptors rather than explicit device-table handling. It covers pen naming, physical units/ranges, pointer-vs-direct properties, side switches, heartbeat reports, pad/touch-ring reports, and multitouch confidence handling.

Important APIs, types, and functions: `KERNEL_MODULE` requests the `wacom` module. `ProximityState.fill()` maps out/proximity/range into `inrange` and `wacomsense` report bits. `Buttons` and `ToolID` are `attrs` value objects that fill report fields for side switches and serial/tool IDs. `PhysRange.contains()` validates descriptor unit/range metadata. `BaseTablet` extends `base.UHIDTestDevice` and implements `create_report()`, `event()`, heartbeat and pad report creation, Wacom-specific evdev node matching, and feature-report offset generation. `OpaqueTablet`, `OpaqueCTLTablet`, and `PTHX60_Pen` are descriptor-backed device models. Test classes layer reusable assertions through `BaseTest.TestTablet`, `PenTabletTest`, `TouchTabletTest`, and `DirectTabletTest`.

Control flow: each test constructs a synthetic UHID device, sends reports through `call_input_event()`, then compares evdev output using `sync_and_assert_events()`. Descriptor physical validation iterates parsed input/feature/output reports and checks required usages against unit/range expectations. `TestPTHX60_Pen` parametrizes real PTH descriptor variants, xfails known physical-range errata, checks heartbeat reports for no events, and verifies pad ring/key events. `TestDTH2452Tablet` extends multitouch helpers and replays timelines for contact ID 0, confidence false, confidence loss, and confidence gain.

State and persistence: `BaseTablet` stores current `buttons`, `toolid`, `proximity`, pad ring/key state, and feature offset. Multitouch assertions inspect evdev slot state, but no data persists beyond the test process and kernel input state.

Dependencies and integration points: depends on `descriptors_wacom`, `hidtools.hut.HUT`, `hidtools.hid.HidUnit`, pytest, attrs, libevdev, the local UHID base, and `test_multitouch`. It integrates directly with the kernel Wacom driver and evdev node naming conventions.

Risks: inline descriptors are large and brittle; exact evdev names/properties may change with driver naming updates; physical range expectations intentionally xfail on known errata for PTH devices; confidence timelines assume stable slot allocation semantics. Because helper state is sticky, omitted fields in a report mean unchanged state rather than cleared state.

Test signals: expected signals include evdev key/ABS/MSC events, no spurious heartbeat sync, correct `INPUT_PROP_POINTER`/`INPUT_PROP_DIRECT`, valid descriptor unit metadata, expected pad `ABS_WHEEL` rotation, and correct multitouch tracking IDs/slot release when confidence changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_wacom_generic.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/vmtest.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/vmtest.sh

Purpose: this shell script runs HID selftests inside a virtme-ng virtual machine. It can optionally build the kernel, HID-BPF programs, and HID selftest binaries from the current source tree before booting a VM, then run `hid_bpf`, `hidraw`, and/or the Python HID pytest suite.

Important APIs, functions, and variables: `SCRIPT_DIR` and `KERNEL_CHECKOUT` locate the selftest tree and kernel root. `HID_BPF_TEST`, `HIDRAW_TEST`, and `HID_BPF_PROGS` point to test binaries/programs. `TEST_NAMES` and `TEST_DESCS` define runnable tests. `usage()`, `die()`, `check_args()`, `check_deps()`, and `check_vng()` validate invocation and environment. `handle_build()` runs `vng --kconfig`, optional remote build args, kernel build, HID-BPF build, and selftest build. `vm_start()`, `vm_wait_for_ssh()`, `vm_mount_bpffs()`, and `vm_ssh()` manage the guest. `run_test()` wraps each test with dmesg error/oops checks. `log()` and helpers prefix setup/host/guest output and append to a temp log.

Control flow: option parsing accepts build, remote host/container, qemu path, shell mode, verbosity, and selected test names. The script checks dependencies and vng version, optionally builds, boots the VM, waits for SSH, mounts bpffs, and either opens an interactive root shell or emits KTAP-style output for each selected test. It runs the test function by name and converts pass/skip/fail counts into a final kselftest exit code.

State and persistence: temporary pid/log files are created under `/tmp`; `cleanup()` terminates QEMU using the pidfile and removes it. VM state exists for the script lifetime. Build mode mutates the kernel tree by generating `.config`, building BPF objects, and building selftests.

Dependencies and integration points: requires `virtme-ng` (`vng`), busybox, qemu, pkill, ssh, pytest, kselftest KTAP helpers, `hid_bpf`, `hidraw`, and a kernel tree. It uses virtme-ng SSH config in `${HOME}/.cache/virtme-ng`.

Risks: only vng versions 1.36 and 1.37 are tested; `eval test_"${name}" "$@"` depends on earlier validation; log redirection is verbosity-dependent; dmesg error count increases from unrelated guest activity can fail tests; build mode may be expensive and host/container args are shell-expanded through arrays except the podman prefix string.

Test signals: KTAP plan/output, per-test `ok`/`not ok`, dmesg oops/error detection, and a final `SUMMARY: PASS=... SKIP=... FAIL=...` plus log path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/vmtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/Makefile

Purpose: this kselftest Makefile registers and builds the IA-64 `aliasing-test` program.

Important APIs and variables: `TEST_PROGS := aliasing-test` declares the executable as a runnable selftest program. `all: $(TEST_PROGS)` makes the default target build it. `include ../lib.mk` imports kselftest build/install/run rules. `clean` removes the generated executable.

Control flow: GNU make resolves `all`, lets the default implicit C compilation build `aliasing-test` from `aliasing-test.c`, and relies on `../lib.mk` for kselftest packaging and execution integration.

State and persistence: creates the `aliasing-test` binary in the source/build directory and deletes it on `make clean`.

Dependencies and integration points: integrates with the kselftest make framework and the adjacent C source. It is architecture-scoped by directory rather than by conditional logic in this Makefile.

Risks: no explicit compiler flags are set here; behavior depends on inherited `lib.mk` and environment. Removing only `$(TEST_PROGS)` is simple but broad through `rm -fr`.

Test signals: successful build produces the executable; kselftest execution signals come from the C program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/aliasing-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/aliasing-test.c

Purpose: this IA-64-oriented selftest exercises historically troublesome `/dev/mem`, PCI legacy memory, PCI ROM, and `/proc/bus/pci` mmap/read paths. The goal is not that every range be readable; the goal is that mapping or reading failures are handled without machine checks or inaccessible-device failures.

Important APIs and functions: `map_mem()` opens a path, optionally issues `PCIIOC_MMAP_IS_MEM` for `/proc/bus/pci/*`, mmaps a requested range, optionally touches every int in the mapping into global `sum`, unmaps, and returns 0 for success, positive for not mappable, and negative for access/setup errors. `scan_tree()` recursively finds matching files and applies `map_mem()`. `read_rom()` enables a sysfs ROM by writing `"1"` and reads it into `buf`. `scan_rom()` recursively finds `rom` files and invokes `read_rom()`. `main()` orchestrates fixed `/dev/mem` ranges and recursive scans.

Control flow: `main()` tests low memory ranges separately, treats whole-1MiB mapping as allowed to fail positively, scans `/sys/class/pci_bus` `legacy_mem`, scans `/sys/devices` `rom`, then scans `/proc/bus/pci` function names matching `??.?`. Recursive walkers allocate child paths, skip `.`/`..`, branch on filename matches, and OR return codes into a cumulative result.

State and persistence: global `sum` prevents read-touch loops from being optimized away; `buf` holds ROM chunks. The test does not write persistent files, but it writes to sysfs ROM enable files and opens/mmap device memory.

Dependencies and integration points: uses libc directory, mmap, stat, fnmatch, and PCI ioctl APIs; depends on `/dev/mem`, sysfs PCI legacy memory/ROM files, `/proc/bus/pci`, and permissions suitable for raw memory access.

Risks: `map_mem()` leaks `fd` if `mmap()` fails; pointer arithmetic on `void *` is a GNU extension; some recursive error paths return before freeing all allocated entries; `read_rom()` writes two bytes (`"1"` including NUL) to a sysfs attribute. The test is inherently platform/permission sensitive and can be dangerous outside its intended hardware/kernel context.

Test signals: stderr prints `PASS` for readable, mappable, not mappable, or unreadable ROM cases that do not represent access failure, and `FAIL` for inaccessible paths. Exit status is based on the whole `/dev/mem` 1MiB mapping result, so log review is important for recursive scan failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/aliasing-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/Makefile

Purpose: this kselftest Makefile builds and registers the Intel P-state frequency validation test.

Important APIs and variables: it appends `-Wall` to `CFLAGS` and `-lm` to `LDLIBS`, normalizes `ARCH` through `ARCH_PROCESSED`, and only sets `TEST_GEN_FILES := msr aperf` on x86/i386/x86_64. `TEST_PROGS := run.sh` registers the shell driver. `include ../lib.mk` imports kselftest behavior. `$(TEST_GEN_FILES): $(HEADERS)` declares generated binaries depend on kselftest headers.

Control flow: on x86, make builds `msr` and `aperf`; on other architectures it only exposes `run.sh`, whose own runtime check skips non-x86.

State and persistence: generated files are the `msr` and `aperf` binaries in the build output. No custom clean target is needed beyond kselftest framework defaults.

Dependencies and integration points: integrates with the kselftest build system, math library for `aperf.c`, and runtime `run.sh`.

Risks: architecture detection is string-based; generated binaries are omitted on non-x86, so direct manual invocation of `run.sh` outside kselftest build output can fail if binaries are missing.

Test signals: build success on x86 yields `msr` and `aperf`; runtime pass/fail is governed by `run.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/aperf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/aperf.c

Purpose: `aperf.c` is a helper load generator and measurement tool for the Intel P-state selftest. It pins itself to one CPU, reads TSC/APERF/MPERF MSRs before and after a CPU-heavy loop, and estimates effective frequency.

Important APIs and functions: `usage()` prints argument form. `main()` parses one CPU number, opens `/dev/cpu/<cpu>/msr`, sets process affinity using `CPU_ZERO`, `CPU_SET`, and `sched_setaffinity()`, timestamps with `clock_gettime(CLOCK_MONOTONIC)`, reads MSRs with `pread()` at offsets `0x10`, `0xe7`, and `0xe8`, runs a long `sqrt(i)` loop, computes deltas, and prints `runTime` plus `freq`. It includes `kselftest.h` for `KSFT_SKIP`.

Control flow: invalid args or parse errors return 1; missing MSR device returns kselftest skip; affinity/timing failures return 1; otherwise the before/read/load/after/read/compute path exits 0.

State and persistence: no persistent state. It reads MSR device files and consumes CPU. Local variables hold before/after counters and elapsed milliseconds.

Dependencies and integration points: requires x86 MSR device support, likely root or msr permissions, libm, scheduler affinity APIs, and `run.sh`, which launches one instance per CPU.

Risks: return values from `pread()` are unchecked, so short/failed reads can produce bogus output. The `pread()` size arguments for APERF/MPERF use the opposite variable names, though the sizes are the same. The heavy loop duration is fixed and may be excessive or insufficient depending on CPU speed. Division by zero is possible if APERF/MPERF deltas are invalid.

Test signals: stdout lines `runTime:` and `freq:` provide measurement evidence for manual or scripted interpretation; exit 4 means skip due to inaccessible MSR device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/aperf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/msr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/msr.c

Purpose: `msr.c` is a tiny helper that reads and prints `MSR_IA32_PERF_CTL` (`0x199`) for one CPU. `run.sh` uses it to include requested P-state control evidence in result files.

Important APIs and functions: `main()` parses a CPU number, opens `/dev/cpu/<cpu>/msr`, reads eight bytes at offset `0x199` with `pread()`, and prints `msr 0x199: 0x...`.

Control flow: invalid argument count or parse error returns 1; open failure prints perror and returns 1; otherwise it reads and prints the MSR then returns 0.

State and persistence: read-only access to `/dev/cpu/*/msr`; no persistent output except stdout captured by `run.sh`.

Dependencies and integration points: depends on the x86 msr driver/device node and permissions. It is built by the intel_pstate Makefile and invoked by `run.sh`.

Risks: `pread()` return value is not checked, so unavailable or partial reads can print uninitialized data. `strtol()` range and trailing-character validation are minimal. It only reads CPU 0 in the shell driver, which may not reflect every CPU under test.

Test signals: a valid line containing `msr 0x199:` is appended to each `/tmp/result.<freq>` file by `run.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/msr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/run.sh

Purpose: this shell script drives the Intel P-state selftest. It iterates maximum CPU frequency settings from max to min in 100 MHz steps, loads each CPU with `aperf`, captures observed frequencies and `MSR_IA32_PERF_CTL`, then prints a comparison table.

Important APIs, functions, and variables: `EVALUATE_ONLY` allows re-reading existing `/tmp/result.*` files. `ksft_skip=4` implements kselftest skip. `run_test()` launches `./aperf $cpu` for every CPU, sleeps, captures unique `/proc/cpuinfo` MHz lines, appends `./msr 0`, records `/sys/devices/system/cpu/intel_pstate/max_perf_pct`, and waits for jobs. Main code uses `cpupower frequency-info -l`, `cpupower frequency-set -g powersave --max=...`, `/proc/cpuinfo`, and `pr`.

Control flow: skip non-x86, non-root (unless evaluate-only), or missing `cpupower`. Compute marketing, min, and max frequencies. Unless evaluating only, loop over frequency targets and run load capture for each, then restore max. Finally build `/tmp/result.tab` with Target, Actual, Difference, MSR, and scaled max_perf_pct, and print it in five columns.

State and persistence: writes `/tmp/result.freqs`, `/tmp/result.<freq>`, and `/tmp/result.tab`; changes system CPU frequency policy during the run and attempts to restore max at the end. Background `aperf` processes run until completion.

Dependencies and integration points: requires x86, root, `cpupower`, intel_pstate sysfs, `/dev/cpu/*/msr`, `/proc/cpuinfo`, and helper binaries `aperf` and `msr`.

Risks: there is no trap to restore frequency on interruption; `/tmp/result.*` names are shared and can be stale or collide; parsing marketing frequency and cpuinfo MHz is fragile; multiple similar frequency lines can intentionally trigger manual cleanup; `max_cpus=$(nproc-1)` assumes contiguous CPU IDs from zero. The script exits 0 after table generation even if differences are large, so this is more diagnostic than assertive.

Test signals: skip messages for unsupported environments, captured result files per target frequency, and the final printed table. Meaningful failures include missing helpers/MSR access, cpupower errors, and suspicious Target/Actual differences in the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/Makefile

Purpose: this kselftest Makefile builds IOMMUFD selftest binaries.

Important APIs and variables: it sets `CFLAGS += -Wall -O2 -Wno-unused-function`, adds `$(KHDR_INCLUDES)` for kernel UAPI headers, links with `-lcap`, and registers `TEST_GEN_PROGS += iommufd iommufd_fail_nth`. `include ../lib.mk` supplies kselftest rules.

Control flow: make builds the generated programs from corresponding C sources in the directory, using kernel headers and libcap. The generated binaries are installed/run by kselftest infrastructure.

State and persistence: produces `iommufd` and `iommufd_fail_nth` binaries. No runtime state is defined here.

Dependencies and integration points: integrates with kselftest, kernel headers, libcap, and the IOMMUFD test sources. It pairs with the adjacent `config` file for required kernel options.

Risks: libcap is a mandatory link dependency; suppressing unused-function warnings may hide dead helper drift; empty initial `TEST_GEN_PROGS :=` is harmless but redundant.

Test signals: build success yields both binaries; runtime signals come from those binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/config

Purpose: this kselftest config fragment declares kernel options needed to run IOMMUFD selftests, especially the fault-injection variant.

Important entries: `CONFIG_IOMMUFD=y` enables the tested subsystem. `CONFIG_IOMMUFD_TEST=y` enables test support. `CONFIG_FAULT_INJECTION=y`, `CONFIG_FAULT_INJECTION_DEBUG_FS=y`, and `CONFIG_FAILSLAB=y` enable kernel fault injection used by failure-path tests such as `iommufd_fail_nth`.

Control flow: there is no executable flow. Kselftest/virtme/kconfig tooling consumes this fragment when preparing a kernel config for the IOMMU selftests.

State and persistence: it is a static configuration artifact. Its effects appear in the built kernel, not in this file.

Dependencies and integration points: paired with `tools/testing/selftests/iommu/Makefile` and IOMMUFD test binaries. Requires debugfs/fault-injection support in the runtime environment for failure injection coverage.

Risks: forcing built-in `=y` may not match distro modular setups; omitting related IOMMU hardware/backend options can still leave tests skipped or unavailable depending on platform. Fault injection options are unsuitable for some production-style kernels.

Test signals: a kernel built with these options should expose IOMMUFD test functionality and fault-injection controls needed by the generated selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/config -->
