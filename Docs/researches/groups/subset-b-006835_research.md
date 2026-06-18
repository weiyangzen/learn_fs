# subset-b-006835 HID selftest research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_bpf.c

## Purpose
`hid_bpf.c` is a kselftest binary for the kernel HID-BPF integration path. It creates a synthetic UHID device, loads the generated `hid.skel.h` libbpf skeleton, attaches selected HID `struct_ops` programs from `progs/hid.c`, then validates that raw HID input, report descriptor fixups, hw request hooks, output report hooks, and injected input reports behave as expected through the kernel-visible `hidraw` node.

## Important APIs, types, and functions
The `FIXTURE(hid_bpf)` state owns a `struct uhid_device`, an open `hidraw_fd`, the BPF skeleton pointer, and up to three attached `bpf_link` objects. `load_programs()` is the central helper: it opens the skeleton, finds BPF programs by name, enables autoload, finds each corresponding struct_ops map by removing the `hid_` prefix from the program name, writes the fixture HID id into the first struct_ops field, disables autoattach for maps, loads the object, attaches struct_ops links, attaches tracing programs, and opens the matching hidraw node. `detach_bpf()` centralizes close/detach/destroy cleanup.

## Control flow
Fixture setup calls `setup_uhid()` with the shared test report descriptor. Tests then choose either `LOAD_BPF` for syscall-style BPF program tests or `LOAD_PROGRAMS()` for struct_ops hooks. Event tests inject UHID input with `uhid_send_event()`, read from `hidraw`, and assert mutations performed by BPF. Raw request and output report tests trigger kernel paths via `HIDIOCGFEATURE` or `write()`, validating filter errno, transformed return sizes, and no-recursion behavior. The report descriptor test attaches `hid_rdesc_fixup`, then re-reads the descriptor through hidraw.

## State and persistence
State is intentionally transient: synthetic devices live only for the fixture, BPF links are destroyed at teardown, and only one temporary BPF pin path (`/sys/fs/bpf/hid_first_event`) is used and immediately removed. Shared BPF data variables such as `callback_check` and `callback2_check` are read through the skeleton to prove program execution.

## Dependencies and integration points
This file depends on libbpf, kselftest harness macros, `hid_common.h`, the generated BPF skeleton, `/dev/uhid`, `/dev/hidraw*`, sysfs HID discovery, and kernel support for HID-BPF kfuncs and struct_ops. It integrates with `progs/hid.c` by name conventions linking `hid_*` programs to struct_ops maps.

## Risks and test signals
Risk concentrates around ordering assumptions, sysfs/hidraw discovery races, kernel feature availability, and error-code contracts. The tests provide strong signals for attach lifecycle, multi-program ordering, changed report IDs, user-triggered BPF syscalls, raw/output report filtering, recursion guards, workqueue event injection, and descriptor rewriting. Failures here usually indicate kernel HID-BPF ABI regressions rather than ordinary userspace logic bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_common.h

## Purpose
`hid_common.h` is the shared C harness for HID kselftests in this directory. It provides the synthetic HID report descriptor, UHID device creation/destruction, asynchronous UHID event processing, hidraw node discovery/opening, and common synchronization objects used by both `hidraw.c` and `hid_bpf.c`.

## Important APIs, types, and functions
`struct uhid_device` records the random physical id, UHID fd, kernel HID id, bus/vendor/product ids, and reader thread id. The global `rdesc` describes a vendor-defined HID device with two report IDs, input reports, output reports, and feature reports; `feature_data` supplies canned GET_REPORT replies. `setup_uhid()` creates `/dev/uhid`, emits `UHID_CREATE`, resolves the kernel HID id, and starts the listener. `uhid_send_event()` emits `UHID_INPUT2`. `open_hidraw()`, `get_hidraw()`, `get_hid_id()`, and `match_sysfs_device()` connect the synthetic device to sysfs and `/dev/hidrawN`.

## Control flow
UHID events are consumed by `uhid_read_events_thread()`, which polls the UHID fd until `UHID_STOP`. `uhid_event()` handles lifecycle notifications, captures output reports into `output_report`, replies to GET_REPORT using `feature_data`, and acknowledges SET_REPORT. `uhid_start_listener()` waits on `uhid_started` before tests proceed, ensuring the kernel has accepted the device.

## State and persistence
The file has process-global mutexes/condition variables for start and output synchronization, a process-global `output_report[10]`, and a `uhid_stopped` flag. These are test-process state only, but because they are global, fixtures rely on serialized harness behavior and careful teardown.

## Dependencies and integration points
It includes Linux `uhid.h`, `hidraw.h`, pthreads, poll, sysfs, and kselftest harness headers. It is the contract layer beneath all C HID tests in the subset and exposes shared descriptor data used by ioctl assertions.

## Risks and test signals
Key risks are sysfs race windows, random `dev_id` collisions, short retry loops under heavy load, and condition-variable misuse if UHID events are delayed. Positive signals include successful UHID start, stable HID id discovery, output report notification, and correct GET/SET report replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hidraw.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hidraw.c

## Purpose
`hidraw.c` is a kselftest binary for the generic hidraw userspace ABI. It creates a UHID-backed HID device and verifies raw reads, writes, revoke behavior, polling, descriptor ioctls, device info ioctls, feature/input/output report ioctls, string ioctls, and invalid ioctl command validation.

## Important APIs, types, and functions
The `FIXTURE(hidraw)` stores a `struct uhid_device` and `hidraw_fd`. `FIXTURE_SETUP` calls `setup_uhid()` with a USB VID/PID distinct from the BPF tests and opens the hidraw node. `close_hidraw()` and teardown handle cleanup. Tests use Linux hidraw ioctls such as `HIDIOCREVOKE`, `HIDIOCGRDESCSIZE`, `HIDIOCGRDESC`, `HIDIOCGRAWINFO`, `HIDIOCGFEATURE`, `HIDIOCSFEATURE`, `HIDIOCGINPUT`, `HIDIOCSINPUT`, `HIDIOCGOUTPUT`, `HIDIOCSOUTPUT`, `HIDIOCGRAWNAME`, `HIDIOCGRAWPHYS`, and `HIDIOCGRAWUNIQ`.

## Control flow
The basic event test injects a UHID input report and confirms the same bytes are readable from hidraw. Revoke tests first prove the fd works, call `HIDIOCREVOKE`, then assert reads/writes/ioctls fail with `ENODEV` and polling reports `POLLHUP`. Descriptor tests compare size and content against `rdesc`, including a deliberately small descriptor buffer. Report ioctl tests use the UHID listener's canned GET_REPORT behavior, expecting success for report id 1 and `EIO` for invalid report ids. Invalid ioctl tests handcraft bad `_IOC_TYPE`, `_IOC_NR`, and `_IOC_DIR` encodings and assert kernel error codes.

## State and persistence
The file does not persist state beyond the test process. It relies on `hid_common.h` globals for output-report synchronization and feature data. Each fixture instance owns its temporary UHID device and hidraw fd, and teardown destroys both.

## Dependencies and integration points
It integrates with `/dev/uhid`, `/dev/hidrawN`, sysfs matching from `hid_common.h`, the kernel hidraw driver, pthread condition variables, and kselftest harness macros. It is an ABI regression suite for userspace tools that depend on hidraw.

## Risks and test signals
Risks include ioctl error-code expectations changing, old kernels lacking `HIDIOCREVOKE`, nonblocking reads returning before injected data, and environment permissions. Strong signals include descriptor byte equality, exact revoke semantics, correct report forwarding through UHID, and string truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hidraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid.c

## Purpose
`progs/hid.c` contains the BPF programs exercised by `hid_bpf.c`. It defines HID `struct_ops` callbacks, syscall-test programs, fentry tracing, and a BPF workqueue path to validate the HID-BPF kernel kfunc surface.

## Important APIs, types, and functions
The file uses `SEC("?struct_ops/...")` programs for `hid_device_event`, `hid_rdesc_fixup`, `hid_hw_request`, and `hid_hw_output_report`, with matching `SEC(".struct_ops.link") struct hid_bpf_ops` maps. It uses `hid_bpf_get_data()`, `hid_bpf_allocate_context()`, `hid_bpf_release_context()`, `hid_bpf_hw_request()`, `hid_bpf_hw_output_report()`, `hid_bpf_input_report()`, and `hid_bpf_try_input_report()`. Syscall programs share `struct hid_hw_request_syscall_args` with userspace tests.

## Control flow
Simple event callbacks mutate report bytes and return either the original or changed size. Insert-order programs verify `BPF_F_BEFORE` and normal insertion ordering. `hid_rdesc_fixup` copies an added descriptor fragment at offset 73 and changes a usage byte. Raw/output request hooks either return negative filter errors, forward requests to the device, rewrite data, or validate recursion prevention. `hidraw_open` captures the current hidraw `struct file *` so hooks can distinguish hidraw-originated requests. The workqueue path stores a `bpf_wq` in a hash map, starts a sleepable callback, allocates a HID context, and injects an additional input report.

## State and persistence
BPF global variables `callback_check`, `callback2_check`, and `current_file` persist for the lifetime of the loaded object. The `hmap` BPF hash map persists workqueue state while attached. All state is destroyed when userspace detaches and destroys the skeleton.

## Dependencies and integration points
It depends on custom HID helper declarations in `hid_bpf_helpers.h`, vmlinux CO-RE types, libbpf section conventions, and kernel HID-BPF kfunc exports. It is tightly coupled to program/map names expected by `hid_bpf.c`.

## Risks and test signals
Risks include ABI drift in `struct hid_bpf_ctx` or kfunc prototypes, verifier constraints around sleepable callbacks and workqueues, and brittle struct_ops naming conventions. Test signals include exact report byte rewrites, return sizes, errno propagation, recursion guard behavior, and descriptor fixup visibility through hidraw.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid_bpf_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid_bpf_helpers.h

## Purpose
`hid_bpf_helpers.h` is the local compatibility header that lets the HID-BPF test programs compile against BPF CO-RE while overriding selected `vmlinux.h` HID types with stable test-local definitions.

## Important APIs, types, and functions
The header temporarily renames `vmlinux.h` symbols, defines `BPF_NO_KFUNC_PROTOTYPES`, includes `vmlinux.h`, then restores the names and declares local `enum hid_report_type`, `struct hid_device`, `struct bpf_wq`, `struct hid_bpf_ctx`, `enum hid_class_request`, and `struct hid_bpf_ops`. It declares weak kfunc symbols for HID data access, context allocation/release, hw request/output/input report helpers, try-input helper, and BPF workqueue helpers.

## Control flow
There is no runtime control flow. Its compile-time control flow is macro based: hide vmlinux definitions, include BTF-derived declarations, undefine the aliases, then provide the exact structs and prototypes needed by `progs/hid.c`.

## State and persistence
The header itself has no state. It defines struct layouts that determine what BPF programs can read and write through CO-RE and through struct_ops maps.

## Dependencies and integration points
It integrates with libbpf helper headers, BPF tracing macros, `linux/const.h`, kernel BTF, and the HID-BPF kernel ABI. The struct_ops layout must match enough of the kernel contract for map initial values and callback slots to work.

## Risks and test signals
The main risk is layout or prototype drift from the kernel. Because these declarations shadow `vmlinux.h`, mismatches may produce verifier failures, wrong field access, or silent bad tests. Successful loading of `progs/hid.c`, correct `hid_id` injection, and passing kfunc behavior are the practical validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/progs/hid_bpf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/run-hid-tools-tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/run-hid-tools-tests.sh

## Purpose
`run-hid-tools-tests.sh` is the kselftest launcher for the Python hid-tools based HID test suite under `tests/`. It provides dependency checks and emits TAP output expected by the kernel selftest runner.

## Important APIs, types, and functions
The script is POSIX shell. It defines `KSELFTEST_SKIP_TEST=4`, checks `python3`, `pytest`, `pytest_tap`, and `hidtools`, sets `TARGET=${TARGET:=.}`, prints `TAP version 13`, and invokes `python3 -u -m pytest $PYTEST_XDIST ./tests/$TARGET --tap-stream --udevd`.

## Control flow
Execution is linear. Missing prerequisites produce a `[SKIP]` message and exit with the kselftest skip code. When dependencies exist, pytest is run on either the whole `tests` directory or a target selected by environment variable. `PYTEST_XDIST` is passed through for optional parallelism, and `--udevd` asks the pytest fixture to start udevd.

## State and persistence
The script persists no state. Runtime effects are delegated to pytest fixtures, which may create UHID devices, udev rules, and temporary kernel-facing objects during tests.

## Dependencies and integration points
It integrates kselftest TAP conventions with Python pytest, pytest-tap, hid-tools, and the local test package. It assumes tests are run from the HID selftest directory or another location where `./tests/$TARGET` resolves correctly.

## Risks and test signals
Risks include unquoted environment variables, dependency version mismatches handled later in `conftest.py`, and environment-specific udevd paths. Positive signal is TAP stream production; skip exits distinguish missing userspace dependencies from kernel/test failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/run-hid-tools-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/__init__.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/__init__.py

## Purpose
`tests/__init__.py` marks the HID pytest directory as a Python package and carries a note that it exists so sphinx-apidoc can document the directory.

## Important APIs, types, and functions
It exports no runtime APIs, classes, fixtures, or constants.

## Control flow
There is no executable control flow beyond module import.

## State and persistence
There is no state or persistence behavior.

## Dependencies and integration points
Its practical integration point is Python package import resolution, enabling relative imports such as `.base`, `.base_device`, and `.test_keyboard` from sibling tests.

## Risks and test signals
Risk is minimal. Removing it could affect package-relative imports and documentation tooling. The test signal is indirect: pytest collection and relative imports continue to work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base.py

## Purpose
`base.py` is the central pytest harness for hid-tools UHID tests. It defines application-to-evdev matching rules, a UHID test device subclass, dataclasses describing kernel modules and HID-BPF objects, the base test fixture lifecycle, debugging helpers, and udev-rule management.

## Important APIs, types, and functions
`application_matches` maps HID application names to `EvdevMatch` requirements and exclusions. `UHIDTestDevice` prefixes device names and supplies those matches to `BaseDevice`. `HidBpf` and `KernelModule` describe optional setup. `BaseTestCase.TestUhid` provides reusable fixtures (`load_kernel_module`, `new_uhdev`, `context`, `check_taint`) and assertions (`assertInputEventsIn`, `assertInputEvents`, `assertName`). `load_hid_bpfs()` and `unload_hid_bpfs()` invoke `udev-hid-bpf` for in-kernel HID-BPF objects. `HIDTestUdevRule` creates and later removes `/run/udev/rules.d` rules to ignore test UHID devices in libinput and hid-bpf auto loading.

## Control flow
For each test, `context` creates the device, installs udev rules, processes skip markers, creates the kernel device, dispatches UHID events until readiness or timeout, optionally loads HID-BPF programs, yields to the test, then unloads BPF programs and tears down. `check_taint` snapshots `/proc/sys/kernel/tainted` before each test and asserts it is unchanged after.

## State and persistence
Class-level lists (`kernel_modules`, `hid_bpfs`) configure subclasses. Per-test state is `self.uhdev`. `HIDTestUdevRule` is a singleton with a reference count and a temporary rules file that persists only while the session/test contexts are active.

## Dependencies and integration points
The file depends on pytest, libevdev, hidtools, system tools (`modprobe`, `udevadm`, `systemd-hwdb`, `udev-hid-bpf`), and `BaseDevice`. It is the integration layer between Python tests, UHID, udev, evdev, kernel modules, and HID-BPF assets.

## Risks and test signals
Risks include root permissions, udev timing, unavailable modules, stale udev rules, and kernel taint changes. Strong signals are successful device creation, evdev node matching, no leftover sync events at creation, clean BPF load/unload, and unchanged kernel taint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base_device.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base_device.py

## Purpose
`base_device.py` defines the hid-tools backed virtual UHID device abstraction used by Python HID tests. It wraps sysfs files, LED and power_supply classes, pyudev readiness tracking, evdev node opening/matching, and the `BaseDevice` subclass of `hidtools.uhid.UHIDDevice`.

## Important APIs, types, and functions
`SysfsFile` provides typed `int_value` and `str_value` accessors. `LED` and `PowerSupply` expose selected sysfs attributes. `HidReadiness`, `HIDIsReady`, and `UdevHIDIsReady` track bind/unbind/remove events from pyudev; the latter registers a monitor fd with `UHIDDevice._append_fd_to_poll()`. `EvdevMatch` expresses required/excluded event bits and input properties. `EvdevDevice` reads uevent metadata, opens `/dev/input/event*` nonblocking through libevdev, and checks application matches. `BaseDevice` constructs the HID report descriptor, exposes `input_nodes`, `get_evdev()`, readiness, and lifecycle hooks.

## Control flow
Device tests create a `BaseDevice` subclass, call hidtools to create the kernel device, then repeatedly dispatch UHID/udev events. When `input_nodes` is first accessed, the class starts a helper thread to keep dispatching UHID events while opening evdev nodes, avoiding kernel SET_REPORT timeouts caused by device opens. `get_evdev()` either returns the sole input node or selects the one matching the requested HID application.

## State and persistence
`UdevHIDIsReady` keeps class-level pyudev context, monitor, and a HID-id keyed readiness dictionary. `BaseDevice` keeps cached evdev nodes, open state, started state, parsed report descriptor, default report id, and input metadata. Open evdev fds are closed on stop, close, and destruction.

## Dependencies and integration points
It depends on pyudev, libevdev, hidtools, sysfs, `/dev/input`, and Linux UHID. It is the base layer consumed by keyboard, mouse, multitouch, tablet, gamepad, and device-specific tests.

## Risks and test signals
Risks include global readiness state collisions, pyudev event loss, nonblocking flag handling, sysfs layout assumptions, and thread dispatch races. Good signals are stable bind counts, correct evdev matching, closed fds after tests, and no 5-second SET_REPORT stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base_device.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base_gamepad.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base_gamepad.py

## Purpose
`base_gamepad.py` provides reusable virtual gamepad and joystick device models for the pytest HID suite. It maps HID usages into evdev button and axis expectations and generates input reports with persistent button, stick, and hat-switch state.

## Important APIs, types, and functions
`InvalidHIDCommunication` reports attempts to set unsupported buttons. `GamepadData` is a dynamic data container passed to hidtools report creation. `AxisMapping` maps HID axis names to libevdev `EV_ABS` bits. `BaseGamepad` extends `BaseDevice`, defining default button maps, stick maps, report state, `create_report()`, and `event()`. `JoystickGamepad` adjusts button mappings and right-stick axes to joystick conventions.

## Control flow
Tests call `event()` with optional left/right stick tuples, hat-switch value, and button dictionary. `create_report()` validates button ids, merges `None` values with prior state, stores axes into a `GamepadData` instance, sets `hatswitch`, and delegates actual report serialization to `BaseDevice.create_report()`. The resulting report is sent via `call_input_event()`.

## State and persistence
Each device instance persists `_buttons`, `left`, `right`, and `hat_switch` values across generated reports so tests can model partial state changes. `default_reportID` is inherited from `BaseDevice` and can be set by subclasses.

## Dependencies and integration points
It depends on libevdev, hidtools bus metadata, and `BaseDevice`. It is consumed by `test_gamepad.py` and device-specific classes to test kernel HID parsing into evdev events.

## Risks and test signals
Risks include mismatched HID usage names, wrong evdev mappings for device classes, and persistent state hiding test setup mistakes. Signals are button press/release events, axis movement events only when values differ from neutral, and hat-switch mapping to `ABS_HAT0X/Y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base_gamepad.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/conftest.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/conftest.py

## Purpose
`conftest.py` configures the HID pytest suite. It enforces hidtools version requirements, manages session-level udev rule cleanup, disables core dumps, optionally starts systemd-udevd, registers custom markers, and parameterizes tests over installed HID kernel modules.

## Important APIs, types, and functions
Autouse fixtures include `hidtools_version_check()`, `udev_rules_session_setup()`, `setup_rlimit()`, and `start_udevd()`. `pytest_configure()` registers `skip_if_uhdev`. `pytest_generate_tests()` detects a `usbVidPid` fixture and fills it from `modinfo` aliases in installed HID modules. `pytest_addoption()` adds `--udevd`.

## Control flow
Before every test, the hidtools version check skips if the package is missing or older than `0.12`. Session setup enters `HIDTestUdevRule.instance()` so the reference-counted rule manager can clean up after tests. If `--udevd` is set, a `systemd-udevd` subprocess is launched for the session and killed afterward. Parameter generation scans `/lib/modules/<release>/kernel/drivers/hid/*.ko`, parses HID USB modaliases, and creates ids for parametrized tests.

## State and persistence
The file changes process resource limits to disable core files. It can start a session subprocess and relies on the singleton udev-rule manager for temporary rule state. It does not write persistent repository files.

## Dependencies and integration points
It integrates pytest with packaging, platform, resource limits, subprocess tools, installed kernel modules, and the base udev rule helper.

## Risks and test signals
Risks include hard-coded udevd path, missing `modinfo`, compressed module names not matching `*.ko`, and broad exception handling in the version check. Signals include clean pytest collection, correct skip reasons, generated USB VID/PID parameter sets, and no core dump artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/descriptors_wacom.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/descriptors_wacom.py

## Purpose
`descriptors_wacom.py` is a data module containing raw HID report descriptors for Wacom tablet models and firmware variants. The descriptors are used by Wacom-oriented HID tests to emulate real devices with realistic pen, pad, touch, feature, and vendor report layouts.

## Important APIs, types, and functions
The module defines large byte-list constants: `wacom_pth660_v145`, `wacom_pth660_v150`, `wacom_pth860_v145`, `wacom_pth860_v150`, and `wacom_pth460_v105`. The v150 variants are shallow copies of the v145 descriptors with one report-count byte changed for report ID 20. There are no functions or classes.

## Control flow
There is no runtime control flow except list construction at import time and the two copy-plus-mutate operations. Descriptor comments document HID item meaning, report IDs, usage pages, units, report counts, and known errata such as missing physical maxima.

## State and persistence
The descriptor lists are module globals. Because v150 variants are copied before mutation, they do not alter their v145 source lists. Consumers should treat these lists as read-only; accidental mutation would affect later tests within the same Python process.

## Dependencies and integration points
The file has no imports. It integrates by being imported into Wacom tests, where the byte lists feed hidtools report descriptor parsing and UHID device creation.

## Risks and test signals
Risks include descriptor byte drift from actual hardware, accidental mutation of globals, and very large hand-maintained arrays where offset edits are brittle. Test signals appear indirectly: Wacom tests should create the right evdev devices, expose expected capabilities, and exercise feature/report handling for each model variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/descriptors_wacom.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_apple_keyboard.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_apple_keyboard.py

## Purpose
`test_apple_keyboard.py` emulates an Apple Wireless Keyboard and validates `hid-apple` function-key behavior, especially interactions between the Fn state report, top-row function keys, media/application mappings, and arrow-key page navigation mappings.

## Important APIs, types, and functions
`KERNEL_MODULE` identifies `hid-apple`. `AppleKeyboard` extends `ArrayKeyboard`, supplies a multi-report descriptor with keyboard, consumer, battery, Fn/vendor, media, and feature reports, sets Bluetooth Apple VID/PID input info, and defines `send_fn_state()` to emit report ID 17 with usage `0xff0003`. `TestAppleKeyboard` extends `TestArrayKeyboard`, loads the apple module, creates the virtual device, and contains focused event-order tests.

## Control flow
Tests create the Apple keyboard through the common UHID fixture. They send key array reports with `uhdev.event([...])`, send Fn state reports with `send_fn_state()`, read evdev sync events, and assert both emitted events and persistent evdev key values. Cases cover plain F4 mapping to `KEY_ALL_APPLICATIONS`, Fn+F4 mapping to `KEY_F4`, releasing Fn before function key release, pressing Fn after a top-row key, multiple function keys, transition cases, and Fn+UpArrow producing `KEY_PAGEUP`.

## State and persistence
State lives in the virtual keyboard and kernel input device: pressed key arrays, Fn key state, and evdev key values. No repository or disk state is written. The test intentionally checks persistent key values after intermediate reports to catch stuck-key regressions.

## Dependencies and integration points
It depends on `test_keyboard.ArrayKeyboard`, `TestArrayKeyboard`, libevdev, hidtools bus metadata, and the `hid-apple` kernel module. It integrates with the common uhid/udev/evdev lifecycle from `base.py`.

## Risks and test signals
Risks include hid-apple keymap changes, event ordering subtleties, and dependence on exact Apple descriptor semantics. Strong signals are expected `EV_KEY` transitions, absence of incorrect alternate key states, and stable behavior across press/release ordering permutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_apple_keyboard.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_gamepad.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_gamepad.py

## Purpose
`test_gamepad.py` validates kernel HID parsing and evdev mapping for several gamepad/joystick descriptors, including generic Saitek and Asus devices plus a FR-TEC Raptor Mach 2 path that requires a HID-BPF descriptor fixup.

## Important APIs, types, and functions
`BaseTest.TestGamepad` is a reusable test class layered on `base.BaseTestCase.TestUhid`. It sends an initial neutral report, then checks individual buttons, dual-button transitions, left/right stick axes, and hat-switch directions. Device classes include `SaitekGamepad`, `AsusGamepad`, and `RaptorMach2Joystick`; they define report descriptors, bus/vendor/product identity, supported button ids, axis mappings, and special hat scaling for the Raptor. `TestRaptorMach2Joystick` lists `HidBpf("FR-TEC__Raptor-Mach-2.bpf.o", True)`.

## Control flow
For each concrete test class, pytest creates a virtual device. The autouse fixture sends an empty report to initialize axes. Button tests build reports through `BaseGamepad.event()`, read evdev events, and assert key values. Axis tests move sticks through representative values and check corresponding absolute events. Hat-switch tests are skipped when the descriptor lacks the usage and otherwise validate north/east/south/west mappings. The Raptor test path loads a HID-BPF program and waits for descriptor fixup rebind readiness.

## State and persistence
Gamepad state persists in the virtual device between reports: held buttons, stick coordinates, and hat-switch null/current values. Kernel evdev state is asserted after transitions. No persistent files are created.

## Dependencies and integration points
It depends on pytest markers, libevdev, `base_gamepad.py`, hidtools, and the common HID-BPF loader for Raptor. It integrates with kernel HID input mapping, optional in-tree `drivers/hid/bpf/progs` assets, and evdev reporting.

## Risks and test signals
Risks include descriptor quirks, neutral-axis assumptions, BPF program availability, and differing joystick/gamepad evdev mappings. Test signals are exact button press/release events, axis events only for meaningful changes, correct hat-switch signs, and successful BPF-assisted device readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_gamepad.py -->
