# subset-b-003793 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/Kconfig

## Purpose

This Kconfig file is the HID subsystem configuration hub. It gates the common HID core, userspace interfaces, generic HID binding, haptics, special vendor drivers, sensor hub drivers, HID-BPF, and bus-specific HID transports such as USB, I2C, Intel ISH, AMD SFH, Surface HID, and Intel THC.

## Important APIs, Types, and Functions

The important exported symbols are configuration symbols rather than C APIs. `HID_SUPPORT` is the top-level menu option. `HID` enables the core and depends on `INPUT`; `HIDRAW`, `UHID`, `HID_GENERIC`, `HID_BATTERY_STRENGTH`, and `HID_HAPTIC` toggle core-facing facilities. The long "Special HID drivers" menu maps device/vendor support to module symbols consumed by `drivers/hid/Makefile`, for example `HID_MULTITOUCH`, `HID_WACOM`, `HID_SENSOR_HUB`, and `HID_KUNIT_TEST`. The file sources sub-Kconfig files for `bpf`, `i2c-hid`, `intel-ish-hid`, `amd-sfh-hid`, `surface-hid`, `intel-thc-hid`, and `usbhid`.

## Control Flow

Kconfig evaluation first exposes `HID_SUPPORT`; if selected, it offers the core `HID` symbol and, under `if HID`, the core options and per-device drivers. The final `source` lines import transport and extension menus. `usbhid/Kconfig` is sourced outside the `if HID` block but still inside `HID_SUPPORT`, preserving historical USB HID configuration behavior.

## State and Persistence Behavior

The file persists only build-time choices in kernel configuration. Runtime state is indirect: selecting symbols controls which object files are built and which modules can bind hardware. Defaults such as `HID_GENERIC=y` when `HID=y` determine baseline behavior for devices without special drivers.

## Dependencies and Integration Points

This file integrates with the top-level input stack, kernel module build rules, and subdirectory Kconfigs. Several symbols depend on other subsystems such as `LEDS_CLASS`, `POWER_SUPPLY`, `NEW_LEDS`, `I2C`, `SPI`, `USB_HID`, `BPF`, `BPF_SYSCALL`, `BPF_JIT`, and `KUNIT`. The AMD SFH and HID-BPF entries researched in this item are included through `source` statements near the end.

## Risks and Test Signals

Dependency drift is the main risk: a driver can be selectable while required libraries or transports are absent, or a Makefile object can reference a missing symbol. Test signals include `allmodconfig`, `allyesconfig`, architecture-specific randconfigs, and checking that every `HID_*` symbol referenced by `drivers/hid/Makefile` has a matching Kconfig entry or intentional external definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/Makefile

## Purpose

This Makefile maps HID Kconfig symbols to core HID objects, vendor-specific drivers, test objects, and transport subdirectories. It is the build-time companion to `drivers/hid/Kconfig`.

## Important APIs, Types, and Functions

The primary build targets are `hid.o`, assembled from `hid-core.o`, `hid-input.o`, and `hid-quirks.o`, with optional `hid-debug.o`, `hid-haptic.o`, and `hidraw.o`. `obj-$(CONFIG_HID_BPF) += bpf/` enters the HID-BPF subdirectory. `obj-$(CONFIG_AMD_SFH_HID) += amd-sfh-hid/` enters the AMD SFH transport. Composite targets include `hid-logitech-y`, `hid-wiimote-y`, `hid-picolcd-y`, `hid-uclogic-objs`, `wacom-objs`, and `hid-uclogic-test-objs`.

## Control Flow

Kbuild evaluates each `obj-$(CONFIG_...)` line after Kconfig resolves symbols. Enabled built-in symbols add objects to vmlinux; module symbols build modules. Composite object lists are resolved first, then the corresponding `obj-*` line decides whether the composite target is linked.

## State and Persistence Behavior

The Makefile has no runtime state. Its persistent effect is the kernel image or module set produced by the selected configuration. Composite objects also define linkage boundaries, for example Wacom code is linked as `wacom.o` from `wacom_wac.o` and `wacom_sys.o`.

## Dependencies and Integration Points

It integrates directly with Kconfig symbols in `drivers/hid/Kconfig` and subdirectory Kconfigs. It also routes bus transports to `usbhid/`, `i2c-hid/`, `intel-ish-hid/`, `amd-sfh-hid/`, `surface-hid/`, and `intel-thc-hid/`.

## Risks and Test Signals

Risks are symbol/object mismatches, duplicate object inclusion, and composite object lists that omit a needed source file. Test signals include Kbuild with `CONFIG_HID=y/m`, `CONFIG_HID_BPF=y/m`, `CONFIG_AMD_SFH_HID=y/m`, and randconfig builds that stress optional composites such as force feedback and KUnit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Kconfig

## Purpose

This Kconfig file exposes AMD Sensor Fusion Hub support as a HID transport. The driver presents AMD MP2/SFH sensors as HID sensor devices.

## Important APIs, Types, and Functions

The sole symbol is `AMD_SFH_HID`, a tristate "AMD Sensor Fusion Hub" option. It depends on `X86_64`, `PCI`, and `ACPI`, and depends on `HID`. It selects `AMD_PMF` when `ACPI` is enabled so SFH 1.1 platform information can integrate with AMD platform management.

## Control Flow

When the parent HID Kconfig sources this file, the menu offers `AMD_SFH_HID` only if the platform dependencies hold. Selecting it enables the `amd-sfh-hid/` Makefile target and links the PCI, HID, descriptor, and SFH 1.1 implementation objects.

## State and Persistence Behavior

State is build-time only. At runtime, the resulting `amd_sfh` module binds AMD MP2 PCI IDs and creates HID devices for discovered sensors.

## Dependencies and Integration Points

This option integrates with PCI enumeration, ACPI system firmware, HID core, and AMD PMF. The downstream C code relies on x86-specific CPU family checks and AMD PCI device IDs.

## Risks and Test Signals

The dependency set must prevent builds on unsupported architectures while allowing module builds on supported AMD laptops. Useful test signals are `CONFIG_AMD_SFH_HID=m/y` builds on x86_64, configurations without `AMD_PMF`, and runtime probe logs on MP2 and MP2 1.1 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Makefile

## Purpose

This Makefile builds the AMD SFH HID module from the transport, PCI, descriptor, and SFH 1.1 source files.

## Important APIs, Types, and Functions

`obj-$(CONFIG_AMD_SFH_HID) += amd_sfh.o` defines the module/composite target. `amd_sfh-objs` includes `amd_sfh_hid.o`, `amd_sfh_client.o`, `amd_sfh_pcie.o`, `hid_descriptor/amd_sfh_hid_desc.o`, and the SFH 1.1 files `amd_sfh_init.o`, `amd_sfh_interface.o`, and `amd_sfh_desc.o`. `ccflags-y += -I $(src)/` makes local headers visible to subdirectory files.

## Control Flow

Kbuild links the listed objects into `amd_sfh.o` whenever `CONFIG_AMD_SFH_HID` is enabled. The module entry point comes from `module_pci_driver()` in `amd_sfh_pcie.c`.

## State and Persistence Behavior

The file has no runtime state, but the object list defines which code paths are always present in the driver. SFH 1.1 support is not optional once the driver is built.

## Dependencies and Integration Points

It depends on the parent HID Makefile routing and the Kconfig symbol. The include path supports headers referenced with local subdirectory paths.

## Risks and Test Signals

The key risk is omitting an object that supplies callbacks installed through `amd_mp2_ops`, such as descriptor operations or SFH 1.1 initialization. Build tests should verify both built-in and module configurations, plus clean builds that catch missing generated include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_client.c -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_client.c

## Purpose

`amd_sfh_client.c` is the legacy AMD SFH HID client layer. It discovers MP2 sensors, allocates coherent sensor buffers and HID report buffers, starts sensors through `amd_mp2_ops`, creates synthetic HID devices, services HID get/set report requests, polls sensor input, and tears everything down on remove or suspend.

## Important APIs, Types, and Functions

`amd_sfh_hid_client_init()` is the main initialization path. `amd_sfh_hid_client_deinit()` stops sensors, cancels delayed work, and removes HID devices. `amd_sfh_get_report()` queues report requests in `amdtp_cl_data.req_list`; `amd_sfh_work()` fulfills the last queued feature/input request by calling descriptor callbacks and `hid_input_report()`. `amd_sfh_work_buffer()` periodically pushes input reports for enabled sensors. Static helpers include `amd_sfh_wait_for_response()`, `get_sensor_name()`, `amd_sfh_suspend()`, and `amd_sfh_resume()`.

## Control Flow

Initialization installs descriptor ops with `amd_sfh_set_desc_ops()`, assigns suspend/resume callbacks, asks `amd_mp2_get_sensor_num()` for active sensor IDs, allocates DMA and report buffers, starts each sensor, waits for status, and then probes a HID device for each enabled non-operating-mode sensor. Periodic delayed work reads input reports every `AMD_SFH_IDLE_LOOP` milliseconds. HID core report requests enter through `amd_sfh_get_report()` and are processed asynchronously by `amd_sfh_work()`.

## State and Persistence Behavior

Persistent per-device state lives in `amdtp_cl_data` and `amd_mp2_dev`: sensor IDs, DMA addresses, report descriptors, feature/input buffers, sensor status, request completion flags, and delayed work items. Request nodes are transient heap objects. The MP2 mutex guards report queue and buffer access. Device-managed allocations are freed by devres; explicit cleanup frees selected buffers on init failure and removes HID devices.

## Dependencies and Integration Points

This file depends on Linux DMA mapping, HID core, workqueues, lists, and the MP2 operation table from `amd_sfh_common.h`. It integrates with `amd_sfh_hid.c` for HID low-level device creation and wakeups, `amd_sfh_pcie.c` for start/stop/response callbacks, and `hid_descriptor/amd_sfh_hid_desc.c` for descriptors and report materialization.

## Risks and Test Signals

Risks include request-list assumptions (`list_last_entry()` requires a nonempty list), report-size zero paths, periodic work racing with suspend/remove if cancellation order changes, and sensor status handling that treats unsupported discovery as `-EOPNOTSUPP`. Test signals include successful sensor enumeration, HID sensor reports in userspace, suspend/resume without stale work, init failure cleanup with fault injection, and lockdep coverage around `mp2->lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_common.h -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_common.h

## Purpose

`amd_sfh_common.h` defines shared MP2/SFH constants, device state, command IDs, sensor information structures, and the operation table used between PCI transport, HID client, and descriptor backends.

## Important APIs, Types, and Functions

Important constants include AMD MP2 PCI device IDs, C2P/P2C message-register address macros for register revisions, sensor status values, and `AMD_SFH_IDLE_LOOP`. `struct amd_mp2_sensor_info` carries sensor ID, polling period, and DMA address. `struct sfh_dev_status` tracks HPD, ALS, and SRA availability. `struct amd_mp2_dev` is the central persistent device object. `struct amd_mp2_ops` contains callbacks for start/stop, response, interrupts, discovery, power management, removal, descriptor lookup, and report generation. Inline helpers `amd_get_c2p_val()` and `amd_get_p2c_val()` select register maps based on `mp2->rver`.

## Control Flow

There is no direct control flow in the header, but the callback table defines it: PCI probe selects or installs `amd_mp2_ops`; client initialization calls descriptor and sensor callbacks; HID request paths call report callbacks.

## State and Persistence Behavior

`struct amd_mp2_dev` persists for the PCI device lifetime and owns the PCI device pointer, MMIO mappings, SFH 1.1 virtual sensor memory base, operation tables, input-data arrays, active-control status, feature flags, work item, mutex, initialization flag, and register revision.

## Dependencies and Integration Points

The header depends on PCI, mutexes, and local HID state from `amd_sfh_hid.h`. It is included by nearly every AMD SFH source file and is the contract that lets legacy MP2 and SFH 1.1 implementations share the HID client.

## Risks and Test Signals

Changing callback semantics affects all SFH generations. Register-map helpers must match firmware/CPU revision behavior. Test signals include compile coverage of all SFH objects, runtime validation on both `PCI_DEVICE_ID_AMD_MP2` and `PCI_DEVICE_ID_AMD_MP2_1_1`, and suspend/resume paths that exercise installed ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_hid.c -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_hid.c

## Purpose

`amd_sfh_hid.c` implements the synthetic HID low-level driver used by AMD SFH sensors. It lets each discovered sensor appear as a HID device even though reports are generated by the MP2/SFH client layer rather than a physical HID transport.

## Important APIs, Types, and Functions

`amdtp_hid_parse()` feeds the generated report descriptor to `hid_parse_report()`. `amdtp_hid_request()` dispatches HID core get/set report requests to `amd_sfh_get_report()` and `amd_sfh_set_report()`. `amdtp_wait_for_response()` waits up to `AMD_SFH_RESPONSE_TIMEOUT` for request completion. `amdtp_hid_wakeup()` marks the current sensor request complete and wakes the waitqueue. `amdtp_hid_probe()` allocates and registers a `hid_device`; `amdtp_hid_remove()` destroys all registered sensor HID devices.

## Control Flow

Client initialization calls `amdtp_hid_probe()` per enabled sensor. The new HID device uses `amdtp_hid_ll_driver`, which supplies parse/start/stop/open/close/request/wait/raw_request callbacks. During `hid_add_device()`, HID core calls parse and later issues requests. Get report requests are asynchronous: `amdtp_hid_request()` queues work in the client file, while `amdtp_wait_for_response()` blocks until `amdtp_hid_wakeup()`.

## State and Persistence Behavior

Each HID device has an `amdtp_hid_data` allocation in `hid->driver_data`, storing the sensor index, shared client pointer, and waitqueue. The shared `amdtp_cl_data` stores the `hid_sensor_hubs[]` array and `request_done[]` flags.

## Dependencies and Integration Points

The file depends on HID core and waitqueue APIs. It integrates tightly with `amd_sfh_client.c`: request functions, wakeups, and report descriptor arrays are shared through `amdtp_cl_data`.

## Risks and Test Signals

Risks include timeout semantics (`ret == 0` from wait_event timeout is treated as success in this version), raw requests being a no-op, and current-index coupling in `amdtp_hid_wakeup()`. Test signals include HID device registration, descriptor parsing success, feature/input report GETs from hid-sensor consumers, and teardown without use-after-free in `driver_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_hid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_hid.h

## Purpose

`amd_sfh_hid.h` defines the shared HID-client data structures and function prototypes used by the AMD SFH client and HID low-level driver.

## Important APIs, Types, and Functions

`MAX_HID_DEVICES` caps the sensor HID array at seven. `AMD_SFH_HID_VENDOR` and `AMD_SFH_HID_PRODUCT` identify synthetic HID devices. `struct request_list` represents a queued report request. `struct amd_input_data` stores DMA-visible sensor buffers and generated input report buffers. `struct amdtp_cl_data` is the central HID client state with descriptor/report arrays, HID devices, sensor status, request state, delayed work, and the request list. `struct amdtp_hid_data` is per-HID-device private data. Prototypes expose `amdtp_hid_probe()`, `amdtp_hid_remove()`, `amd_sfh_get_report()`, `amd_sfh_set_report()`, and `amdtp_hid_wakeup()`.

## Control Flow

The header establishes a two-way API: the client calls HID probe/remove and wakeup helpers, while the HID low-level driver calls client report handlers.

## State and Persistence Behavior

Arrays in `amdtp_cl_data` persist for the PCI device lifetime and are indexed by client enumeration order, not always by raw sensor ID. Request flags and `cur_hid_dev` are mutable synchronization state used by HID wait paths.

## Dependencies and Integration Points

It depends on HID device types, workqueues, waitqueues, and local MP2 code that embeds `amd_input_data` inside `amd_mp2_dev`.

## Risks and Test Signals

The fixed `MAX_HID_DEVICES` must cover all enumerated sensors; sensor additions can overflow expectations if discovery changes. Tests should cover all supported sensor combinations, request queue processing, and sensor-index/current-index mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.c -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.c

## Purpose

`amd_sfh_pcie.c` is the PCI transport driver for AMD MP2/SFH. It binds PCI IDs, maps MMIO registers, selects legacy or v2 command operations, handles interrupts, exposes HPD sysfs control for SFH 1.1, schedules initialization work, and wires runtime power-management callbacks.

## Important APIs, Types, and Functions

The module defines PCI driver `pcie_mp2_amd`. Legacy/v2 command helpers include `amd_start_sensor()`, `amd_stop_sensor()`, `amd_stop_all_sensors()`, `amd_start_sensor_v2()`, `amd_stop_sensor_v2()`, `amd_stop_all_sensor_v2()`, and `amd_sfh_wait_response_v2()`. `amd_mp2_get_sensor_num()` converts active sensor masks into sensor IDs, with DMI and module-parameter overrides. `mp2_select_ops()` installs legacy or v2 `amd_mp2_ops`. Probe/remove/shutdown/PM paths are `amd_mp2_pci_probe()`, `amd_sfh_remove()`, `amd_sfh_shutdown()`, `amd_mp2_pci_suspend()`, and `amd_mp2_pci_resume()`.

## Control Flow

Probe rejects known unsupported Google systems, applies DMI interrupt quirks, allocates `amd_mp2_dev`, enables PCI, maps BAR 2, sets DMA mask, allocates client data, initializes the mutex, and checks whether the PCI ID carries SFH 1.1 ops. SFH 1.1 devices schedule `sfh1_1_init_work()`. Legacy devices select ops, initialize interrupts if supported, and schedule `sfh_init_work()`, which calls `amd_sfh_hid_client_init()`. Remove and shutdown flush work before stopping sensors.

## State and Persistence Behavior

Persistent state is stored in `amd_mp2_dev` and PCI driver data. Module state includes `sensor_mask_override` and `intr_disable`, both affecting runtime discovery/commands. Sysfs attribute `hpd` reflects and toggles `mp2->dev_en.is_hpd_enabled` through SFH 1.1 ops.

## Dependencies and Integration Points

The driver depends on PCI managed resources, DMA, DMI matching, interrupts, MMIO polling, workqueues, and HID client code. It integrates with `sfh1_1/amd_sfh_init.c` through `sfh1_1_ops` for `PCI_DEVICE_ID_AMD_MP2_1_1`.

## Risks and Test Signals

Risks include DMI overrides hiding real sensors, long 10-second response polling during probe, interrupt quirks changing firmware behavior, and cleanup differences between legacy and SFH 1.1 paths. Test signals are PCI probe on both IDs, sensor mask module parameter behavior, sysfs HPD visibility only when present, suspend/resume, shutdown stop-all, and no IRQ storms after `amd_sfh_clear_intr()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.h -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.h

## Purpose

`amd_sfh_pcie.h` defines MP2 PCI register offsets, command/response bit layouts, sensor IDs, memory-type constants, HPD status layout, and public PCI/client function prototypes.

## Important APIs, Types, and Functions

Constants include `AMD_C2P_MSG0..2`, `AMD_P2C_MSG3`, `V2_STATUS`, `HPD_IDX`, `ACS_IDX`, and discovery-status masks. `union sfh_cmd_base`, `union cmd_response`, and `union sfh_cmd_param` encode command register payloads for legacy and v2 firmware. `struct sfh_cmd_reg` groups command fields and physical address. `enum sensor_idx` names accelerometer, gyro, magnetometer, operating mode, and ALS IDs. Prototypes expose `amd_mp2_get_sensor_num()`, `amd_sfh_hid_client_init()`, `amd_sfh_hid_client_deinit()`, and `amd_sfh_set_desc_ops()`.

## Control Flow

The header is consumed by PCI command writers and descriptor code. Command fields written by `amd_sfh_pcie.c` are later interpreted by firmware and response registers polled by callback functions.

## State and Persistence Behavior

The header defines wire-level state layouts rather than storing state. Bitfield definitions must remain consistent with firmware ABI.

## Dependencies and Integration Points

It includes `amd_sfh_common.h` and is included by client, PCI, and descriptor code. Its `HPD_IDX`/`ACS_IDX` constants are shared with descriptor generation and sensor discovery.

## Risks and Test Signals

Bitfield layout mistakes directly break firmware commands. Test signals include command register traces for start/stop, response parsing on v2 devices, ALS C2P-register input, HPD report values, and compile checks for duplicate `hpd_status` definitions across SFH generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.c -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.c

## Purpose

`amd_sfh_hid_desc.c` supplies legacy MP2 descriptor operations. It returns HID report descriptors, descriptor sizes, feature reports, and input reports for accelerometer, gyroscope, magnetometer, ambient light/color sensors, and HPD.

## Important APIs, Types, and Functions

`amd_sfh_set_desc_ops()` installs callbacks into `amd_mp2_ops`: `get_report_descriptor()`, `get_feature_report()`, `get_input_report()`, and `get_descr_sz()`. Helpers `get_common_features()` and `get_common_inputs()` populate shared HID sensor fields. `get_input_report()` converts raw DMA or register values into packed report structures from `amd_sfh_hid_desc.h`.

## Control Flow

Client initialization calls `amd_sfh_set_desc_ops()` before requesting descriptor sizes and report descriptors. HID requests and periodic polling later call the installed report callbacks. Input reports read from `in_data->sensor_virt_addr[current_index]` for most sensors; ALS on v2 can read illuminance from `AMD_C2P_MSG(5)`, and HPD reads from `AMD_C2P_MSG(4)`.

## State and Persistence Behavior

The file is stateless aside from writing into caller-provided buffers. Generated reports are stored by the client in per-sensor feature/input buffers. Raw sensor values persist in coherent DMA buffers owned by the client.

## Dependencies and Integration Points

It depends on HID descriptor byte arrays from `amd_sfh_hid_report_desc.h`, packed report structures from `amd_sfh_hid_desc.h`, sensor IDs from `amd_sfh_pcie.h`, and MP2 status/register data from `amd_sfh_common.h`.

## Risks and Test Signals

Risks include size mismatches between descriptors and packed report structs, unit conversion truncation by `AMD_SFH_FW_MULTIPLIER`, and special cases for ACS/HPD/ALS registers. Test signals include `hid_parse_report()` success for every descriptor, expected hid-sensor attributes in userspace, ALS/ACS color fields, and HPD presence changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.h -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.h

## Purpose

`amd_sfh_hid_desc.h` defines descriptor type constants and packed feature/input report structures for AMD SFH HID sensor reports.

## Important APIs, Types, and Functions

`enum desc_type` names descriptor, input, and feature size queries. `struct common_feature_property` and `struct common_input_property` hold shared HID sensor fields. Sensor-specific packed structs include `accel3_feature_report`, `accel3_input_report`, `gyro_feature_report`, `gyro_input_report`, `magno_feature_report`, `magno_input_report`, `als_feature_report`, `als_input_report`, `hpd_feature_report`, and `hpd_input_report`.

## Control Flow

Descriptor callback files use these structs to size report buffers and serialize feature/input report payloads. HID report descriptors in `amd_sfh_hid_report_desc.h` must describe layouts compatible with these packed structures.

## State and Persistence Behavior

The header defines wire-format payloads. Instances are transient stack objects copied into client-owned report buffers for HID core delivery.

## Dependencies and Integration Points

It is included by both legacy and SFH 1.1 descriptor implementations. The packed ABI integrates with Linux HID sensor parsing and userspace consumers of hid-sensor devices.

## Risks and Test Signals

Any field order, size, or packing change can desynchronize descriptors from reports. Test signals include descriptor/report size equality checks, HID sensor collection parsing, and userspace readings for all supported sensor types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_report_desc.h -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_report_desc.h

## Purpose

`amd_sfh_hid_report_desc.h` contains static HID report descriptor byte arrays for AMD SFH sensor devices.

## Important APIs, Types, and Functions

The exported arrays are `accel3_report_descriptor`, `gyro3_report_descriptor`, `comp3_report_descriptor`, `als_report_descriptor`, and `hpd_report_descriptor`. Each describes a HID Sensor usage collection, feature reports for reporting/power/sensitivity properties, and input reports matching the packed structures in `amd_sfh_hid_desc.h`.

## Control Flow

Descriptor callbacks copy one of these arrays into a per-sensor descriptor buffer. `amdtp_hid_parse()` then passes the selected array to `hid_parse_report()` during synthetic HID device registration.

## State and Persistence Behavior

The arrays are static read-only data. Runtime state is limited to copies stored in `amdtp_cl_data.report_descr[]`.

## Dependencies and Integration Points

The descriptors integrate with Linux HID core and HID sensor hub parsing. They must match report IDs and payload layouts generated by both legacy and SFH 1.1 descriptor implementations.

## Risks and Test Signals

Descriptor byte arrays are easy to corrupt with off-by-one edits. Risks include report ID mismatches, invalid logical/physical ranges, and descriptors that parse but do not match generated reports. Test signals include `hid-tools` descriptor parsing, kernel `hid_parse_report()` success, and functional hid-sensor readings for accelerometer, gyro, compass, ALS, and HPD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_report_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_desc.c -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_desc.c

## Purpose

`sfh1_1/amd_sfh_desc.c` provides descriptor and report callbacks for SFH 1.1 firmware. Unlike the legacy descriptor path, it reads sensor data from an SFH firmware memory window and converts firmware float encodings to integer HID values.

## Important APIs, Types, and Functions

`amd_sfh1_1_set_desc_ops()` installs `get_report_desc()`, `get_feature_rep()`, `get_desc_size()`, and `get_input_rep()` into `amd_mp2_ops`. `amd_sfh_float_to_int()` converts IEEE-like 32-bit firmware float values with rounding. `get_input_rep()` reads `sfh_accel_data`, `sfh_gyro_data`, `sfh_mag_data`, `sfh_als_data`, and HPD status and emits packed HID reports.

## Control Flow

SFH 1.1 client init installs these ops, copies static descriptors, starts sensors, then periodic work requests input reports. For accelerometer, gyro, magnetometer, and ALS, the code computes a sensor memory address from `vsbase`, sensor index, `SENSOR_DATA_MEM_SIZE_DEFAULT`, and `OFFSET_SENSOR_DATA_DEFAULT`. HPD uses a C2P/P2C register selected by revision helper.

## State and Persistence Behavior

The file is mostly stateless. It reads persistent firmware memory and writes caller-owned report buffers. ALS color fields are conditional on firmware feature bits in `sfh_base_info`.

## Dependencies and Integration Points

It depends on `amd_sfh_interface.h` for SFH 1.1 memory layouts, shared descriptor arrays, and packed report structs. It integrates with the generic AMD SFH HID client through `amd_mp2_ops`.

## Risks and Test Signals

Risks include float conversion corner cases, stale firmware memory reads, scale divisors differing by sensor, and feature-bit handling for ALS color data. Test signals include SFH 1.1 devices exposing correct hid-sensor values, ALS color feature validation, HPD reports, and unit tests for `amd_sfh_float_to_int()` edge values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.c -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.c

## Purpose

`sfh1_1/amd_sfh_init.c` initializes AMD SFH 1.1 devices. It maps the firmware sensor memory window, discovers sensors from `sfh_base_info`, starts and stops sensors, registers HID devices, manages suspend/resume, toggles HPD, and removes the SFH 1.1 instance.

## Important APIs, Types, and Functions

`amd_sfh1_1_init()` is the public init entry. `amd_sfh1_1_hid_client_init()` mirrors the legacy client initialization but uses SFH 1.1 discovery and command semantics. `amd_sfh_hid_client_deinit()` tears down sensors and HID devices. `amd_sfh_resume()`, `amd_sfh_suspend()`, and `amd_sfh_toggle_hpd()` implement power and HPD policy. `amd_sfh_set_ops()` installs interface, interrupt, PM, and remove callbacks.

## Control Flow

Initialization reads the physical base from a C2P register, maps 128 KiB of SFH firmware memory, waits five seconds for firmware configuration, validates firmware version and sensor list, installs ops, initializes interrupts, and starts HID client setup. The client discovers sensors from the firmware sensor bitmask, handles SRA as a platform-info-only sensor, creates HID devices for enabled non-SRA sensors, marks HPD/ALS/SRA availability, and schedules periodic input work.

## State and Persistence Behavior

State persists in `amd_mp2_dev`, `sfh_dev_status`, `amdtp_cl_data`, and the global interface pointer cleared by `sfh_deinit_emp2()`. HPD enabled state is persistent until toggled by sysfs/policy, and suspend/resume intentionally leaves HPD alone.

## Dependencies and Integration Points

It depends on HID core, delays, PCI-managed memory mapping, the SFH 1.1 interface layer, descriptor callbacks, and generic AMD SFH HID helpers. It integrates with `amd_sfh_pcie.c` through `sfh1_1_ops`.

## Risks and Test Signals

Risks include the fixed five-second firmware wait, physical base calculation by shifting register contents, SRA not producing a HID device, and HPD policy interactions during suspend. Test signals include SFH 1.1 probe on supported hardware, `amd_get_sfh_info()` success for SRA/ALS/HPD, sysfs HPD toggling, suspend/resume preserving HPD policy, and cleanup after partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.h -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.h

## Purpose

`sfh1_1/amd_sfh_init.h` declares the SFH 1.1 operation table used by the PCI driver.

## Important APIs, Types, and Functions

`struct amd_sfh1_1_ops` contains `init` and `toggle_hpd` callbacks. The header declares `amd_sfh1_1_init()` and `amd_sfh_toggle_hpd()`, then defines static `sfh1_1_ops` with those callbacks.

## Control Flow

`amd_sfh_pcie.c` stores `&sfh1_1_ops` in the PCI ID table for `PCI_DEVICE_ID_AMD_MP2_1_1`. Probe reads that driver data and schedules SFH 1.1 initialization instead of legacy MP2 initialization.

## State and Persistence Behavior

The operation table is static read-only data. Runtime state is carried by `amd_mp2_dev`.

## Dependencies and Integration Points

The header includes `amd_sfh_common.h` and bridges PCI probing to SFH 1.1 implementation files.

## Risks and Test Signals

Risks are callback signature drift and accidental omission from the PCI ID table. Test signals include build coverage and runtime probe selecting SFH 1.1 ops for device ID `0x164A`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.c -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.c

## Purpose

`sfh1_1/amd_sfh_interface.c` implements SFH 1.1 command operations and exports platform sensor information to other AMD platform code through `amd_get_sfh_info()`.

## Important APIs, Types, and Functions

Internal command helpers include `amd_sfh_wait_response()`, `amd_start_sensor()`, `amd_stop_sensor()`, and `amd_stop_all_sensor()`. `sfh_interface_init()` installs the SFH 1.1 `amd_mp2_ops` and stores the global `emp2` pointer; `sfh_deinit_emp2()` clears it. Query helpers `amd_sfh_mode_info()`, `amd_sfh_hpd_info()`, and `amd_sfh_als_info()` feed exported `amd_get_sfh_info()`.

## Control Flow

SFH 1.1 init calls `sfh_interface_init()`. Start/stop callbacks write command bitfields into revision-selected C2P registers and response polling checks P2C registers. `amd_get_sfh_info()` dispatches by message type: HPD reads HPD status, ALS reads the mapped sensor memory and converts lux, and SRA reads mode bits to derive platform type and laptop placement.

## State and Persistence Behavior

The global `emp2` pointer is the main state and makes exported info queries refer to the active SFH device. It is cleared during remove. The file also reads persistent `mp2->dev_en` flags to decide whether data is available.

## Dependencies and Integration Points

It depends on `linux/amd-pmf-io.h` for the exported info ABI, MMIO polling, register helpers, and SFH 1.1 structures. The exported symbol integrates with AMD PMF and any platform code querying HPD/ALS/SRA.

## Risks and Test Signals

Risks include single-device global state, queries racing removal, ambiguous laptop placement states, and returning `-ENODEV` until SRA/ALS/HPD flags are set. Test signals include AMD PMF consumers reading correct placement/light/presence values, remove clearing `emp2`, and response timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.h -->
# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.h

## Purpose

`sfh1_1/amd_sfh_interface.h` defines SFH 1.1 command, firmware, sensor-list, sensor-property, and sensor-data memory layouts.

## Important APIs, Types, and Functions

Constants define default sensor data memory size, static memory size, and offsets. `enum sensor_index` names SFH 1.1 sensor IDs. `struct sfh_cmd_base` and `struct sfh_cmd_response` define register command/response bitfields. `struct sfh_base_info` models the firmware base block with platform, firmware, sensor list, and per-sensor properties. Data structs model common sensor metadata, accel/gyro/mag/ALS payloads, HPD status, and SRA operating mode. Prototypes expose interface init/deinit, descriptor-op installation, and float conversion.

## Control Flow

Implementation files use these layouts to parse the mapped firmware memory, generate HID reports, and export AMD PMF information.

## State and Persistence Behavior

The header defines memory-mapped state owned by firmware. Driver state is derived by copying or reading these structures from `mp2->vsbase`.

## Dependencies and Integration Points

It includes `amd_sfh_common.h` and is shared by SFH 1.1 init, interface, and descriptor files. Its layouts must match firmware and AMD PMF expectations.

## Risks and Test Signals

Risks include bitfield layout drift, duplicate `hpd_status` naming relative to the legacy header, and offset/size assumptions for the 128 KiB virtual sensor memory. Test signals include firmware version/sensor-list parsing, ALS/SRA/HPD exported data, and descriptor reports reading correct offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/Kconfig

## Purpose

This Kconfig file exposes HID-BPF support, allowing eBPF programs to fix HID report descriptors, rewrite HID events, and issue selected HID operations through BPF kfuncs and struct_ops.

## Important APIs, Types, and Functions

The sole symbol is `HID_BPF`, a boolean "HID-BPF support". It depends on `BPF`, `BPF_SYSCALL`, `DYNAMIC_FTRACE_WITH_DIRECT_CALLS`, and `BPF_JIT`, and defaults to enabled when dependencies are present.

## Control Flow

When selected from the parent HID Kconfig, Kbuild enters `drivers/hid/bpf/` and builds the HID-BPF dispatcher and struct_ops support. If dependencies are unavailable, HID core builds without this extension.

## State and Persistence Behavior

This file persists a build-time feature choice. Runtime per-device BPF state is initialized by HID core only when the built code is present.

## Dependencies and Integration Points

The dependency set ties HID-BPF to the BPF verifier/runtime, syscall loading path, JIT support, and tracing direct-call infrastructure needed for struct_ops and kfunc calls.

## Risks and Test Signals

Dependency mistakes can produce build failures or a selectable feature that cannot load programs. Test signals include `CONFIG_HID_BPF=y` builds, BPF selftests using HID struct_ops, and module load paths on kernels with and without BPF JIT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/Makefile

## Purpose

This Makefile builds the kernel HID-BPF support object.

## Important APIs, Types, and Functions

`obj-$(CONFIG_HID_BPF) += hid_bpf.o` defines the composite target. `hid_bpf-objs += hid_bpf_dispatch.o hid_bpf_struct_ops.o` links the dispatch/kfunc and struct_ops registration halves. `CFLAGS_hid_bpf_dispatch.o` and `CFLAGS_hid_bpf_jmp_table.o` add `$(LIBBPF_INCLUDE)`.

## Control Flow

Kbuild compiles these objects when `CONFIG_HID_BPF` is enabled. Initialization happens through `late_initcall()` functions inside the C files.

## State and Persistence Behavior

No runtime state is stored here. The file determines that dispatcher and struct_ops code are always built together.

## Dependencies and Integration Points

It integrates with parent HID Kbuild and the kernel BPF/libbpf include setup. The `hid_bpf_jmp_table.o` flag appears to reference an object not in this composite target, so it may be leftover or for generated/optional code outside this snapshot.

## Risks and Test Signals

Risks include stale CFLAGS for missing objects and include path drift. Test signals are clean `CONFIG_HID_BPF=y` builds and BPF selftest compilation of HID programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.c

## Purpose

`hid_bpf_dispatch.c` provides the runtime dispatch layer and BPF kfuncs for HID-BPF. It lets attached BPF struct_ops programs modify device events, intercept raw requests/output reports, fix report descriptors, allocate contexts, access report buffers, send hardware requests, and inject input reports.

## Important APIs, Types, and Functions

Exported dispatch APIs include `dispatch_hid_bpf_device_event()`, `dispatch_hid_bpf_raw_requests()`, `dispatch_hid_bpf_output_report()`, and `call_hid_bpf_rdesc_fixup()`. Device lifecycle APIs include `hid_bpf_connect_device()`, `hid_bpf_disconnect_device()`, `hid_bpf_destroy_device()`, and `hid_bpf_device_init()`. BPF kfuncs include `hid_bpf_get_data()`, `hid_bpf_allocate_context()`, `hid_bpf_release_context()`, `hid_bpf_hw_request()`, `hid_bpf_hw_output_report()`, `hid_bpf_try_input_report()`, and `hid_bpf_input_report()`. `hid_ops` is an exported bridge to HID core operations.

## Control Flow

HID core calls dispatchers at event, raw-request, output-report, and descriptor-fixup points. The dispatchers build `hid_bpf_ctx_kern`, copy or reference report data, iterate attached ops under RCU/SRCU, and propagate return sizes/errors. Kfuncs validate report types and report IDs through `hid_ops`, prevent recursive hardware calls when `from_bpf` is set, copy DMA buffers for hardware requests, and inject reports through HID core locks.

## State and Persistence Behavior

Per-device BPF state lives in `hdev->bpf`: attached program list, SRCU, mutex, descriptor-fixup op, allocated event buffer, allocation size, and destroyed flag. Context allocations hold a device reference until released. `hid_bpf_init()` registers kfunc sets at late init and logs but does not fail HID if registration fails.

## Dependencies and Integration Points

The file depends on HID core internals, BTF kfunc registration, BPF program types, SRCU/RCU, kfifo/minmax helpers, and exported `__hid_bpf_ops_destroy_device()` from the struct_ops file.

## Risks and Test Signals

Risks include recursion/deadlock if `from_bpf` checks are bypassed, event buffer sizing based on parsed reports, descriptor fixup allocation fallback silently ignoring BPF, and device destruction races. Test signals include HID-BPF selftests for event rewriting, descriptor reprobe, kfunc verifier access, concurrent detach/destroy, and hardware request recursion rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.h -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.h

## Purpose

`hid_bpf_dispatch.h` is the private header shared between HID-BPF dispatcher and struct_ops implementation.

## Important APIs, Types, and Functions

`struct hid_bpf_ctx_kern` embeds public `struct hid_bpf_ctx`, a kernel data pointer, and a `from_bpf` recursion flag. Prototypes cover device lookup/reference helpers, event data allocation, device-destroy cleanup, and HID reprobe.

## Control Flow

Struct_ops registration uses `hid_get_device()`, `hid_put_device()`, `hid_bpf_allocate_event_data()`, and `hid_bpf_reconnect()` while dispatch code provides the implementations.

## State and Persistence Behavior

The header defines transient context wrapper state. Device references acquired by `hid_get_device()` must be released by `hid_put_device()`.

## Dependencies and Integration Points

It includes `<linux/hid.h>` and is private to `drivers/hid/bpf`. It forms the internal ABI between the two HID-BPF C files.

## Risks and Test Signals

Risks are ownership mismatches for HID device references and accidental exposure of private context fields. Test signals include attach/detach reference-count tests, device removal under active BPF programs, and compile checks when `struct hid_bpf_ctx` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_dispatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_struct_ops.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_struct_ops.c

## Purpose

`hid_bpf_struct_ops.c` registers the `hid_bpf_ops` BPF struct_ops type and manages attachment, detachment, verifier write permissions, and device cleanup for HID-BPF programs.

## Important APIs, Types, and Functions

Verifier hooks include `hid_bpf_ops_is_valid_access()`, `hid_bpf_ops_check_member()`, and `hid_bpf_ops_btf_struct_access()`. Initialization and member-copy hooks are `hid_bpf_ops_init()` and `hid_bpf_ops_init_member()`. Runtime attach/detach handlers are `hid_bpf_reg()` and `hid_bpf_unreg()`. `__hid_bpf_ops_destroy_device()` nulls attached ops during HID device destruction. `hid_bpf_struct_ops_init()` registers the struct_ops type at late init.

## Control Flow

When userspace links a `hid_bpf_ops` map, `hid_bpf_reg()` resolves `hid_id` to a device, locks the device BPF list, enforces `HID_BPF_MAX_PROGS_PER_DEV`, installs a single descriptor-fixup op if requested, allocates event data when needed, inserts the ops before or after existing programs based on `BPF_F_BEFORE`, and triggers reprobe for descriptor fixups. Detach removes the list node, clears descriptor fixup if owned, optionally reprobes, and drops the device reference.

## State and Persistence Behavior

State persists in `hdev->bpf.prog_list`, `hdev->bpf.rdesc_ops`, and each `struct hid_bpf_ops` instance's `hdev` and list node. The file stores a BTF pointer in `hid_bpf_ops_btf`. Destroy-device cleanup clears `e->hdev` so later unregister avoids using a destroyed device.

## Dependencies and Integration Points

It depends on BPF verifier APIs, BTF, HID core, workqueue headers, and the dispatcher helpers. It integrates with BPF syscall loading of struct_ops maps and HID device lifecycle hooks.

## Risks and Test Signals

Risks include write-permission gaps in verifier rules, descriptor fixup exclusivity, list ordering with `BPF_F_BEFORE`, reference drops during destroy, and sleepable-program restrictions for event callbacks. Test signals include verifier tests for writable fields, attach limit tests, rdesc-fixup attach/detach reprobe, concurrent device removal, and ordering tests with multiple programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/hid_bpf_struct_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/FR-TEC__Raptor-Mach-2.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/FR-TEC__Raptor-Mach-2.bpf.c

## Purpose

This HID-BPF program fixes the FR-TEC/Betop Raptor Mach 2 joystick report descriptor and event stream so the hat switch has kernel-compatible values.

## Important APIs, Types, and Functions

The program matches USB generic HID device VID `0x11C0`, PID `0x5606` through `HID_BPF_CONFIG`. `hid_fix_rdesc_raptor_mach_2()` is a `HID_BPF_RDESC_FIXUP` program that changes descriptor byte 177 from logical maximum 239 to 7. `raptor_mach_2_fix_hat_switch()` is a `HID_BPF_DEVICE_EVENT` program that divides report byte 33 by 30 for report ID 1. `HID_BPF_OPS(raptor_mach_2)` attaches both hooks. `probe()` accepts only the expected 232-byte descriptor with byte 177 still equal to `0xef`.

## Control Flow

At load/probe time the descriptor gate rejects already-fixed or unknown descriptors. During descriptor fixup, the BPF program mutates the logical max. During events, only joystick report ID 1 is changed; other reports pass through.

## State and Persistence Behavior

The program has no mutable persistent state. It mutates the report descriptor buffer and event buffer supplied by HID-BPF.

## Dependencies and Integration Points

It depends on HID-BPF helpers, `hid_bpf_get_data()`, BPF tracing macros, and udev-hid-bpf loading conventions.

## Risks and Test Signals

Risks are hard-coded descriptor and report offsets. Test signals include probe rejection on descriptor changes, hat switch reporting 0..7 instead of 0..239, no changes to non-ID-1 reports, and successful BPF verifier load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/FR-TEC__Raptor-Mach-2.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Generic__touchpad.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Generic__touchpad.bpf.c

## Purpose

This generic HID-BPF probe program reads a Windows 8 multitouch touchpad's Pad Type feature report and exports it as a udev property.

## Important APIs, Types, and Functions

`HID_BPF_CONFIG` matches any bus/vendor/product in `HID_GROUP_MULTITOUCH_WIN_8`. `EXPORT_UDEV_PROP(HID_DIGITIZER_PAD_TYPE, 32)` declares the output property. `HID_REPORT_DESCRIPTOR` is filled by udev-hid-bpf. `probe()` scans feature reports for Digitizers Pad Type usage, allocates a HID-BPF context, sends `HID_REQ_GET_REPORT` through `hid_bpf_hw_request()`, extracts the field with `EXTRACT_BITS()`, and writes strings `Clickpad`, `Pressurepad`, `Discrete`, or `Unknown`.

## Control Flow

This program runs in the syscall/probe lane, not as an event hook. It rejects devices without the Pad Type feature. For matching devices, it performs a feature report request and emits a udev property before releasing the context.

## State and Persistence Behavior

Persistent BPF globals are `hw_req_buf` and the report descriptor descriptor supplied by userspace. The durable output is the udev property generated by the loader.

## Dependencies and Integration Points

It depends on HID report parsing helper macros, HID-BPF kfuncs for context allocation and hardware requests, and udev-hid-bpf property export support.

## Risks and Test Signals

Risks include a fixed 1024-byte request buffer, feature report failures delaying property export, and descriptor parser assumptions. Test signals include correct `HID_DIGITIZER_PAD_TYPE` values on clickpad/pressurepad/discrete hardware, rejection of devices without Pad Type, and no leaked HID context on request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Generic__touchpad.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/HP__Elite-Presenter.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/HP__Elite-Presenter.bpf.c

## Purpose

This HID-BPF program improves the HP Elite Presenter Mouse Bluetooth report descriptor so the second mouse-like collection is treated as a pointer collection, enabling both mouse and digital laser pointer behavior.

## Important APIs, Types, and Functions

The program matches Bluetooth generic HID VID `0x03F0`, PID `0x464A`. `hid_fix_rdesc()` obtains the descriptor buffer and changes byte 79 from application mouse (`0x02`) to pointer (`0x01`) when applicable. `HID_BPF_OPS(hp_elite_presenter)` attaches only the descriptor-fixup hook. `probe()` requires descriptor size 264.

## Control Flow

The probe gate validates descriptor length. Descriptor fixup then performs one conditional byte substitution. No event hook is installed.

## State and Persistence Behavior

The program is stateless after attach. Its only persistent effect is the fixed descriptor used when HID core reprobes the device.

## Dependencies and Integration Points

It depends on HID-BPF descriptor fixup hooks and is intended to complement or improve a kernel quirk for the same device.

## Risks and Test Signals

Risks are hard-coded offset assumptions and future firmware descriptors with the same length but different layout. Test signals include both pointer modes appearing as intended, probe rejection on unexpected descriptors, and no event-path overhead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/HP__Elite-Presenter.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Dial-2.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Dial-2.bpf.c

## Purpose

This HID-BPF program fixes Huion Dial 2 tablet descriptors and reports across firmware/default mode and raw tablet mode. It avoids duplicate unusable nodes when a firmware ID is known and translates vendor/keyboard-style reports into tablet pad, pen, button, and dial reports.

## Important APIs, Types, and Functions

The program matches USB VID `0x256C`, PID `0x0060`. It consumes udev property `HUION_FIRMWARE_ID` and expects prefix `HUION_T216_`. Constants define descriptor lengths, report IDs, and report lengths for pad, pen, vendor, dial, and keyboard paths. Static replacement descriptors are `fixed_rdesc_pad`, `fixed_rdesc_pen`, `fixed_rdesc_vendor`, plus disabled vendor-sized descriptors. `dial_2_fix_rdesc()` selects the replacement descriptor. `dial_2_fix_events()` rewrites default keyboard/dial reports and raw vendor pad reports. `last_button_state` persists pad button state across raw dial events.

## Control Flow

Probe accepts only the three known descriptor sizes. During descriptor fixup, known firmware ID disables default pad/pen nodes and always fixes the vendor node; without firmware ID it fixes all nodes so manual mode switching still works. Event flow handles default pad report ID 3, default dial report ID 17, and raw vendor report ID 8. Raw pad packets become a packed pad report with button state plus two dial axes; pen packets pass through.

## State and Persistence Behavior

Persistent BPF state includes `UDEV_PROP_HUION_FIRMWARE_ID`, `EXPECTED_FIRMWARE_ID`, and `last_button_state`. Descriptor changes persist through HID reprobe; event rewrites are per report.

## Dependencies and Integration Points

It depends on HID-BPF, HID report descriptor helper macros, udev-hid-bpf property injection, and Huion mode-switch tooling that can set firmware ID.

## Risks and Test Signals

Risks include fixed report layouts, firmware prefix mismatch, button state becoming stale when reports are lost, and signed dial values encoded as `0xff`. Test signals include correct behavior in default and raw modes, no duplicate active devices when firmware ID is present, button/dial mapping tests, descriptor-size probe rejection, and verifier acceptance of bounded copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Dial-2.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Inspiroy-2-M.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Inspiroy-2-M.bpf.c

## Purpose

This HID-BPF program fixes Huion Inspiroy 2 M tablet descriptors and events, supporting both default firmware mode and raw tablet mode while avoiding duplicate inactive nodes when the firmware ID is known.

## Important APIs, Types, and Functions

The program matches USB VID `0x256C`, PID `0x0067`. It uses `HUION_FIRMWARE_ID` with expected prefix `HUION_T21k_`. Constants define descriptor lengths, report IDs, and packet sizes. Replacement descriptors `fixed_rdesc_pad`, `fixed_rdesc_pen`, and `fixed_rdesc_vendor` correct pad, pen, pressure, coordinate, button, and wheel semantics; disabled descriptors hide mute nodes. `hid_fix_rdesc()` selects descriptors. `inspiroy_2_fix_events()` converts default keyboard shortcut packets into pad reports and raw vendor pad packets into button/wheel reports. `last_button_state` preserves raw button bits between wheel packets.

## Control Flow

Probe accepts only known pad, pen, and vendor descriptor sizes. Descriptor fixup disables default pad/pen reports when firmware ID proves raw mode support, otherwise fixes all descriptors. Event handling rewrites report ID 3 keyboard/wheel packets to a compact pad report; report ID 8 vendor packets with pad marker bits are translated to pad state, while pen reports pass through.

## State and Persistence Behavior

Persistent BPF globals are the udev firmware ID buffer, expected prefix, and `last_button_state`. Runtime report rewrites are transient but descriptor replacements persist across the HID device instance.

## Dependencies and Integration Points

It depends on HID-BPF helpers, descriptor helper macros, udev-hid-bpf property passing, and the Huion raw-mode ecosystem described in comments.

## Risks and Test Signals

Risks include hard-coded dimensions/ranges, firmware ID prefix drift, wheel values represented in unsigned bytes, and stale raw button state. Test signals include pad button mapping for all default shortcuts, wheel direction correctness, raw mode button/wheel behavior, pen pressure/coordinate ranges, duplicate-node suppression, and BPF verifier load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Inspiroy-2-M.bpf.c -->
