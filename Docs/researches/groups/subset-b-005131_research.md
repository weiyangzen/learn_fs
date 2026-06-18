# Research Report: subset-b-005131

This grouped report covers AMD and platform-x86 source files from `sources/distributed-fs/ceph-client/drivers/platform/x86`. Each section preserves the source path and is bounded by the exact markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/acerhdf.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/acerhdf.c

Purpose: `acerhdf.c` is a DMI-gated Acer/Gateway/Packard Bell thermal and fan-control platform driver for legacy Aspire One-style systems. It reads temperature and fan state through the embedded controller, exposes a thermal zone named `acerhdf`, and registers a cooling device named `acerhdf-fan`. By default it leaves BIOS fan control active unless `kernelmode` is enabled by module parameter or thermal mode change.

Important APIs, types, and functions: `struct bios_settings`, `struct ctrl_settings`, `struct fancmd`, and `struct manualcmd` encode per-BIOS EC register offsets and command values. `acerhdf_check_hardware()` matches DMI vendor/product/BIOS against `bios_tbl`, with `force_bios`, `force_product`, and `list_supported` module parameters for override/listing. `acerhdf_get_temp()` and `acerhdf_get_fanstate()` use `ec_read()`, while `acerhdf_change_fanstate()` uses `ec_write()` and optional manual-off register programming. Thermal integration is through `thermal_zone_device_register_with_trips()`, `thermal_cooling_device_register()`, `acerhdf_dev_ops`, and `acerhdf_cooling_ops`.

Control flow: module init validates DMI and copies the selected register map into global `ctrl_cfg`, registers a dummy platform device/driver, then registers thermal and cooling devices. Thermal polling calls `acerhdf_get_ec_temp()`; the bang-bang governor binds only the local cooling device to the active trip. `acerhdf_set_cur_state()` refuses active control when `kernelmode` is off, otherwise it reads current temperature and fan state before switching fan off or returning it to BIOS automatic mode. Suspend and module exit always return the fan to BIOS automatic control.

State and persistence: most state is global module state: `kernelmode`, `interval`, `fanon`, `fanoff`, `fanstate`, `ctrl_cfg`, `thz_dev`, `cl_dev`, and `acerhdf_dev`. There is no persistent on-disk state. Module parameters persist only for the module instance. Runtime thermal trip values are updated by `acerhdf_check_param()` and clamp unsafe settings, including a hard 80 C maximum fan-on threshold and a 15 second maximum polling interval.

Dependencies and integration points: the driver depends on DMI, ACPI EC access, platform devices, and the thermal framework. It exports DMI module aliases for supported product families. It integrates with `/sys/class/thermal` mode control and cooling-device state, and prints supported BIOS rows when requested.

Risks: EC register offsets and command values are highly model-specific, so wrong DMI matching or forced overrides can write unintended EC locations. `acerhdf_register_thermal()` does not unwind the cooling device if thermal-zone registration fails, leaving cleanup dependent on later paths. The `interval` module parameter is registered after `module_init`, but its setter can call `acerhdf_check_param(thz_dev)` with a possibly null thermal device if invoked unusually early. Hardware safety relies on returning to BIOS mode on EC read errors and on exit/suspend.

Test signals: useful signals are successful DMI acceptance, `thermal_zone` creation with two trips, mode enable/disable behavior, fan state transitions at `fanon`/`fanoff`, EC read/write error paths reverting to BIOS mode, suspend returning to auto, and rejection of unsupported BIOS tables unless force parameters are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/acerhdf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/adv_swbutton.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/adv_swbutton.c

Purpose: `adv_swbutton.c` is a compact Advantech ACPI software-button driver. It binds ACPI HID `AHC0310`, registers an input device named `Advantech Software Button`, and converts ACPI notify events into `KEY_PROG1` press/release input events.

Important APIs, types, and functions: `struct adv_swbutton` stores the devm-managed `input_dev` and a physical path string. `adv_swbutton_probe()` allocates state with `devm_kzalloc()`, allocates/registers an input device, enables device wakeup, and installs an ACPI device notify handler. `adv_swbutton_notify()` maps event `0x85` to key press and `0x86` to key release with `input_report_key()` and `input_sync()`. `adv_swbutton_remove()` removes the notify handler.

Control flow: platform-driver ACPI matching invokes probe. Probe registers input first, then ACPI notifications. Runtime ACPI notifications arrive with the platform device as context and report input events through the stored input device. Remove unregisters only the ACPI notify handler because devm owns memory and input-device lifetime.

State and persistence: state is per-device and volatile. Wakeup enablement is stored in the device power-management flags for the device lifetime. There is no firmware mutation beyond ACPI handler installation and no persistent data.

Dependencies and integration points: dependencies are ACPI, platform driver core, and input subsystem. The external ABI is an input event stream for `KEY_PROG1`; wakeup policy may also be visible via device power sysfs.

Risks: if `acpi_install_notify_handler()` fails after input registration, devm unwinds the input device but wakeup remains enabled until device cleanup. The handler assumes `dev_get_drvdata()` and `button->input` are valid, so notify removal ordering matters. Unknown ACPI events are ignored with debug logging only.

Test signals: bind on an ACPI node with HID `AHC0310`; verify `/proc/bus/input/devices` entry, press/release event reports for `0x85`/`0x86`, unsupported event debug behavior, and clean handler removal on driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/adv_swbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Kconfig

Purpose: this Kconfig file is the top-level AMD platform-x86 menu. It includes HSMP, PMF, PMC, and HFI submenus and defines build options for 3D V-Cache optimization, WBRF, and the AMD ISP4 platform driver.

Important APIs, types, and functions: there are no C APIs, but key symbols are `AMD_3D_VCACHE`, `AMD_WBRF`, and `AMD_ISP_PLATFORM`. The file also sources `amd/hsmp/Kconfig`, `amd/pmf/Kconfig`, `amd/pmc/Kconfig`, and `amd/hfi/Kconfig`.

Control flow: kernel configuration flows from this file into subdirectory-specific symbols. `AMD_3D_VCACHE` depends on `X86_64 && ACPI`; `AMD_WBRF` depends on ACPI; `AMD_ISP_PLATFORM` depends on I2C, x86_64, and ACPI.

State and persistence: configuration choices persist in the kernel `.config`; no runtime state exists here.

Dependencies and integration points: the symbols map directly to object inclusion in the sibling `Makefile`. Help text documents module names and user-facing scope, including `amd_isp4` as the ISP4 module.

Risks: dependency mistakes can expose drivers on unsupported architectures or omit required subsystem dependencies. Because sourced submenus are unconditional in this file, their own dependencies must protect unsupported builds.

Test signals: `make menuconfig` visibility, generated `.config` symbol values, and object inclusion in `drivers/platform/x86/amd/Makefile` are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Makefile

Purpose: this Makefile maps AMD platform-x86 Kconfig symbols to built objects and subdirectories.

Important APIs, types, and functions: object rules include `obj-$(CONFIG_AMD_3D_VCACHE) += amd_3d_vcache.o` with `amd_3d_vcache-y := x3d_vcache.o`, `obj-$(CONFIG_AMD_PMC) += pmc/`, `obj-$(CONFIG_AMD_HSMP) += hsmp/`, `obj-$(CONFIG_AMD_PMF) += pmf/`, `obj-$(CONFIG_AMD_WBRF) += wbrf.o`, `obj-$(CONFIG_AMD_ISP_PLATFORM) += amd_isp4.o`, and `obj-$(CONFIG_AMD_HFI) += hfi/`.

Control flow: kbuild descends into subdirectories or links single objects based on enabled config symbols. There is no runtime control flow.

State and persistence: build artifacts are generated according to `.config`; no runtime state exists.

Dependencies and integration points: this file integrates top-level AMD symbols with implementation directories. It is tightly coupled to the Kconfig definitions in the same folder and subfolders.

Risks: mismatched object names or missing subdirectory rules would silently drop drivers from builds. Composite object naming for `amd_3d_vcache` must match module expectations.

Test signals: kernel build logs, presence of expected `.o` or `.ko` artifacts, and `modinfo` module naming validate the mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/amd_isp4.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/amd_isp4.c

Purpose: `amd_isp4.c` is an AMD ISP4 platform helper that supplies missing firmware-node graph and I2C board information for a camera sensor, currently OV05C10. It binds ACPI sensor HID `OMNI5C10`, registers a software-node graph representing ISP, I2C, ports, endpoints, and remote endpoint links, then instantiates the sensor I2C client when the AMD ISP I2C adapter appears.

Important APIs, types, and functions: `struct amdisp_platform_info` holds an `i2c_board_info` template and node group; `struct amdisp_platform` holds copied board info, an I2C bus notifier, an instantiated `i2c_client`, and a mutex. Static `software_node` and `property_entry` objects describe `amd_camera`, `isp4`, `i2c1`, `OMNI5C10`, endpoint bus type, data lanes, link frequencies, and remote endpoint references. Runtime helpers are `prepare_amdisp_platform()`, `instantiate_isp_i2c_client()`, `isp_i2c_bus_notify()`, `try_to_instantiate_i2c_client()`, `amd_isp_probe()`, and `amd_isp_remove()`.

Control flow: probe gets the matched `amdisp_platform_info`, allocates platform state, initializes a mutex, copies board info, registers the software-node group, attaches the sensor software node to board info, registers an I2C bus notifier, stores the root software node in the ACPI companion `driver_data`, scans existing I2C devices, and stores drvdata. Bus notifications instantiate the I2C client when an adapter named `AMDISP_I2C_ADAP_NAME` is added, and clear the pointer if the client is removed. Remove unregisters the notifier, unregisters the I2C client, and unregisters the software-node group.

State and persistence: state is per platform device and devm-managed except the software-node group and I2C client, which are explicitly registered/unregistered. The mutex protects single-client creation and removal notification races. No persistent state is written.

Dependencies and integration points: dependencies include ACPI matching, I2C core, software nodes/property framework, V4L2-style fwnode graph conventions, and `linux/soc/amd/isp4_misc.h` for adapter naming. The driver integrates with sensor and V4L drivers by providing standard firmware properties and endpoint links that firmware omitted.

Risks: node index `src->swnodes[6]` is positional and fragile if the node list changes. `adev->driver_data` is assigned without an explicit null check after `ACPI_COMPANION()`. I2C adapter matching by name is simple but brittle. Remove calls `i2c_unregister_device()` on `i2c_dev` without checking whether a prior bus-remove notification already cleared it, but null is safe for the helper.

Test signals: ACPI match on `OMNI5C10`, successful software-node registration, creation of an `ov05c10` I2C client at address `0x10` when the ISP adapter exists or appears later, correct fwnode graph parsing by camera drivers, and clean notifier/client/node cleanup on unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/amd_isp4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Kconfig

Purpose: this Kconfig option enables the AMD Heterogeneous Core Hardware Feedback Interface driver.

Important APIs, types, and functions: the sole symbol is `AMD_HFI`, a bool depending on ACPI, AMD CPU support, and `SCHED_MC_PRIO`.

Control flow: when selected, the hfi subdirectory Makefile links `hfi.o` into the kernel. The bool nature means it is built-in rather than a loadable module.

State and persistence: configuration persists in `.config`; no runtime state exists in this file.

Dependencies and integration points: the dependency on `SCHED_MC_PRIO` reflects the driver's use of scheduler ITMT/core-priority hooks. ACPI is required for the platform device and PCCT data.

Risks: missing scheduler or CPU feature dependencies would create compile-time or runtime failures. Since the driver is bool-only, unload/reload style testing is not available.

Test signals: config visibility only on matching dependency sets, successful kernel link, and boot-time HFI initialization on systems with matching ACPI and CPU features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Makefile

Purpose: this Makefile builds the AMD HFI driver.

Important APIs, types, and functions: it maps `CONFIG_AMD_HFI` to `amd_hfi.o` and composes that object from `hfi.o`.

Control flow: kbuild includes the object only when `AMD_HFI` is selected.

State and persistence: build-only state; no runtime behavior.

Dependencies and integration points: tied to `amd/hfi/Kconfig` and to the top-level AMD Makefile that descends into this directory.

Risks: object naming must stay aligned with the module/driver name. Since `AMD_HFI` is bool, the object is linked into vmlinux when enabled.

Test signals: build artifact inclusion and successful link of `hfi.o` into `amd_hfi.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/hfi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/hfi.c

Purpose: `hfi.c` implements AMD Hardware Feedback Interface support for heterogeneous AMD cores. It parses ACPI PCCT shared memory containing workload-class performance/efficiency rankings, maps rankings to per-CPU scheduler priority data, enables workload classification MSRs on online CPUs, and exposes ranking data in debugfs.

Important APIs, types, and functions: `struct amd_shmem_info` models the PCCT shared-memory table. `struct amd_hfi_data` stores PCC/PCCT and debugfs state. `struct amd_hfi_cpuinfo` is per-CPU class data, including APIC ID, class count, IPCC scores, and `amd_hfi_classes`. Key functions include `amd_hfi_alloc_class_data()`, `amd_hfi_metadata_parser()`, `amd_hfi_fill_metadata()`, `amd_set_hfi_ipcc_score()`, `amd_hfi_online()`, `amd_hfi_offline()`, `update_hfi_ipcc_scores()`, debugfs `class_capabilities_show()`, and PM callbacks that toggle MSRs.

Control flow: module init first rejects systems without ACPI and required AMD heterogeneous/workload-class CPU features, creates a simple platform device, then registers the platform driver. Probe validates ACPI match `AMDI0104`, allocates class arrays sized by CPUID leaf `0x80000027`, reads the first PCCT PCC subspace, maps and copies shared memory, validates `PCC_SIGNATURE` and table version 2, walks bitmaps to map APIC IDs to CPU indices, fills per-class performance/efficiency rankings, writes scheduler IPCC scores, registers CPU hotplug online/offline callbacks, schedules ITMT support enablement, and creates `arch_debugfs_dir/amd_hfi/class_capabilities`.

State and persistence: HFI state is in devm allocations, one static platform device pointer, per-CPU `amd_hfi_cpuinfo`, a global mutex, and debugfs. Runtime MSR state is toggled for CPUs on hotplug, suspend, and resume. No persistent storage exists.

Dependencies and integration points: dependencies include ACPI PCCT/PCC, x86 CPUID and MSR interfaces, CPU hotplug, scheduler ITMT/prio hooks, topology APIC IDs, debugfs, and platform device infrastructure. It is built only when scheduler multicore priority support exists.

Risks: the parser assumes the first PCCT PCC subspace is the relevant HFI table and uses pointer arithmetic on firmware data; malformed tables can produce wrong rankings despite signature/version checks. Ranking index math depends on table layout and APIC enumeration. `cpuhp_setup_state()` return is not stored for removal, so full hotplug-state teardown is not visible in `amd_hfi_remove()`. Debugfs displays possible CPUs and assumes class arrays were allocated. Suspend/resume MSR writes can fail per CPU and abort the PM callback.

Test signals: boot logs on systems with `X86_FEATURE_AMD_HTR_CORES` and `X86_FEATURE_AMD_WORKLOAD_CLASS`, debugfs class table contents, `sched_set_itmt_core_prio()` effects on CPU priorities, hotplug online/offline MSR write success, suspend/resume retaining workload classification, and rejection on invalid PCCT signature/version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hfi/hfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Kconfig

Purpose: this Kconfig file defines AMD Host System Management Port support, split into shared common code plus ACPI and legacy platform front ends.

Important APIs, types, and functions: `AMD_HSMP` is a hidden tristate selected by `AMD_HSMP_ACPI` or `AMD_HSMP_PLAT`. `AMD_HSMP_ACPI` depends on ACPI and optionally hwmon. `AMD_HSMP_PLAT` is the platform-device probing path for systems without the ACPI object.

Control flow: selecting either front end selects the common HSMP core. The menu is visible only when `AMD_NODE` or `COMPILE_TEST` is set.

State and persistence: only kernel configuration state exists.

Dependencies and integration points: HSMP relies on AMD node/SMN support, optional hwmon, ACPI for modern probing, and platform-device probing for older systems. Help text documents user-space monitoring and management use on EPYC and MI300A server CPUs.

Risks: enabling both ACPI and platform paths requires runtime code to avoid duplicate binding. Optional hwmon support must compile both with and without `CONFIG_HWMON`.

Test signals: config combinations for ACPI-only, platform-only, both, and no hwmon; module names `hsmp_acpi` and `amd_hsmp`; and common object selection through `AMD_HSMP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Makefile

Purpose: this Makefile builds the HSMP common layer and its ACPI/platform front ends.

Important APIs, types, and functions: `hsmp_common.o` is built from `hsmp.o` and optionally `hwmon.o`. `amd_hsmp.o` is built from `plat.o`; `hsmp_acpi.o` is built from `acpi.o`.

Control flow: kbuild includes common code when `CONFIG_AMD_HSMP` is selected, the platform front end for `CONFIG_AMD_HSMP_PLAT`, and the ACPI front end for `CONFIG_AMD_HSMP_ACPI`.

State and persistence: build-only state.

Dependencies and integration points: object names match exported namespace use in front ends and optional hwmon integration.

Risks: omitting `hsmp_common` would break symbol imports for front ends. Optional hwmon inclusion must stay aligned with the inline fallback in `hsmp.h`.

Test signals: compile/link for all three config combinations and namespace import/export resolution for `AMD_HSMP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/acpi.c

Purpose: `acpi.c` is the ACPI front end for AMD HSMP. It binds ACPI HID `AMDI0097`, parses ACPI `_CRS` and `_DSD` mailbox descriptions for each socket, maps the mailbox MMIO region, validates HSMP via the common mailbox test, and exposes misc-device, sysfs, binary metrics, and optional hwmon interfaces.

Important APIs, types, and functions: `struct hsmp_sys_attr` binds a device attribute to an HSMP message ID. `amd_hsmp_acpi_rdwr()` performs MMIO reads/writes. `hsmp_get_uid()` maps ACPI UID strings like `ID00` to socket indices. `hsmp_read_acpi_crs()` maps the mailbox resource; `hsmp_read_acpi_dsd()` validates the HSMP UUID and extracts message ID/argument/response offsets. `init_acpi()` wires a socket, runs `hsmp_test()`, caches protocol version, maps metrics-table DRAM for protocol v6, and creates hwmon sensors. Attribute show helpers call `hsmp_msg_get_nargs()` and decode bandwidth, firmware version, clocks, and frequency-limit source fields.

Control flow: probe gets the shared `hsmp_pdev`, allocates the socket array once using `topology_max_packages()`, initializes the current ACPI device/socket, and registers the common misc device once. Device groups expose per-ACPI-device attributes and `metrics_bin` when protocol version is v6. Remove deregisters the misc device once and clears the probed flag.

State and persistence: the shared `hsmp_plat_device` singleton stores socket array, protocol version, and misc-device state. Each `hsmp_socket` stores MMIO base, offsets, mapped address, semaphore, socket index, and device pointer. No persistent storage exists; sysfs reads trigger live mailbox messages.

Dependencies and integration points: depends on ACPI methods `_CRS`, `_DSD`, device UID naming, common HSMP exported functions, miscdevice, sysfs binary attributes, topology package count, and optional hwmon. It imports the `AMD_HSMP` namespace.

Risks: `_DSD` parsing assumes expected package shape and nonzero offsets, so firmware defects block probing. The shared `proto_ver` is overwritten per socket and assumed uniform. `apmf_notify_smart_pc_update`-style partial initialization is not present, but allocating the socket array under the first ACPI device means devm lifetime is tied to that device while other socket devices may still exist. `hsmp_acpi_remove()` unregisters the misc device on any remove when `is_probed` is true, even in multi-socket scenarios.

Test signals: ACPI resource and UUID validation, per-socket UID parsing, successful `hsmp_test(0xDEADBEEF)`, `/dev/hsmp` misc node, sysfs attribute reads with decoded values, protocol-v6 `metrics_bin`, hwmon power sensors, and clean unload/rebind across multiple socket ACPI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.c

Purpose: `hsmp.c` is the common AMD HSMP mailbox core. It validates user and in-kernel HSMP messages, serializes access per socket, sends messages through a front-end-provided read/write callback, registers `/dev/hsmp`, and provides helpers for protocol version, metrics-table mapping, and test messages.

Important APIs, types, and functions: global `hsmp_pdev` is the shared singleton. `__hsmp_send_message()` implements the mailbox protocol: clear status, write arguments, write message ID, poll response, translate firmware status codes, and read response arguments. `validate_message()` checks `hsmp_msg_desc_table` from `<asm/amd/hsmp.h>`. Exported namespace APIs include `hsmp_send_message()`, `hsmp_msg_get_nargs()`, `hsmp_test()`, `hsmp_metric_tbl_read()`, `hsmp_get_tbl_dram_base()`, `hsmp_cache_proto_ver()`, `hsmp_misc_register()`, `hsmp_misc_deregister()`, and `get_hsmp_pdev()`. `hsmp_ioctl()` is the userspace ABI through `struct hsmp_message`.

Control flow: front ends initialize `hsmp_pdev.sock[]` and each socket's `amd_hsmp_rdwr` callback. Userspace opens `/dev/hsmp` with read/write permissions that gate GET vs SET messages in `hsmp_ioctl()`. In-kernel callers call exported functions directly. The core validates message IDs, argument counts, response sizes, socket range, and reserved messages before taking `hsmp_sem` and issuing firmware mailbox transactions.

State and persistence: state is volatile: the singleton platform-device data, per-socket semaphores, mapped metric-table addresses, and cached protocol version. There is no on-disk persistence. Mailbox commands can change firmware/platform state depending on message type.

Dependencies and integration points: the file depends on `<asm/amd/hsmp.h>` for message IDs, descriptors, and metric-table structures. It integrates with miscdevice for userspace, devm ioremap in front ends for metrics, namespace exports for `hsmp_acpi`, `amd_hsmp`, and `hwmon`.

Risks: userspace ABI correctness depends on `copy_struct_from_user()` size expectations and descriptor-table accuracy. `hsmp_msg_get_nargs()` sets `response_sz` but not `num_args`, so it only works for GET-style messages whose descriptor expects zero input arguments. `hsmp_get_tbl_dram_base()` indexes `hsmp_pdev.sock[sock_ind]` without a local socket-range guard. Mailbox polling timeout and status translations directly affect user-visible error semantics.

Test signals: ioctl permission gating for read-only/write-only/read-write opens, validation failures for reserved/bad messages, concurrent per-socket serialization, firmware error-code mapping, successful TEST response value+1, metrics-table binary read size enforcement, and namespace symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.h

Purpose: `hsmp.h` is the internal HSMP header shared by the common core, ACPI front end, platform front end, and hwmon support.

Important APIs, types, and functions: it defines device names (`hsmp_cdev`, `hsmp`), ACPI HID `AMDI0097`, driver version, `struct hsmp_mbaddr_info`, `struct hsmp_socket`, and `struct hsmp_plat_device`. It declares common APIs for mailbox tests, ioctl handling, misc registration, metrics-table reads, protocol caching, socket singleton access, and `hsmp_msg_get_nargs()`. It conditionally declares or stubs `hsmp_create_sensor()` based on `CONFIG_HWMON`.

Control flow: not executable, but it defines how front ends populate socket read/write callbacks and how optional hwmon hooks compile away.

State and persistence: structures define runtime state but do not instantiate it. State includes MMIO addresses, metric-table mappings, semaphores, socket indices, protocol version, and misc-device status.

Dependencies and integration points: includes compiler, device, hwmon, kconfig, miscdevice, PCI, semaphore, and sysfs headers. It bridges kernel internal code to UAPI message definitions in `<asm/amd/hsmp.h>`.

Risks: because this header defines shared structures, ABI-like assumptions exist across objects. Changing fields can affect all front ends. The hwmon stub returns success, so callers must not assume a real sensor exists when `CONFIG_HWMON` is off.

Test signals: compile with and without `CONFIG_HWMON`, namespace exports using declared functions, and structure field consistency between ACPI/platform/common source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hwmon.c

Purpose: `hwmon.c` exposes HSMP socket power readings and power-limit control through the Linux hwmon subsystem.

Important APIs, types, and functions: `hsmp_hwmon_read()` maps `hwmon_power_input`, `hwmon_power_cap`, and `hwmon_power_cap_max` to `HSMP_GET_SOCKET_POWER`, `HSMP_GET_SOCKET_POWER_LIMIT`, and `HSMP_GET_SOCKET_POWER_LIMIT_MAX`. `hsmp_hwmon_write()` maps writable `hwmon_power_cap` to `HSMP_SET_SOCKET_POWER_LIMIT`. `hsmp_hwmon_is_visble()` defines permissions, `hsmp_chip_info` describes the channel, and exported `hsmp_create_sensor()` registers a devm hwmon device named `amd_hsmp_hwmon`.

Control flow: front ends call `hsmp_create_sensor(dev, sock_ind)` after validating a socket. The socket index is stored as hwmon drvdata via `(void *)(uintptr_t)sock_ind`. Hwmon reads and writes construct `struct hsmp_message` and call the common `hsmp_send_message()`.

State and persistence: no local persistent state. Writes can persist in SMU/platform firmware for the runtime power limit. Values are converted between HSMP milliwatts and hwmon microwatts.

Dependencies and integration points: depends on hwmon, units constants, and the common HSMP namespace. It integrates with standard `/sys/class/hwmon` power attributes.

Risks: conversion uses `long val / MICROWATT_PER_MILLIWATT` for writes and multiplication for reads, so bounds depend on `long` size and firmware-supported limits. Only power sensors are accepted; all other types return `-EOPNOTSUPP`. There is no channel distinction beyond one power channel per registered sensor.

Test signals: hwmon device creation per socket, readable `power1_input`, `power1_cap`, `power1_cap_max`, writable `power1_cap`, unit conversions, and failure propagation from `hsmp_send_message()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/plat.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/plat.c

Purpose: `plat.c` is the legacy non-ACPI HSMP front end. It creates a synthetic platform device on supported AMD families, accesses HSMP mailboxes through AMD SMN/PCI helpers, registers `/dev/hsmp`, and exposes per-socket metrics binary attributes.

Important APIs, types, and functions: `amd_hsmp_pci_rdwr()` bridges common mailbox access to `amd_smn_hsmp_rdwr()`. `init_platform_device()` initializes all sockets with hardcoded SMN offsets, tests each socket, caches protocol version, optionally maps protocol-v6 metrics DRAM, and registers hwmon sensors. `legacy_hsmp_support()` gates supported CPU families/models. `hsmp_plt_init()` rejects systems with the ACPI HSMP device, checks legacy support, obtains `amd_num_nodes()`, registers the platform driver, and creates the platform device.

Control flow: `device_initcall()` runs at boot/module init. On legacy supported systems without ACPI `AMDI0097`, it registers `amd_hsmp` and probes the synthetic device. Probe allocates socket array, initializes mailboxes for each node/socket, and registers the misc device. Remove deregisters misc. Module exit unregisters platform device and driver.

State and persistence: shared `hsmp_pdev`, socket array, mapped metric-table addresses, protocol version, and static platform device pointer are runtime-only. Mailbox writes can affect firmware/runtime power-management settings.

Dependencies and integration points: depends on AMD node/SMN support, PCI/platform driver core, sysfs binary attributes, common HSMP exports, optional hwmon, and CPU family/model data. The static sysfs groups cover `socket0` through `socket7`, guarded by `MAX_AMD_NUM_NODES == 8`.

Risks: hardcoded SMN offsets must match CPU family/model, with a special case for family 0x1A model <= 0x0F. The global `proto_ver` is shared even though initialization loops all sockets. Metrics sysfs groups are statically sized to eight sockets. The ACPI-present check is essential to prevent duplicate front ends.

Test signals: boot on legacy supported family/model without ACPI object, socket count from `amd_num_nodes()`, successful TEST per socket, `/dev/hsmp`, `socketN/metrics_bin` visibility only for protocol v6 and valid sockets, hwmon registration, and refusal when ACPI HSMP is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Kconfig

Purpose: this Kconfig file defines AMD Power Management Controller support and the optional MP2 Smart Trace Buffer helper.

Important APIs, types, and functions: `AMD_PMC` is a tristate depending on ACPI, PCI, RTC_CLASS, AMD_NODE, SUSPEND, and selecting SERIO. `AMD_MP2_STB` is a bool depending on `AMD_PMC`, defaulting to it.

Control flow: enabling `AMD_PMC` builds the PMC module; enabling `AMD_MP2_STB` includes MP2 STB support in the composite object.

State and persistence: configuration persists in `.config`.

Dependencies and integration points: dependencies mirror runtime integration with ACPI LPS0, root PCI/SMN access, RTC wake-alarm workarounds, AMD node access, suspend callbacks, and serio wakeup manipulation.

Risks: defaulting MP2 STB on broadens debugfs and PCI probing behavior. Missing dependencies would fail compile or produce runtime stubs for suspend/RTC paths.

Test signals: config visibility on AMD x86 builds, successful module build as `amd-pmc`, and inclusion/exclusion of `mp2_stb.o` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Makefile

Purpose: this Makefile builds the AMD PMC composite object.

Important APIs, types, and functions: `amd-pmc-y` contains `pmc.o`, `pmc-quirks.o`, and `mp1_stb.o`; `amd-pmc-$(CONFIG_AMD_MP2_STB)` conditionally adds `mp2_stb.o`.

Control flow: kbuild links one module/object named `amd-pmc` when `CONFIG_AMD_PMC` is enabled, with optional MP2 STB code.

State and persistence: build-only state.

Dependencies and integration points: maps PMC Kconfig symbols to implementation files and ensures quirk and MP1 STB support are always present with PMC.

Risks: because STB and quirks are linked unconditionally into PMC, their symbols and module parameters are always present when PMC is present. Optional MP2 paths must compile out cleanly.

Test signals: build with `AMD_MP2_STB=y` and disabled; check that `stb_read_previous_boot` debugfs support appears only with MP2 STB compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp1_stb.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp1_stb.c

Purpose: `mp1_stb.c` implements AMD MP1 Smart Trace Buffer support for PMC S2Idle debugging. It can write PM event markers to STB, dump legacy FIFO STB data, and on newer systems map firmware spill-to-DRAM telemetry for debugfs reads.

Important APIs, types, and functions: module parameters `enable_stb` and `dump_custom_stb` control STB debug setup. Exported helpers to PMC are `amd_stb_write()`, `amd_stb_read()`, and `amd_stb_s2d_init()`. Legacy debugfs uses `amd_stb_debugfs_fops`; enhanced spill-to-DRAM uses `amd_stb_debugfs_fops_v2` and `struct amd_stb_v2_data`. `amd_is_stb_supported()` selects S2D message IDs by CPU/root device; `amd_stb_update_args()` selects message/argument/response register offsets, with Zen5 model 0x44 special handling.

Control flow: PMC probe calls `amd_stb_s2d_init()`. If `enable_stb` is false, no debugfs file is added. Unsupported systems get a legacy `stb_read` file backed by repeated SMN reads from `AMD_STB_PMI_0`. Supported systems set S2D message-port offsets, query telemetry size and DRAM address through `amd_pmc_send_cmd()` while temporarily setting `dev->msg_port = MSG_PORT_S2D`, map the DRAM buffer, and create enhanced `stb_read`. Opening enhanced debugfs writes a dummy postcode, optionally flushes firmware data, reads either the full custom buffer or a ring-ordered slice based on sample count, and serves it through `simple_read_from_buffer()`.

State and persistence: state lives in `amd_pmc_dev` fields `stb_virt_addr`, `dram_size`, `msg_port`, and `stb_arg`. Debugfs open allocates per-file buffers. Firmware STB contents persist across the relevant firmware runtime window but are not stored by the driver.

Dependencies and integration points: depends on AMD SMN read/write helpers, PMC SMU command transport, debugfs, and CPU feature/model detection. PMC S2Idle paths call `amd_stb_write()` for prepare/check/restore breadcrumbs.

Risks: `dev->msg_port` is shared with normal PMC command paths; failures in `amd_stb_s2d_init()` before resetting it could leave subsequent SMU commands using S2D offsets. Enhanced open sets S2D mode, calls a flush command, and only resets after the sample-count command; early custom STB path bypasses the reset. Firmware-reported sizes and DRAM addresses are trusted after basic checks. Debugfs can allocate large buffers up to firmware DRAM size.

Test signals: `enable_stb=1` creates `amd_pmc/stb_read`, legacy FIFO reads produce 4096 u32 entries, enhanced systems map S2D DRAM and produce ring-ordered data, prepare/check/restore STB writes succeed during S2Idle, and `msg_port` returns to PMC after debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp1_stb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp2_stb.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp2_stb.c

Purpose: `mp2_stb.c` adds MP2 previous-boot STB dumping to the AMD PMC debugfs tree. It discovers a PCI MP2 STB device, maps its MMIO BAR, allocates DMA/coherent buffers, issues MP2 mailbox commands, and exposes captured STB data through `stb_read_previous_boot`.

Important APIs, types, and functions: `struct mp2_cmd_base`, `struct mp2_cmd_response`, and `struct mp2_stb_data_valid` model MP2 command/status registers. `amd_mp2_stb_init()` probes PCI device `PCI_DEVICE_ID_AMD_MP2_STB`, enables the device, maps BAR 2, sets DMA mask, and registers debugfs. `amd_mp2_process_cmd()` validates data availability/length, allocates buffers via `amd_mp2_stb_region()`, sends a DMA command, waits for response, and copies data. `amd_mp2_stb_deinit()` clears bus mastering, releases PCI reference and devres group, and clears `dev->mp2`.

Control flow: PMC probe calls `amd_mp2_stb_init()` when compiled. The debugfs open path lazily fetches STB data on first open; later opens reuse cached `mp2->stbdata` while `is_stb_data` is true. Reads stream the cached buffer. Deinit runs during PMC removal.

State and persistence: `struct amd_mp2_dev` is devm-allocated under the PMC device but owns resources under the MP2 PCI device through a devres group. It stores MMIO mapping, coherent DMA address, copied data buffer, length, and cache-valid flag. Previous-boot STB content is fetched from MP2 firmware/device state and cached until deinit.

Dependencies and integration points: depends on PCI, DMA coherent allocation, MMIO polling, debugfs, and the PMC device debugfs root. It uses `writeq()` to pass DMA address and MP2 C2P/P2C registers for command exchange.

Risks: `amd_mp2_stb_region()` checks `!mp2->stbdata` before allocation, but `stb_len` can change if firmware reports a different length on a later uncached attempt. Cached data is never refreshed after first success. Error cleanup spans two devices and relies on devres group release. Debugfs open can fail with `-EBADMSG`, `-EMSGSIZE`, timeout, or unsupported status depending on firmware registers.

Test signals: PCI device discovery, BAR2 mapping, DMA mask success, debugfs file creation, valid data marker `0xA`, supported length codes 1 and 4 mapping to 2 KiB/16 KiB, MP2 response status 2, stable cached reads, and deinit releasing PCI resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp2_stb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc-quirks.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc-quirks.c

Purpose: `pmc-quirks.c` contains DMI-based workarounds for AMD PMC S2Idle firmware issues, primarily skipping a problematic NVMe SMI handler and disabling spurious IRQ1/i8042 wakeups on affected systems.

Important APIs, types, and functions: `struct quirk_entry` has `s2idle_bug_mmio` and `spurious_8042` fields. Static quirk instances are referenced by `fwbug_list`, a large DMI table. `amd_pmc_quirks_init()` applies default Cezanne IRQ1 behavior, looks up DMI quirks, and sets `dev->quirks` and `dev->disable_8042_wakeup`. `amd_pmc_process_restore_quirks()` calls `amd_pmc_skip_nvme_smi_handler()` when configured.

Control flow: PMC probe calls `amd_pmc_quirks_init()` unless workarounds are disabled. On S2Idle restore, the PMC core calls `amd_pmc_process_restore_quirks()` after SMU restore and STB logging. The MMIO workaround requests one byte at an FCH scratch address, maps it, clears bit 0, unmaps, and releases the region.

State and persistence: quirk state is stored in the runtime `amd_pmc_dev`. The MMIO workaround mutates platform firmware/FCH scratch state for the resume path but does not store driver-owned persistent data.

Dependencies and integration points: depends on DMI matching, FCH platform-data constants, MMIO resource claiming, and PMC core restore/suspend hooks. It coordinates with `amd_pmc_suspend_handler()` via `disable_8042_wakeup`.

Risks: DMI matching must be precise; too broad matches can alter wake behavior or MMIO bits on unaffected systems, while missing matches leave suspend/resume bugs. The MMIO workaround silently returns if the region cannot be requested or mapped. Default Cezanne IRQ1 workaround can be overridden only by DMI quirk data and module-level `disable_workarounds` in PMC core.

Test signals: DMI match logs, `dev->disable_8042_wakeup` set for expected systems, IRQ1 wake disabled during suspend, bit 0 cleared at the configured FCH scratch byte on restore, and no quirk activity when `disable_workarounds=1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc.c

Purpose: `pmc.c` is the AMD SoC Power Management Controller driver. It binds ACPI PMC devices, locates the AMD root PCI/SMN base, maps SMU registers, registers ACPI LPS0/S2Idle callbacks, exposes SMU firmware/debug data, applies platform workarounds, and coordinates STB logging.

Important APIs, types, and functions: global `struct amd_pmc_dev pmc` stores all PMC state. `amd_pmc_send_cmd()` is the locked SMU command transport. `amd_pmc_get_ip_info()` selects IP block maps and message register offsets by CPU/root-device ID. `amd_pmc_setup_smu_logging()`, `get_metrics_table()`, and debugfs show functions expose SMU metrics, active IPs, S0ix stats, and idle masks. S2Idle flow is implemented by `amd_pmc_s2idle_prepare()`, `amd_pmc_s2idle_check()`, and `amd_pmc_s2idle_restore()` registered via `acpi_register_lps0_dev()`. Probe and remove manage ACPI/platform lifecycle.

Control flow: probe finds root PCI device 00:00.0, rejects unsupported IDs and server parts without S0i3, reads SMU base address through AMD SMN registers, maps PMC MMIO, initializes the mutex and IP metadata, registers LPS0 callbacks and quirks, creates debugfs files, initializes MP1 S2D STB and optional MP2 STB, and reports max hardware sleep. During S2Idle, prepare starts SMU logging, applies RTC workaround if needed, sends OS hint, and writes STB prepare marker. Check may delay to avoid OVP, dumps idlemask, and writes STB check marker. Restore sends OS hint, asks SMU to dump metrics, writes STB restore marker, reports deepest-state residency, and runs restore quirks.

State and persistence: state is global singleton `pmc`, including mapped MMIO, root PCI reference, SMU logging DRAM mapping, FCH mapping, debugfs root, quirks, STB state, and cached SMU version. Firmware state is affected by OS hint commands, logging commands, power-management workarounds, and RTC alarm handling. No driver file persistence exists.

Dependencies and integration points: depends on ACPI device IDs, PCI root device IDs, AMD SMN helpers, suspend/LPS0 framework, RTC class, serio bus, debugfs, PM reporting (`pm_report_hw_sleep_time()`), and STB helpers. User-visible surfaces include sysfs `smu_fw_version`/`smu_program` and debugfs `amd_pmc` files.

Risks: `amd_pmc_send_cmd()` trusts that response register nonzero means ready and serializes all SMU/S2D messages through one mutex; wrong `msg_port` state from STB code can redirect commands. Probe error after STB init path can leak root PCI reference only through `err_pci_dev_put`, but debugfs or LPS0 partial registration need careful unwinding. RTC workaround opens `rtc0` and has early returns that do not always close the RTC device. S2Idle failures are logged but do not necessarily abort all suspend paths.

Test signals: ACPI match and root PCI ID detection, MMIO mapping, sysfs firmware version read, debugfs SMU metrics/S0ix/idlemask output, LPS0 callback registration, OS hint command success on suspend/resume, idle-mask values in PM debug, STB markers, DMI quirk behavior, and no binding on unsupported CPU IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc.h

Purpose: `pmc.h` is the shared header for AMD PMC core, quirks, and STB helpers.

Important APIs, types, and functions: it defines PMC SMU registers, scratch registers, STB marker constants, mapping sizes and SMU base registers, response codes, FCH S0i3 offsets, SMU message IDs, supported CPU/root-device IDs, `enum s2d_msg_port`, `struct amd_mp2_dev`, `struct stb_arg`, `struct amd_pmc_dev`, IP bitmap and metrics-table structures, and prototypes for quirks, MP2 STB, MP1 STB, and `amd_pmc_send_cmd()`.

Control flow: not executable, but it encodes the register and message contract used by all PMC components. `amd_pmc_dev.msg_port` controls whether `amd_pmc_send_cmd()` uses normal PMC registers or S2D STB registers.

State and persistence: structure definitions describe runtime state such as MMIO mappings, root PCI device reference, active IP bitmaps, SMU version, debugfs root, quirks, MP2 pointer, and STB arguments. No state is instantiated here.

Dependencies and integration points: includes Linux types and mutex. It bridges core PMC, DMI quirks, MP1 STB, and MP2 STB into one composite module.

Risks: register constants are hardware-specific; mistakes affect suspend/resume firmware commands. Shared `amd_pmc_dev` fields create coupling between normal PMC and STB code, especially `msg_port` and `stb_arg`. CPU ID definitions overlap with root PCI IDs and must remain synchronized with probe tables.

Test signals: compile coverage of all consumers, correct SMU command offsets per CPU family, STB S2D command routing, and structure layout compatibility across composite object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/pmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Kconfig

Purpose: this Kconfig file defines AMD Platform Management Framework support and optional PMF debug logging.

Important APIs, types, and functions: `AMD_PMF` is a tristate depending on ACPI, PCI, POWER_SUPPLY, AMD_NODE, TEE/AMDTEE, AMD_SFH_HID, and I/O memory, and selecting ACPI platform profile support. `AMD_PMF_DEBUG` gates additional debug logs for OEM-provided power settings.

Control flow: selecting `AMD_PMF` builds the composite PMF module. Selecting debug enables verbose dump helpers inside PMF sources.

State and persistence: only kernel config state exists.

Dependencies and integration points: dependencies reflect runtime use of ACPI APMF/APTS, root PCI/SMN, power-supply notifications, platform profile, AMD TEE policy engine, AMD SFH sensors, and MMIO.

Risks: the hard dependency on TEE/AMDTEE and AMD SFH means PMF availability is constrained even for systems that might only use static-slider features. Debug builds can expose extensive OEM configuration in logs.

Test signals: Kconfig visibility, module build as `amd_pmf`, successful compile with debug enabled/disabled, and dependency-driven symbol selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Makefile

Purpose: this Makefile builds the AMD PMF composite object.

Important APIs, types, and functions: `amd-pmf-y` contains `core.o`, `acpi.o`, `sps.o`, `auto-mode.o`, `cnqf.o`, `tee-if.o`, and `spc.o`.

Control flow: kbuild links all PMF feature layers into one module/object when `CONFIG_AMD_PMF` is enabled.

State and persistence: build-only state.

Dependencies and integration points: the object list reflects PMF layering: core lifecycle/SMU, ACPI method interface, static slider, auto mode, CnQF dynamic slider, TEE policy engine, and Smart PC input collection.

Risks: all layers are linked together, so Kconfig dependencies must satisfy every source file even if a platform uses only a subset of PMF features.

Test signals: successful composite build and expected `MODULE_SOFTDEP("pre: amdtee")` behavior from the core module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/acpi.c

Purpose: `acpi.c` is the PMF ACPI method and notification layer. It wraps APMF and APTS method calls, validates returned buffers, discovers supported PMF functions and notification masks, manages SBIOS heartbeat, installs ACPI notify handlers, and queues Smart PC custom BIOS input events.

Important APIs, types, and functions: `apmf_if_call()` invokes ACPI method `APMF` with a function ID and optional buffer. `apmf_if_call_store_buffer()` and `apts_if_call_store_buffer()` validate ACPI buffer type, embedded size, and minimum output size before copying into typed structs. Exported PMF helpers include `is_apmf_func_supported()`, `apmf_get_static_slider_granular*()`, `apmf_os_power_slider_update()`, `amd_pmf_notify_sbios_heartbeat_event_v2()`, `apmf_update_fan_idx()`, `apmf_get_auto_mode_def()`, `apmf_get_sbios_requests*()`, `apmf_get_dyn_slider_def_ac/dc()`, `apmf_install_handler()`, `apmf_check_smart_pc()`, `amd_pmf_smartpc_apply_bios_output()`, `apmf_acpi_init()`, and `apmf_acpi_deinit()`.

Control flow: core probe calls `apmf_acpi_init()`, which verifies the interface, records supported functions, PMF interface version, and notification mask, reads system params, and starts v1 heartbeat work when requested. Feature layers call getter wrappers to load OEM ACPI tables. `apmf_install_handler()` installs a legacy auto-mode notify handler when Auto Mode and SBIOS requests are supported, then installs a Smart PC custom BIOS input handler for PMF IF v1/v2 when enabled. Notify handlers read SBIOS request buffers, update AMT/CQL state, or enqueue custom BIOS input snapshots into a circular buffer for later TA input collection.

State and persistence: ACPI-derived state is stored in `amd_pmf_dev`: `supported_func`, `notifications`, `pmf_if_version`, `hb_interval`, request structs, custom BIOS previous values, and circular-buffer indices. Heartbeat is delayed work. No file persistence exists; ACPI calls may notify SBIOS of runtime events and Smart PC outputs.

Dependencies and integration points: depends on ACPI method semantics, APMF function numbering, APTS state indexing, PMF core workqueues, custom BIOS input bitmaps from `pmf.h`, and Smart PC/auto-mode consumers. It also extracts the Smart PC policy memory resource from the platform device.

Risks: `apmf_notify_smart_pc_update()` initializes only one `custom_bios[index]` field in a stack struct without zeroing the whole struct, so uninitialized values could be passed to firmware. Several callers ignore ACPI getter return values and may use default-zero data after firmware errors. Handler installation can install both legacy and Smart PC handlers on `ACPI_ALL_NOTIFY`, so deinit must remove the exact function pointers. Circular-buffer overflow drops oldest custom BIOS input values with a warning.

Test signals: APMF verify logs supported functions/version/notifications, heartbeat scheduling and v2 load/unload/suspend/resume events, static/dynamic slider buffer validation, ACPI notify events toggling AMT/CQL, custom BIOS input ring behavior, Smart PC resource validation, and clean handler removal on driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/auto-mode.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/auto-mode.c

Purpose: `auto-mode.c` implements PMF Auto Mode, a firmware-configured dynamic thermal/power policy that transitions among quiet, balanced, performance, and performance-on-lap modes based on averaged socket power and CQL notifications.

Important APIs, types, and functions: static `struct auto_mode_mode_config config_store` holds transition thresholds/timers and per-mode power/fan settings. `amd_pmf_load_defaults_auto_mode()` reads `struct apmf_auto_mode` through ACPI and populates config. `amd_pmf_trans_automode()` applies the transition algorithm on each metrics sample. `amd_pmf_set_automode()` sends SPL/FPPT/SPPT/SPPT_APU_ONLY/STT limits to SMU and optionally updates fan index through ACPI. Public functions include `amd_pmf_update_2_cql()`, `amd_pmf_reset_amt()`, `amd_pmf_handle_amt()`, `amd_pmf_init_auto_mode()`, and `amd_pmf_deinit_auto_mode()`.

Control flow: initialization loads ACPI defaults, sets initial mode to balanced, initializes moving-average history, and starts the PMF metrics delayed work. Each metrics tick computes a 3-sample moving average, updates per-transition timers depending on threshold direction, marks transitions applied/unapplied, then selects the first applied transition as highest priority and sends the target mode limits if the mode changed. CQL notifications can redirect the performance target between normal performance and on-lap performance.

State and persistence: Auto Mode state is global to the module through `config_store`; per-device history index and socket power samples live in `amd_pmf_dev`. SMU power limits and fan index are runtime firmware/device state. No persistent storage exists.

Dependencies and integration points: depends on ACPI `APMF_FUNC_AUTO_MODE`, PMF core metrics scheduling, SMU command transport, optional `APMF_FUNC_SET_FAN_IDX`, and static-slider fallback for reset. It integrates with `acpi.c` notify handling for AMT/CQL and with `core.c` metrics collection.

Risks: `config_store` is static global, so multiple PMF devices would conflict. `amd_pmf_load_defaults_auto_mode()` does not check the return from `apmf_get_auto_mode_def()`, risking zeroed or stale defaults. Several `amd_pmf_send_cmd()` calls ignore failures, so partial mode application is possible. Threshold calculations subtract deltas from power floors with unsigned arithmetic and can underflow if firmware provides inconsistent values.

Test signals: ACPI defaults load, initial balanced mode application on AMT enable, moving-average transitions at configured thresholds/time constants, CQL toggling performance-on-lap limits, fan index automatic/manual behavior, metrics work cancellation on deinit, and static-slider restoration on AMT reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/auto-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/cnqf.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/cnqf.c

Purpose: `cnqf.c` implements PMF CnQF dynamic slider behavior. It transitions among quiet, balanced, performance, and turbo modes using AC/DC-specific firmware tables, platform-profile state, power-source state, and averaged socket power over transition windows.

Important APIs, types, and functions: static `struct cnqf_config config_store` stores per-source transition parameters and mode settings. `amd_pmf_load_defaults_cnqf()` reads AC/DC dynamic slider definitions through `apmf_get_dyn_slider_def_ac/dc()`. `amd_pmf_update_mode_set()`, `amd_pmf_update_trans_data()`, and `amd_pmf_update_power_threshold()` populate the runtime table. `amd_pmf_trans_cnqf()` is the metrics-driven transition engine. `cnqf_enable` sysfs attribute toggles runtime CnQF enablement through `cnqf_feature_attribute_group`.

Control flow: init loads defaults for supported AC/DC functions, starts metrics-table work, marks CnQF supported, initializes enablement from firmware flags, and applies balanced-mode limits if enabled and the platform profile is balanced. Each metrics tick chooses the active power source, refuses to enforce CnQF if the user-selected profile is not balanced, accumulates socket power over each transition time constant, sets priority booleans when averages cross thresholds, and applies the first/highest-priority target mode.

State and persistence: CnQF runtime state includes static global config, `dev->cnqf_supported`, `dev->cnqf_enabled`, metrics work, and firmware-applied SMU/fan settings. The sysfs toggle affects runtime only.

Dependencies and integration points: depends on ACPI dynamic slider functions, platform profile support through `is_pprof_balanced()`, PMF metrics work, power-supply source detection, SMU command transport, and optional fan-index ACPI method. Sysfs visibility is controlled by `cnqf_feature_is_visible()`.

Risks: global `config_store` prevents safe multi-device use. `amd_pmf_check_flags()` does not check ACPI getter return status before using `out.flags`. Time/power accumulators are 32-bit and can overflow under long intervals or large power values. Power-source mapping assumes `APMF_FUNC_DYN_SLIDER_AC + i` matches AC then DC function IDs. Send-command failures are ignored during mode application, allowing partial policy updates.

Test signals: `cnqf_enable` visibility only after supported init, AC/DC table loading, default enablement from flags, profile-balanced gating, transitions through all six priority directions, power-source switching, fallback to static slider when disabled, and work cancellation on deinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/cnqf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/core.c

Purpose: `core.c` is the PMF lifecycle and SMU transport core. It probes ACPI PMF devices, maps SMU registers, initializes ACPI and feature layers, manages metrics-table transfer, exposes NPU metrics to other kernel users, handles suspend/resume, and coordinates Smart PC/Auto Mode/CnQF selection.

Important APIs, types, and functions: module parameters include `metrics_table_loop_ms`, `force_load`, and `smart_pc_support`. `amd_pmf_send_cmd()` is the locked SMU command path. `amd_pmf_set_dram_addr()` allocates/selects metrics buffer size by CPU and programs its physical address to SMU. `amd_pmf_init_metrics_table()` starts delayed metrics work; `amd_pmf_get_metrics()` transfers metrics and calls Auto Mode/CnQF transition engines. `amd_pmf_get_npu_data()` is exported in namespace `AMD_PMF`. Probe/remove are `amd_pmf_probe()` and `amd_pmf_remove()`.

Control flow: probe ACPI-matches PMF device IDs, optionally blocks older `AMDI0100` unless `force_load`, allocates `amd_pmf_dev`, verifies root PCI ID, maps SMU MMIO from AMD SMN base registers, initializes mutexes, runs ACPI init, stores drvdata, registers debugfs, initializes features, installs ACPI notify handlers, sends SBIOS load heartbeat v2, and records a global `pmf_device`. Feature initialization enables static slider/platform profiles and power-source notifier, tries Smart PC first, otherwise enables Auto Mode or CnQF based on supported ACPI functions. PM callbacks restore metrics DRAM address after resume/restore and suspend/reinitialize TEE policy work as needed.

State and persistence: per-device state holds MMIO base, metrics buffers/tables, delayed works, current platform profile, debugfs root, Smart PC/TEE fields, ACPI notification state, custom BIOS input state, and locks. `pmf_device` is a global pointer for exported NPU metrics. Firmware-visible runtime state includes SMU metrics-buffer address and applied power/thermal policies.

Dependencies and integration points: depends on ACPI, PCI root device matching, AMD SMN, power_supply notifications, platform profile, debugfs, TEE/Smart PC helpers, AMD SFH through SPC, and PM sleep callbacks. The exported NPU metrics API integrates with other AMD components.

Risks: `apmf_acpi_init(dev)` return is ignored in probe, so feature initialization can continue after ACPI interface failure. `pmf_device` is not cleared on remove, creating stale global access risk. Metrics buffer uses `virt_to_phys()` on `devm_kzalloc()` memory instead of DMA APIs, which depends on platform memory assumptions. Repeated NPU data calls with `alloc_buffer=true` can allocate a new devm buffer each time. Power-source notifier registration return is ignored.

Test signals: ACPI/PCI match success and old-device `force_load` behavior, SMU command response handling, metrics transfer cadence, platform profile and power-source notifier behavior, feature selection precedence with Smart PC over Auto/CnQF, NPU metrics export on supported CPUs, suspend/resume reprogramming of DRAM address, and clean remove/deinit ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/pmf.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/pmf.h

Purpose: `pmf.h` is the shared PMF contract across core, ACPI, static slider, Auto Mode, CnQF, Smart PC, TEE, and SPC layers.

Important APIs, types, and functions: it defines policy buffer limits, APMF function IDs, SMU message IDs, platform profile slider constants, PMF policy action IDs, TA UUIDs, APMF/SBIOS request structures, SMU metrics v1/v2 structures, power source/mode enums, `struct amd_pmf_dev`, static-slider structures, auto-mode and CnQF configuration structures, Smart PC condition/action/TA shared-memory structures, and cross-file prototypes.

Control flow: not executable, but it defines the data flow: ACPI fills APMF structures, core stores them in `amd_pmf_dev`, metrics/feature engines consume them, Smart PC populates TA enact inputs, TEE returns policy actions, and core/feature layers apply SMU/ACPI outputs.

State and persistence: `struct amd_pmf_dev` centralizes runtime state including MMIO mapping, metrics buffers, delayed works, locks, debugfs, platform profile device, Smart PC policy buffer/TEE session/shared memory, ACPI request snapshots, custom BIOS input ring, and feature flags. No state is instantiated in the header.

Dependencies and integration points: includes ACPI, AMD PMF I/O UAPI, circular buffer helpers, input, platform device, and platform profile. It exposes `amd_pmf_get_npu_data()` indirectly through core source and declares namespace-shared PMF functions.

Risks: duplicated declaration of `amd_pmf_source_as_str()` suggests header drift. Many packed firmware structures require exact layout with ACPI/TEE/SBIOS contracts; changes can break firmware ABI. The central device struct creates tight coupling and makes partial feature builds hard, reflected by broad Kconfig dependencies.

Test signals: compile all PMF objects with this header, validate packed struct sizes against firmware expectations, exercise PMF IF v1/v2 paths, Smart PC custom BIOS input mapping, metrics v1/v2 CPU selection, and namespace consumers of exported PMF APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/pmf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/spc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/spc.c

Purpose: `spc.c` implements Smart PC input collection for the PMF TEE policy engine. It gathers system, power, thermal, battery, sensor-fusion, platform-profile, lid, and custom BIOS input data into `struct ta_pmf_enact_table`.

Important APIs, types, and functions: public `amd_pmf_populate_ta_inputs()` fills TA enact inputs. Debug builds provide string converters and `amd_pmf_dump_ta_inputs()`. Helpers include `amd_pmf_get_smu_info()`, `amd_pmf_get_battery_info()`, `amd_pmf_get_slider_info()`, `amd_pmf_get_sensor_info()`, `amd_pmf_get_custom_bios_inputs()`, and custom BIOS mapping helpers that split inputs across `bios_input_1` and `bios_input_2`.

Control flow: when the TEE policy engine invokes enactment, PMF calls `amd_pmf_populate_ta_inputs()`. It sets lid state from ACPI, power source from PMF core, transfers fresh SMU metrics into the selected v1/v2 metrics table, reads battery properties, maps current platform profile to TA slider enum, asks AMD SFH for ALS/HPD/SRA data, and consumes at most one queued custom BIOS input snapshot while preserving previous values for unchanged inputs.

State and persistence: SPC reads and updates `amd_pmf_dev` metrics tables, custom BIOS previous-value storage, and circular-buffer tail. It does not persist data outside runtime memory. TA inputs are a snapshot of current system state plus preserved custom BIOS input state.

Dependencies and integration points: depends on ACPI lid helpers, power_supply APIs, AMD SFH HID information (`amd_get_sfh_info()`), PMF metrics transfer and platform profile state, and ACPI custom BIOS input queueing from `acpi.c`.

Risks: `amd_pmf_get_battery_prop()` loops possible battery names but returns `value.intval` even if no supply was found, leaving an uninitialized return path. It also does not break after a successful read, so later missing supplies do not stop prior value use clearly. Several input-gathering helpers ignore failures in the top-level populate path, meaning TA may receive default or stale values. SMU metric transfer send-command failures are not checked before copying from `dev->buf`.

Test signals: TA input snapshots under AC/DC, battery present/absent cases, platform-profile mapping for performance/balanced/low-power profiles, SFH ALS/HPD/SRA availability and absence, lid open/closed mapping, custom BIOS input queue consumption and previous-value preservation, and debug dumps when `AMD_PMF_DEBUG` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/spc.c -->
