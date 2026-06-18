# Research Report: subset-b-005019

This grouped report covers the requested PECI core/controller files and performance-monitor drivers. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/peci-npcm.c -->
# sources/distributed-fs/ceph-client/drivers/peci/controller/peci-npcm.c

Purpose: Implements the Nuvoton NPCM PECI controller driver. It exposes an MMIO-backed `struct peci_controller_ops` transfer function, initializes NPCM PECI timing/control registers, handles transfer completion interrupts, and registers the controller on the PECI bus for `nuvoton,npcm750-peci` and `nuvoton,npcm845-peci` platform devices.

Important APIs and functions: `struct npcm_peci` stores regmap, completion, interrupt status, clock, timeout, controller pointer, and a spinlock. `npcm_peci_xfer()` is the core `.xfer` callback. `npcm_peci_irq_handler()` latches DONE/CRC/abort bits and completes pending transfers. `npcm_peci_init_ctrl()` enables the reference clock, parses `cmd-timeout-ms`, programs pull-down and host negotiation bit-rate defaults, waits for idle, and enables done interrupts. `npcm_peci_probe()` maps resources, creates the regmap, requests IRQ, initializes locks/completion, initializes hardware, and calls `devm_peci_controller_add()`.

Control flow: Probe maps the controller registers and initializes the block before registering the PECI controller. A PECI request enters through the bus core, waits for `START_BUSY` to clear, programs target address, read/write lengths, command byte, and payload bytes, then starts the transaction. The interrupt handler records error/done state, acknowledges interrupt bits, and completes the wait when DONE is seen. The transfer path then validates that the only final latched status is DONE, clears the command register, reads response bytes, and returns success or `-EIO`/`-ETIMEDOUT`.

State and persistence: Runtime state is in `priv->status`, `xfer_complete`, and NPCM PECI registers. The spinlock protects status/completion setup against IRQ-side updates. Hardware settings such as pull-down, bit rate, interrupt enable, and programmed request bytes persist in registers until reset or reprogramming. The devm controller lifetime follows the platform device.

Dependencies and integration points: Depends on Linux platform, OF, regmap MMIO, clock, IRQ, reset, completion, and PECI APIs. It imports the `PECI` namespace. Its `.xfer` is consumed by the PECI core in `device.c` and `request.c`; the core serializes transfers with `controller->bus_lock`, while this driver handles controller-local IRQ synchronization.

Risks: Register comments have some mislabeled offsets, so changes should follow macro values rather than comments. `NPCM_PECI_RD_LENGTH` is written with `NPCM_PECI_WR_LEN_MASK`, which is numerically equivalent but easy to misread. Any DONE combined with CRC/abort returns `-EIO`, so tests must cover mixed status. Timeout properties above 60000 ms or zero fall back to defaults. Transfer paths do not reset hardware after timeout, so later idle polling is the recovery signal.

Test signals: Probe on both compatible strings, valid clock and IRQ resources, sysfs PECI controller appearance, ping/device scan success, GetDIB/GetTemp requests, CRC/abort fault injection if available, command timeout behavior, and dynamic debug TX/RX dumps are the strongest validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/controller/peci-npcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/core.c -->
# sources/distributed-fs/ceph-client/drivers/peci/core.c

Purpose: Provides the PECI bus core: controller allocation/registration, controller removal cleanup, automatic device scanning, PECI bus matching/probe/remove callbacks, and module-level bus registration.

Important APIs and types: `devm_peci_controller_add()` is the exported controller registration API. `peci_controller_scan_devices()` probes PECI CPU addresses `0x30` through `0x37`. `peci_controller_alloc()` creates `struct peci_controller`, assigns an ID with `IDA`, initializes the embedded device, and sets up `bus_lock`. `peci_bus_type` supplies `.match`, `.probe`, `.remove`, and bus sysfs groups. `peci_controller_type` provides the release method.

Control flow: A hardware controller driver calls `devm_peci_controller_add()` late in probe. The core names the controller `peci-N`, enables runtime PM without callbacks, mirrors the firmware node, adds the device, registers a devm cleanup action, then scans all PECI CPU slots. Driver binding checks only PECI devices, matches `peci_device_id.x86_vfm`, and passes the matched ID to the PECI driver probe. Controller unregister walks children in reverse and destroys PECI devices before unregistering the controller device.

State and persistence: Persistent runtime state consists of the controller IDA allocation, controller device, child devices, firmware-node reference, runtime PM state, and `bus_lock`. The release path frees the ID and destroys the mutex. Scanning failures are intentionally non-fatal to controller registration because CPU availability can be transient.

Dependencies and integration points: Depends on Linux device core, bus core, IDA, firmware node/property, runtime PM, and the public PECI API. Integrates with `device.c` for PECI child creation/destruction, `sysfs.c` for bus attributes, and controller drivers such as `peci-npcm.c`.

Risks: `devm_peci_controller_add()` requires a non-null `.xfer`; controller drivers that register too early may expose a bus before hardware is usable. Device scan ignores per-address absence errors, so diagnostics require lower-level debug. The bus match assumes every PECI device has valid `info.x86_vfm`; broken detection in `device.c` prevents later driver binding.

Test signals: Build with `CONFIG_PECI`, bus registration at module load, controller add/remove, rescans, child cleanup on controller removal, module namespace exports, and successful binding of `peci-cpu` to detected Intel VFM IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/cpu.c -->
# sources/distributed-fs/ceph-client/drivers/peci/cpu.c

Purpose: Implements the PECI CPU client driver and exports convenience read APIs for CPU temperature, package config space, local PCI config, endpoint PCI config, and endpoint MMIO reads. It also creates auxiliary devices for CPU and DIMM temperature consumers once a supported Intel CPU is detected.

Important APIs and functions: Exported `PECI_CPU` APIs are `peci_temp_read()`, `peci_pcs_read()`, `peci_pci_local_read()`, `peci_ep_pci_local_read()`, and `peci_mmio_read()`. `struct peci_cpu` stores the backing PECI device and matched ID. `adev_alloc()`, `devm_adev_add()`, and `peci_cpu_add_adevices()` create `cputemp.<platform>` and `dimmtemp.<platform>` auxiliary devices. `peci_cpu_device_ids` maps Intel VFM IDs for Haswell through Emerald Rapids Xeon families to short platform strings.

Control flow: The PECI bus matches a detected CPU's `x86_vfm` against `peci_cpu_device_ids` and calls `peci_cpu_probe()`. Probe stores driver data and tries to add both auxiliary devices, warning but continuing if one fails. Read helper functions allocate and execute request helpers from `request.c`, check completion codes where applicable, copy typed data out of the response buffer, and free the request.

State and persistence: The driver stores only per-device driver data and devm-managed auxiliary devices. Auxiliary IDs combine controller ID and PECI address to keep child device identities stable per controller/address. Read APIs do not cache data; each call performs a PECI transaction and returns current target state.

Dependencies and integration points: Depends on `linux/peci.h`, `linux/peci-cpu.h`, the auxiliary bus, and request helpers from `internal.h`. The auxiliary devices are consumed by PECI hwmon-style drivers. It imports `PECI` and exports `PECI_CPU`.

Risks: Helper APIs return raw PECI/target errors, so clients must distinguish transport failure from completion-code failure. Auxiliary device names depend on `id->data`; new VFM entries must use names expected by child drivers. Probe does not fail if auxiliary creation fails, which keeps CPU binding alive but can hide missing sensors without checking warnings.

Test signals: Successful binding for each supported VFM, appearance of auxiliary devices, GetTemp reads, PCS/package config reads, endpoint reads on supported platforms, module autoload via PECI modalias, and negative tests for unsupported VFM IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/device.c -->
# sources/distributed-fs/ceph-client/drivers/peci/device.c

Purpose: Handles PECI target detection, `struct peci_device` creation/destruction, CPU identity discovery, and PECI client-driver registration wrappers.

Important APIs and functions: `peci_device_create()` validates an address, skips existing children, pings the target, allocates a PECI device, initializes CPU information, names the device, and adds it to the bus. `peci_device_destroy()` unregisters devices once despite concurrent sysfs/controller removal. `__peci_driver_register()` and `peci_driver_unregister()` export PECI client driver registration. Helpers include `peci_get_cpu_id()`, `peci_get_revision()`, `peci_device_info_init()`, and x86 signature decoding helpers.

Control flow: Controller scanning calls `peci_device_create()` for each valid slot. Detection uses a zero-length PECI ping under `controller->bus_lock`; `-EIO` and `-ETIMEDOUT` mean absent or temporarily unavailable and are ignored. For responding targets, the code reads CPU ID via RdPkgConfig and DIB revision via GetDIB, computes x86 vendor-family-model, stores PECI revision and socket ID, then exposes the child device.

State and persistence: Created devices persist as children of the controller until sysfs remove or controller removal. `device->deleted` is protected by a global mutex to avoid double unregister. Device info stores derived CPU VFM, PECI revision, and socket ID. There is no persistent scan cache beyond existing child devices.

Dependencies and integration points: Depends on PECI request helpers, Linux device core, bitfield helpers, `peci-cpu.h` constants, and the PECI bus type in `core.c`. `sysfs.c` uses `peci_device_destroy()`, and `cpu.c` consumes initialized `device->info`.

Risks: Detection requires both CPU ID and nonzero DIB; targets that ping but cannot answer these reads are not registered. Existing-device detection returns success when an address is already present, so rescans are idempotent but do not refresh CPU info. The global deletion mutex protects double-delete, not other device state.

Test signals: Address validation, duplicate rescan behavior, absent target handling, nonzero DIB requirement, device names like `0-30`, sysfs remove races with controller removal, and client-driver registration failures without probe/id table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/internal.h -->
# sources/distributed-fs/ceph-client/drivers/peci/internal.h

Purpose: Defines the internal PECI core contract shared by bus, device, sysfs, CPU, and request implementation files. It declares request allocation/transfer helpers, data accessors, bus/device types, driver registration helpers, and controller scan/create/destroy functions.

Important APIs and types: Constants `PECI_BASE_ADDR` and `PECI_DEVICE_NUM_MAX` define the CPU address window. `struct peci_device_id` matches devices by x86 VFM and carries driver data. `struct peci_driver` wraps a Linux `device_driver` with PECI `probe`, optional `remove`, and `id_table`. Macros `peci_driver_register()` and `module_peci_driver()` provide registration boilerplate. Numerous `peci_xfer_*` declarations expose typed PECI command builders.

Control flow: The header itself has no runtime flow, but it defines how requests move from higher-level clients to `request.c`, how drivers bind through `core.c`, and how devices are created/destroyed by scanning and sysfs.

State and persistence: No storage is defined here. The declarations expose stateful objects owned elsewhere: PECI request buffers, controller/device embedded `struct device` objects, bus attribute groups, and device attribute groups.

Dependencies and integration points: Includes Linux device/types headers and is included by all local PECI implementation files. It bridges private implementation details with exported namespace functions in `request.c`, `device.c`, and `core.c`.

Risks: Because this is the private ABI between PECI compilation units, signature drift breaks builds across multiple files. Buffer-size assumptions live in the public request structure while allocation validation is in `request.c`; new commands must keep these declarations and implementation macros aligned.

Test signals: Full PECI subsystem build, namespace export resolution, module_peci_driver users compiling, and command helper consumers linking against all declared functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/request.c -->
# sources/distributed-fs/ceph-client/drivers/peci/request.c

Purpose: Builds, executes, retries, interprets, and frees PECI protocol requests. It contains command encodings for GetDIB, GetTemp, RdPkgConfig, RdPCIConfigLocal, RdEndpointConfig PCI, and RdEndpointConfig MMIO reads, plus typed response accessors.

Important APIs and functions: `peci_request_alloc()`/`peci_request_free()` manage fixed-buffer requests. `peci_request_status()` maps PECI completion codes to Linux errors. `peci_request_xfer()` serializes through `controller->bus_lock`; `peci_request_xfer_retry()` handles retryable completion codes with exponential sleep and retry-bit setting. Exported `peci_xfer_*` helpers construct and execute protocol-specific reads. Data accessors include `peci_request_data_readb/w/l/q()`, `peci_request_dib_read()`, and `peci_request_temp_read()`.

Control flow: A helper allocates a request with exact TX/RX lengths, writes command bytes and little-endian parameters, performs transfer directly or through retry logic, and returns either an ERR_PTR or a request containing RX data. Retryable completion codes `0x80` through `0x82` cause the retry bit in `tx.buf[1]` to be set, then the request sleeps with a backoff up to 128 ms until a 700 ms overall timeout.

State and persistence: Request state is heap allocated and caller-owned until `peci_request_free()`. `prev_count`-style persistence does not exist; only command buffers and response buffers persist per request. The retry path mutates the TX retry bit in place across attempts. Bus serialization is delegated to the controller mutex.

Dependencies and integration points: Depends on Linux PCI address helpers, unaligned little-endian accessors, PECI public structs, and the controller `.xfer` operation. CPU helper code in `cpu.c` and device detection in `device.c` consume these functions.

Risks: `peci_request_status()` must not be used for commands without completion-code byte, and the code documents that GetDIB/GetTemp/Ping are excluded. New request helpers must account for the first RX byte being completion code for most reads, so data accessors start at `rx.buf[1]`. Retry returns success when the transport succeeds and the final status is not retry, leaving callers to call `peci_request_status()` for non-retry protocol errors.

Test signals: Unit-like command encoding checks, completion-code mapping, retry on `NEED_RETRY`/resource codes, interruptible sleep interruption, bounds warnings for oversized buffers, endian correctness for PCI/MMIO addresses, and successful reads through the exported CPU APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/peci/sysfs.c

Purpose: Provides PECI bus and device sysfs controls: bus-wide rescan and per-device remove.

Important APIs and functions: `rescan_store()` parses a boolean and triggers `peci_controller_scan_devices()` on every PECI controller device on the bus. `remove_store()` parses a boolean, uses `device_remove_file_self()` for safe self-removal, and calls `peci_device_destroy()`. `peci_bus_groups` and `peci_device_groups` export the attribute groups used by `peci_bus_type` and `peci_device_type`.

Control flow: Writing true to the bus `rescan` attribute walks bus devices, filters controller devices by `peci_controller_type`, and rescans each controller. Writing true to a PECI device's `remove` attribute removes the sysfs file from within the write path and unregisters the device.

State and persistence: The file itself has no long-lived mutable state. Rescan can create new device children; remove transitions a child toward unregister and sets `device->deleted` in `device.c`.

Dependencies and integration points: Depends on Linux sysfs/device helpers and PECI internal bus/device types. It is wired into `core.c` and `device.c` via exported attribute-group arrays.

Risks: Rescan is best-effort and stops on the first nonzero scan error from a controller. Remove relies on `peci_device_destroy()` for double-delete protection. Boolean false writes are accepted as no-ops, which may be surprising but matches common sysfs patterns.

Test signals: Presence and permissions of `/sys/bus/peci/rescan` and device `remove`, true/false parsing, rescan creating newly available devices, repeated remove/controller-unplug races, and lockdep behavior around `DEVICE_ATTR_IGNORE_LOCKDEP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/peci/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/perf/Kconfig

Purpose: Defines kernel configuration options for platform and uncore performance monitor drivers under the `PERF_EVENTS` menu.

Important APIs and entries: Entries in this subset include `ARM_CCI_PMU`, `ARM_CCI400_PMU`, `ARM_CCI5xx_PMU`, `ARM_CCN`, `APPLE_M1_CPU_PMU`, `ALIBABA_UNCORE_DRW_PMU`, and inclusion of `drivers/perf/amlogic/Kconfig` for `MESON_DDR_PMU`. The file also configures many adjacent PMU drivers such as CMN, NI, ARM PMU, RISC-V PMU, SMMUv3 PMCG, SPE, DMC620, CXL, Marvell, Nvidia, and Hisilicon PMUs.

Control flow: Kconfig dependency resolution determines which objects the Makefile can build. `ARM_CCI_PMU` selects common CCI support and gates model-specific booleans. `APPLE_M1_CPU_PMU` depends on `ARM_PMU && ARCH_APPLE`. `ALIBABA_UNCORE_DRW_PMU` depends on ARM64 ACPI or COMPILE_TEST. The Amlogic PMU is sourced from its subdirectory.

State and persistence: Kconfig selections persist in `.config` and determine build products and module availability. Help text documents module names and hardware scope.

Dependencies and integration points: Integrated by the kernel Kconfig tree and paired with `drivers/perf/Makefile`. Architecture, ACPI, PCI, CXL, MSI, NUMA, and COMPILE_TEST dependencies prevent unsupported builds or expose compile coverage.

Risks: Incorrect dependencies can either hide usable drivers or allow build/runtime breakage on unsupported architectures. Model sub-options under CCI affect compiled event tables and validation paths. Source ordering matters for subdirectory Kconfigs.

Test signals: `olddefconfig`, `menuconfig` visibility, randconfig/COMPILE_TEST coverage, module names matching help text, and object inclusion matching Makefile entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/perf/Makefile

Purpose: Maps performance monitor Kconfig symbols to built objects and subdirectories.

Important APIs and entries: Relevant entries include `obj-$(CONFIG_ARM_CCI_PMU) += arm-cci.o`, `obj-$(CONFIG_ARM_CCN) += arm-ccn.o`, `obj-$(CONFIG_APPLE_M1_CPU_PMU) += apple_m1_cpu_pmu.o`, `obj-$(CONFIG_ALIBABA_UNCORE_DRW_PMU) += alibaba_uncore_drw_pmu.o`, and `obj-$(CONFIG_MESON_DDR_PMU) += amlogic/`. It also routes Hisilicon and Arm CSPMU subdirectories and many other platform PMU objects.

Control flow: Kbuild evaluates `obj-y`/`obj-m` from configuration symbols and descends into subdirectories when enabled. Single-file drivers build directly; Amlogic builds through its own Makefile.

State and persistence: No runtime state. The file determines build graph state and module linkage.

Dependencies and integration points: Paired with `drivers/perf/Kconfig` and per-subdirectory Makefiles. Object names must match source filenames and module expectations.

Risks: Mismatched Kconfig symbol/object names silently omit drivers or break builds. Subdirectory entries depend on subdir Makefiles defining composite objects correctly.

Test signals: `make drivers/perf/`, all relevant `CONFIG_*` combinations as built-in and module, and module file names matching expected aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/alibaba_uncore_drw_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/alibaba_uncore_drw_pmu.c

Purpose: Implements the Alibaba T-Head Yitian 710 DDR Sub-System Driveway uncore PMU. It exposes DDR subsystem events through perf, handles shared overflow IRQs, migrates PMU contexts on CPU hotplug, and binds ACPI IDs `BABA5000` and historical `ARMHD700`.

Important APIs and functions: `struct ali_drw_pmu` stores MMIO base, PMU, CPU affinity, event/counter arrays, used counter bitmap, and associated shared IRQ. `struct ali_drw_pmu_irq` tracks an IRQ shared by one or more PMU instances with refcount, CPU affinity, and RCU PMU list. Perf callbacks include `ali_drw_pmu_event_init()`, `add`, `del`, `start`, `stop`, and `read`. `ali_drw_pmu_isr()` handles common counter overflow status. Sysfs exposes event aliases, `format/event`, `cpumask`, and identifier.

Control flow: Probe maps MMIO, names the PMU from resource address, resets counters, enables common-counter overflow interrupts, clears status, initializes or reuses a shared IRQ object, then registers the PMU. Event init rejects sampling, task events, CPU-less events, and groups with more than one hardware event. Add allocates one of 16 common counters for non-cycle events; cycle events use a special 64-bit counter path. Start programs preload, event select, counter enable, and global start. IRQ handling disables active counters, reads overflow status, updates/reloads overflowed events, clears status, and re-enables non-stopped counters.

State and persistence: Hardware registers hold counter control, event select, preload, common counters, cycle counters, and overflow interrupt state. Software tracks used counters and event IDs per PMU. Shared IRQ objects persist while any PMU references them. CPU affinity is stored per IRQ and PMU and changes during hotplug migration.

Dependencies and integration points: Depends on ACPI platform probing, perf uncore PMU APIs, cpuhotplug multi-state, IRQ affinity hints, RCU lists, refcounts, and MMIO accessors. Integrates with `drivers/perf/Kconfig` and `Makefile` through `CONFIG_ALIBABA_UNCORE_DRW_PMU`.

Risks: The driver intentionally uses `IRQF_SHARED` due to an MPAM interrupt overlap, but notes that the PMU interrupt should not be shared. Cycle event handling uses `hw.idx = -1`, so code paths must avoid common-counter indexing for cycle events. Event init resets all PMU counters, which can disturb concurrent sessions if perf allowed them, hence the single-hardware-event group restriction is important. IRQ cleanup must respect RCU grace periods; list removal is RCU-style but object free relies on no concurrent handler after IRQ teardown/refcounting.

Test signals: ACPI probe for both IDs, event alias visibility, single event counting, cycle event counting, overflow interrupt updates, shared IRQ with multiple PMU instances, hotplug migration and affinity hint changes, rejection of sampling/task/grouped events, and remove disabling interrupts before unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/alibaba_uncore_drw_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/perf/amlogic/Kconfig

Purpose: Defines the Amlogic DDR bandwidth performance monitor config option.

Important APIs and entries: `MESON_DDR_PMU` is a tristate option titled "Amlogic DDR Bandwidth Performance Monitor" and depends on `ARCH_MESON || COMPILE_TEST`.

Control flow: When enabled, the parent Makefile descends into `drivers/perf/amlogic/` and builds the Meson DDR PMU composite object.

State and persistence: The option persists in kernel `.config` and controls module/built-in availability.

Dependencies and integration points: Sourced by `drivers/perf/Kconfig`; paired with `drivers/perf/amlogic/Makefile` and the G12 platform driver.

Risks: Too broad dependencies could build code without required SoC headers; too narrow dependencies reduce compile-test coverage. Help text promises multiple-channel bandwidth monitoring and should stay aligned with supported hardware data.

Test signals: Menu visibility under Meson and COMPILE_TEST, built-in/module builds, and object inclusion through the parent Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/perf/amlogic/Makefile

Purpose: Builds the Amlogic Meson DDR PMU driver as a composite object.

Important APIs and entries: `obj-$(CONFIG_MESON_DDR_PMU) += meson_ddr_pmu_g12.o` and `meson_ddr_pmu_g12-y := meson_ddr_pmu_core.o meson_g12_ddr_pmu.o`.

Control flow: Kbuild links the generic core and G12 hardware implementation into one module/object when `MESON_DDR_PMU` is enabled.

State and persistence: No runtime state; it defines build composition.

Dependencies and integration points: Requires exported non-static functions in `meson_ddr_pmu_core.c` to be visible to `meson_g12_ddr_pmu.c` within the composite object.

Risks: Adding a new SoC implementation requires updating the composite object or adding a new target; otherwise OF compatibles may exist without linked hardware callbacks.

Test signals: Module build, `meson_ddr_pmu_g12.ko` composition, and modpost resolving `meson_ddr_pmu_create()`/`remove()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_ddr_pmu_core.c -->
# sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_ddr_pmu_core.c

Purpose: Provides the generic perf PMU layer for Amlogic DDR bandwidth counters. Hardware-specific callbacks supply enable/disable, IRQ handling, counter reads, AXI filter programming, channel count, capabilities, and format attributes.

Important APIs and functions: `struct ddr_pmu` wraps `struct pmu`, `struct dmc_info`, accumulated counters, CPU hotplug state, and device metadata. Exported-in-object functions are `meson_ddr_pmu_create()` and `meson_ddr_pmu_remove()`. Perf callbacks include `meson_ddr_perf_event_init()`, `add`, `start`, `stop`, `del`, and `update`. `dmc_irq_handler()` accumulates one-shot hardware counter snapshots. Sysfs exposes bandwidth events with `.unit` and `.scale`, format attributes filtered by hardware capability, `cpumask`, and identifier.

Control flow: Platform-specific probe calls `meson_ddr_pmu_create()`, which allocates the PMU, parses DT resources and IRQ, installs hardware format attributes, creates a CPU hotplug state, fills event aliases according to channel count, and registers perf. Event init rejects sampling/task events and requires a CPU. Event add programs AXI filters from `config1` and `config2` bitmaps, with at most four ports per channel event. Start clears accumulated counters and enables hardware. IRQ handler asks hardware to acknowledge/fill counters, adds them to software totals, and re-enables one-shot timer mode if still enabled. Stop optionally updates from current hardware counters and disables hardware.

State and persistence: Software accumulation in `pmu->counters` preserves counts across periodic hardware timer interrupts during a perf session. Hardware filter and timer/counter state is reset by the hardware-specific disable callback. CPU affinity is stored in `pmu->cpu` and migrated on hotplug with IRQ affinity update.

Dependencies and integration points: Depends on perf event core, platform/OF resource parsing, IRQs, cpuhotplug, sysfs, and `soc/amlogic/meson_ddr_pmu.h`. The G12 implementation supplies `struct dmc_hw_info` through OF match data.

Risks: `ddr_perf_events_attrs` and `ddr_perf_format_attr_group.attrs` are file-global, so multiple hardware instances with different capabilities/channel counts could race or overwrite sysfs layout. `meson_ddr_perf_format_attr_visible()` calls a show method into a fixed 20-byte stack buffer, which depends on current format strings remaining short. Filter programming does not clear previous filters on add except via hardware disable paths, so session sequencing matters.

Test signals: OF probe with all required MMIO resources plus PLL resource, IRQ accumulation, total and per-channel events, AXI filter masks across `config1`/`config2`, capability-based format visibility, CPU hotplug migration, and scale/unit correctness for MB conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_ddr_pmu_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_g12_ddr_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_g12_ddr_pmu.c

Purpose: Implements the Amlogic G12A/G12B/SM1 DDR monitor hardware callbacks and platform driver glue for the generic Meson DDR PMU core.

Important APIs and functions: `dmc_g12_counter_enable()` programs a 100 ms timer from DDR PLL frequency and enables all four channels. `dmc_g12_counter_disable()` clears control, timer, counters, and port filters. `dmc_g12_set_axi_filter()`/`dmc_g12_config_fiter()` program major/subport filter registers per channel. `dmc_g12_get_counters()` reads total request/grant and per-channel grant counts. `dmc_g12_irq_handler()` detects and clears QOS timer IRQ. `g12a_dmc_info`, `g12b_dmc_info`, and `sm1_dmc_info` define capabilities and callbacks.

Control flow: OF matching selects a hardware-info structure, and probe delegates to `meson_ddr_pmu_create()`. During perf start, the core invokes `enable`; the G12 code calculates timer ticks from PLL registers, writes the timer, and sets enable/use-timer/channel bits. AXI filters are set before start based on perf event config bitmaps. On interrupt, the core invokes `irq_handler`, which reads counters if `DMC_QOS_IRQ` is set and writes back the control value to clear flags.

State and persistence: Hardware state lives in DMC monitor control registers, filter registers, timer, and counter registers. Capability bitmasks differ by SoC and control visible format attributes. The PLL register is read on each enable for current DDR frequency.

Dependencies and integration points: Depends on the generic Meson DDR PMU core and `soc/amlogic/meson_ddr_pmu.h`. Platform matching supports `amlogic,g12a-ddr-pmu`, `amlogic,g12b-ddr-pmu`, and `amlogic,sm1-ddr-pmu`.

Risks: Function name `dmc_g12_config_fiter` is misspelled but internal. `dmc_g12_set_axi_filter()` checks `channel > chann_nr`; an equal channel would pass, though current callers derive valid zero-based channels. Timer calculation depends on PLL encoding and defaults; bad PLL values can produce zero/invalid periods. Filter register programming treats ports >=32 as subports behind the device selector, so capability masks must match SoC wiring.

Test signals: Probe each compatible, sysfs format visibility differences for G12A/G12B/SM1, DDR bandwidth events over timer interrupts, PLL-derived timer sanity, per-channel filters for major and subport IDs, and clearing/re-enabling after stop/start cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_g12_ddr_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/apple_m1_cpu_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/apple_m1_cpu_pmu.c

Purpose: Provides an ARM PMU backend for Apple M1/M2 CPU PMUs, whose counters and events are non-architectural implementation registers rather than standard PMUv3 counters.

Important APIs and functions: `m1_pmu_init()` fills an `arm_pmu` with backend callbacks. Low-level helpers read/write counters `PMC0..PMC9`, enable counters and interrupts through Apple PMCR registers, configure EL0/EL1 host/guest filters, and program event selectors in PMESR0/PMESR1. `m1_pmu_handle_irq()` handles overflows. `m1_pmu_get_event_idx()` enforces event-to-counter affinity from `m1_pmu_event_affinity`. OF init callbacks name Icestorm, Firestorm, Avalanche, and Blizzard PMUs.

Control flow: Platform probe calls `arm_pmu_device_probe()` with Apple compatible data. The selected init callback sets PMU name and counter width mode: M1 cores use advertised 47-bit overflow behavior, M2 cores 63-bit. Event mapping translates generic perf hardware events and selected PMUv3 common events to Apple event IDs. When an event starts, the driver configures filters/event select, enables the counter and PMI, and relies on the shared ARM PMU framework for period management. IRQ handling reads Apple PMSR overflow state, stops the PMU, updates each active event, resets periods, calls perf overflow handling, and restarts.

State and persistence: Counter values, enable bits, interrupt bits, filter bits, event selectors, PMU mode, and overflow state live in Apple system registers per CPU. Software stores event mappings, counter masks, and per-CPU `arm_pmu` state in the ARM PMU framework. No data is persistent across CPU reset.

Dependencies and integration points: Depends on `linux/perf/arm_pmu.h`, `arm_pmuv3.h`, Apple implementation sysreg definitions, IRQ register helpers, and OF platform probing. It integrates with generic ARM PMU event allocation, filtering, reset, and perf sysfs groups.

Risks: The event table is partly experimental and has strict counter affinity; wrong affinity causes unavailable or incorrect counts. Counters 0 and 1 are fixed cycles/instructions, while programmable counters start at 2. Guest filtering is only supported when kernel runs in hyp mode; otherwise non-excluded guest events are rejected. Spurious interrupt handling clears `PMCR0_IACT`; changes must preserve that path.

Test signals: OF probe on each compatible, sysfs events/format, generic cycles/instructions/branch events, PMUv3 event mapping bitmap, counter allocation under constrained events, overflow interrupts, exclude_user/exclude_kernel/exclude_host/exclude_guest combinations, reset on CPU bring-up, and M1 versus M2 counter-width behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/apple_m1_cpu_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-cci.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm-cci.c

Purpose: Implements perf support for ARM CCI-400, CCI-500, and CCI-550 Cache Coherent Interconnect PMUs. It handles model-specific event validation, counter allocation, overflow IRQs, CPU hotplug migration, and perf sysfs event/format exposure.

Important APIs and types: `struct cci_pmu_model` captures model name, fixed/program counters, counter stride, attributes, event ranges, validation, allocation, and special write-counter hooks. `struct cci_pmu` stores MMIO bases, PMU, selected CPU, IRQs, model, event arrays, active event count, and reserve mutex. Key callbacks are `cci_pmu_event_init()`, `add`, `del`, `start`, `stop`, `read`, `pmu_enable`, and `pmu_disable`. Model-specific functions include `cci400_validate_hw_event()`, `cci400_get_event_idx()`, `cci500_validate_hw_event()`, `cci550_validate_hw_event()`, and `cci5xx_pmu_write_counters()`.

Control flow: Probe allocates model state from OF match data or probes old CCI-400 compatible data via secure CCI access, maps PMU registers, collects one IRQ per hardware counter while de-duplicating shared IRQs, sets up hotplug state, and registers perf. Event init maps and validates `attr.config`, rejects sampling/task events, pins the event to the PMU CPU, and reserves IRQ hardware on the first active event. Start programs event select for programmable counters, sets a half-range period, marks counters for sync, and enables the counter. Global PMU enable synchronizes marked counters before setting `CCI_PMCR_CEN`. IRQ handling disables the PMU, scans counters for overflow flags, clears flags, updates events, resets periods, and re-enables with sync.

State and persistence: Hardware state includes PMCR enable, per-counter event select, count, control, and overflow registers. Software tracks used counters, event pointers, active IRQ bits, active event count, and selected CPU. CCI-400 has a fixed cycle counter at index 0; CCI-5xx has no fixed counter and needs a special counter-write sequence because power-saving clock gating can ignore writes unless counters and global profiling are enabled in a precise order.

Dependencies and integration points: Depends on Linux perf, platform/OF, IRQ, spinlock, `linux/arm-cci.h`, and CPU hotplug. Kconfig model options compile in event tables and compatible strings. It uses platform data for the CCI control base and platform access helpers for legacy CCI-400 probing.

Risks: The driver has a single global `g_cci_pmu`, so it is structured for one CCI PMU instance. IRQ count must match hardware counters even when lines are shared; bad DT interrupt lists fail probe. Event encodings differ by CCI-400 revision and CCI-500 versus CCI-550 master ports. CCI-5xx counter writes are order-sensitive due to gated clocks. Group validation uses a fake used mask and must mirror real allocation semantics.

Test signals: Probe on CCI-400 r0/r1 and CCI-500/550 compatibles, sysfs event format correctness, cycles and interface events, overflow IRQs on shared and per-counter lines, first-event IRQ reservation and last-event release, CPU hotplug context migration, unsupported event rejection, and secure-access fallback for deprecated CCI-400 compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-cci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-ccn.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm-ccn.c

Purpose: Implements perf support for ARM CCN-502/504/512 Cache Coherent Network PMUs. It discovers CCN topology, exposes node/XP/watchpoint events, programs the Debug/Test subsystem counters, handles overflow via IRQ or polling timer, and migrates the uncore PMU context on CPU hotplug.

Important APIs and types: `struct arm_ccn` stores base MMIO, IRQ, topology arrays, feature flags, and the DT PMU. `struct arm_ccn_dt` stores DT base, config lock, counter allocations, compare masks, timer, CPU, and `struct pmu`. `struct arm_ccn_component` represents nodes and XPs with event/watchpoint allocation bitmaps. Perf callbacks include `arm_ccn_pmu_event_init()`, `add`, `del`, `start`, `stop`, `read`, `pmu_enable`, and `pmu_disable`. Configuration helpers program XP watchpoints, XP PMU events, node PMU events, DT active DSM routing, and compare masks.

Control flow: Module init registers a CPU hotplug multi-state, populates event sysfs attribute pointers, and registers the platform driver. Probe maps CCN registers, tests whether PMU interrupt acknowledgement is writable, requests the IRQ when usable, walks the component-list bitmap once to count nodes/XPs and again to initialize component bases/types, then initializes DT PMU registers and registers perf. Event init validates topology, type, event ID, port, VC, grouping, and CPU affinity. Watchpoint-like MN/HN-I/SBSX events are translated to XP watchpoints. Add allocates a DT counter plus a source event slot or XP watchpoint, starts the polling timer if no IRQ, programs routing and event registers, and optionally starts counting.

State and persistence: Hardware state includes DT enable/PMCR/overflow registers, active DSM mapping, XP DT config/control, compare values/masks, interface selection, and node event selector registers. Software state includes topology arrays, per-source allocation bitmaps, counter-to-event mappings, writable and predefined compare masks, selected CPU, hrtimer, and IDA-provided PMU names.

Dependencies and integration points: Depends on Linux perf, platform/OF, MMIO, IRQ, hrtimer, IDA, cpuhotplug, and sysfs. It integrates through compatibles `arm,ccn-502`, `arm,ccn-504`, and `arm,ccn-512`; the PMU appears as `ccn` or `ccn_N`.

Risks: The driver mutates `event->attr.config` when translating node watchpoints to XP watchpoints, so later code assumes the rewritten encoding. No-IRQ mode relies on a polling hrtimer; poll-period tuning affects overhead and overflow latency. Topology discovery trusts component-list and ID fields; malformed hardware/DT can cause sparse arrays and invalid node IDs. Compare-mask sysfs attributes are writable for masks 0-7 and global to the PMU, so changing them affects future watchpoint events.

Test signals: Probe topology logs, sysfs events/format/cmp_mask/cpumask, IRQ path and timer fallback path, cycle counter and 32-bit event counters, XP watchpoint events with compare masks, HNF/RNI/SBAS/SBSX event visibility, overflow update behavior, CPU hotplug migration with IRQ affinity, and invalid topology/event/group rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-ccn.c -->
