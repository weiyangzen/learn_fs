# subset-b-001027 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_core.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/processor_core.c

### Purpose
`processor_core.c` maps ACPI processor namespace identifiers to kernel CPU identifiers and physical CPU IDs by reading `_MAT` objects and MADT subtables. It also provides optional IOAPIC hotplug lookup support when `CONFIG_ACPI_HOTPLUG_IOAPIC` is enabled.

### Important APIs, Types, And Functions
The central exported APIs are `acpi_get_phys_id()`, `acpi_map_cpuid()`, and `acpi_get_cpuid()`. Early boot helpers include `acpi_map_madt_entry()` and `acpi_get_madt_revision()`. Static mapper functions decode architecture-specific MADT records: local APIC, x2APIC, SAPIC, ARM GICC MPIDR, RISC-V RINTC hart ID, and LoongArch CORE_PIC. `get_madt_table()` caches a runtime MADT mapping.

### Control Flow
CPU mapping first evaluates a processor object's `_MAT`; if it yields a recognized local interrupt-controller subtable, the file extracts the hardware ID from that subtable. If `_MAT` is absent or invalid, it scans the cached MADT. The resulting physical ID is translated to a Linux CPU by matching `cpu_physical_id()` over possible CPUs, with a uniprocessor fallback that accepts only ACPI ID 0 when no physical ID is available. IOAPIC lookup follows the same `_MAT` then MADT fallback for a matching GSI base.

### State, Persistence, And Dependencies
The only retained state is the static cached MADT pointer and read flag. The file depends on ACPICA table APIs, ACPI object evaluation, per-CPU physical-ID helpers, architecture MADT type definitions, and optional IOAPIC hotplug support.

### Integration Points
Processor enumeration, CPU hotplug, architecture setup, and ACPI processor drivers use these helpers to connect namespace `Processor` or processor device objects to kernel CPU numbers. IOAPIC hotplug uses `acpi_get_ioapic_id()` to recover APIC IDs and physical addresses from firmware data.

### Risks
Firmware may provide disabled, malformed, or inconsistent `_MAT` and MADT entries. Runtime MADT caching omits `acpi_put_table()` for the cached pointer, so lifetime assumptions follow ACPI core table mapping behavior. Table scans advance by firmware-provided record lengths and rely on ACPICA table validation. The UP fallback deliberately ignores nonzero ACPI IDs.

### Test Signals
Useful checks include systems with only MADT data, only `_MAT`, disabled processor entries, x2APIC UIDs above and below 255, RISC-V/ARM/LoongArch mappings, UP kernels without SMP tables, and IOAPIC hotplug records with matching and missing GSI bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_driver.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/processor_driver.c

### Purpose
`processor_driver.c` is the ACPI processor driver module entry point. It registers the CPU-subsystem driver, wires ACPI processor notifications into cpufreq, cpuidle, throttling, and thermal subsystems, and manages CPU hotplug callbacks.

### Important APIs, Types, And Functions
The file defines `acpi_processor_driver`, `processor_device_ids`, `acpi_processor_notify()`, `__acpi_processor_start()`, `acpi_processor_stop()`, `acpi_soft_cpu_online()`, `acpi_soft_cpu_dead()`, and module init/exit routines. It exports the global state `acpi_processor_cpufreq_init` and weak `acpi_processor_init_invariance_cppc()`.

### Control Flow
Module init registers a cpufreq policy notifier, registers the ACPI idle driver, registers the CPU bus driver, installs CPU hotplug states, initializes throttling coordination, initializes CPPC frequency invariance, and rescans dead SMT siblings. Starting a processor probes CPPC, initializes idle power handling, initializes P-state/throttling data when `_PSS` support is configured, registers a thermal cooling device, and installs an ACPI notify handler. Notifications dispatch `_PPC`, C-state, T-state, and highest-performance-change events to the relevant subsystem and generate netlink events. Stop/remove unwinds notify, idle, CPPC, and thermal state.

### State, Persistence, And Dependencies
State is per-processor in `struct acpi_processor`, per-CPU `processors`, cpuhp state IDs, registered notifier blocks, and the `previously_online` and `acpi_processor_cpufreq_init` flags. Dependencies include CPU hotplug, cpufreq, cpuidle, ACPI scan/device APIs, CPPC, thermal cooling, and the ACPI processor internal interfaces.

### Integration Points
This file is the coordinator for `processor_idle.c`, `processor_perflib.c`, `processor_throttling.c`, and `processor_thermal.c`. It also provides ACPI event delivery to userspace through `acpi_bus_generate_netlink_event()`.

### Risks
Initialization ordering matters: thermal setup is unwound through power exit, cpufreq notifier registration controls whether `_PPC` is honored, and first physical hotplug differs from later soft online events. Notify handlers must tolerate stale or missing driver data. Exit removes dynamic cpuhp state and notifier state but only when ACPI is enabled.

### Test Signals
Test CPU online/offline cycles, first hotplug of a previously unseen CPU, module load with ACPI disabled, ACPI notifications `0x80`, `0x81`, `0x82`, and `0x85`, cpufreq policy create/remove, and failure paths in thermal registration or notify-handler installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_idle.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/processor_idle.c

### Purpose
`processor_idle.c` implements the ACPI-backed cpuidle driver. It discovers legacy C-states from `_CST` or FADT/P_BLK, discovers low-power idle states from `_LPI`, validates platform constraints, and registers per-CPU cpuidle devices.

### Important APIs, Types, And Functions
Public integration functions include `acpi_processor_register_idle_driver()`, `acpi_processor_unregister_idle_driver()`, `acpi_processor_power_init()`, `acpi_processor_power_exit()`, `acpi_processor_hotplug()`, `acpi_processor_power_state_has_changed()`, and `acpi_idle_rescan_dead_smt_siblings()`. Important internals include C-state discovery and verification helpers, `acpi_idle_enter()`, `acpi_idle_enter_bm()`, `acpi_idle_enter_s2idle()`, `_LPI` parsing via `acpi_processor_evaluate_lpi()`, and LPI flattening via `flatten_lpi_states()`.

### Control Flow
Driver registration clamps `max_cstate`, claims CST control, finds one processor with valid idle data, builds global cpuidle state descriptors, and registers `acpi_idle_driver`. Per-CPU power initialization rediscoveries power data, allocates a `cpuidle_device`, fills per-CPU state pointers, and registers the device. Legacy C-state discovery prefers `_CST`, falls back to FADT, adds mandatory C1, verifies C2/C3 address and latency, applies DMI quirks, sets APIC timer broadcast and TSC stability flags, and handles bus-mastering rules for C3. LPI discovery validates architecture FFH support and `_OSC` LPI support, evaluates `_LPI` at the CPU and processor-container parents, flattens hierarchical local/parent states, and registers FFH enter callbacks.

### State, Persistence, And Dependencies
State includes module parameters `max_cstate`, `nocst`, `bm_check_disable`, and `latency_factor`, per-CPU `acpi_cpuidle_device`, per-CPU C-state pointers, `acpi_idle_driver`, static bus-mastering flags, and per-processor power flags. Dependencies span cpuidle, CPU hotplug, DMI, tick broadcast, context tracking, perf low-power callbacks, ACPI `_CST`/`_LPI`, FADT, architecture FFH hooks, and x86 APIC/TSC behavior.

### Integration Points
`processor_driver.c` calls the registration and per-CPU init/exit hooks. Architecture files may override weak LPI probe and enter hooks. Thermal, hotplug, and ACPI power notifications trigger reinitialization or device enablement.

### Risks
Idle entry runs in low-level CPU contexts, so interrupt, RCU, context-tracking, and bus-mastering sequencing are sensitive. Firmware latency ordering bugs are worked around by sorting only latencies, not whole state entries. `_LPI` hierarchy flattening limits to `ACPI_PROCESSOR_MAX_POWER`. Reinitialization unregisters all cpuidle devices when CPU0 receives a power notification, which depends on CPU hotplug locking.

### Test Signals
Exercise `_CST`, FADT-only, `_LPI`, disabled `nocst`, boot idle override, C3 with and without BM control, APIC timer-stop systems, suspend-to-idle entry, CPU hotplug, ACPI C-state notification, malformed `_LPI` packages, and platforms with too many LPI combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_pdc.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/processor_pdc.c

### Purpose
`processor_pdc.c` performs the ACPI `_PDC` processor-driver-capabilities handshake so firmware can expose modern processor power and performance features.

### Important APIs, Types, And Functions
The main public functions are `acpi_processor_set_pdc()` and early boot `acpi_early_processor_set_pdc()`. Internals are `acpi_set_pdc_bits()`, `acpi_processor_alloc_pdc()`, `acpi_processor_eval_pdc()`, and the namespace walker callback `early_init_pdc()`.

### Control Flow
The early init path runs `acpi_proc_quirk_mwait_check()`, walks legacy `Processor` objects and processor device HID objects, skips objects not physically present, allocates a one-element ACPI object list containing a 12-byte buffer, sets revision/count/capability bits, lets the architecture fill capability bits, evaluates `_PDC`, and frees all temporary allocations.

### State, Persistence, And Dependencies
There is no retained state in this file. The persistent effect is firmware state changed by `_PDC`. Dependencies are ACPI namespace walks, object evaluation, processor presence checks, and architecture hooks `arch_has_acpi_pdc()` and `arch_acpi_set_proc_cap_bits()`.

### Integration Points
The handshake happens early enough to affect later processor `_CST`, `_PSS`, `_PCT`, CPPC, and idle/performance feature exposure. It is shared by all architectures that implement the arch capability hooks.

### Risks
Allocation failure silently skips the handshake after logging. `_PDC` failure falls back to legacy performance control. Incorrect architecture capability bits can cause firmware to expose unsupported paths or hide needed ones. The early walker covers both processor object models and must avoid absent hotplug targets.

### Test Signals
Check systems with and without `_PDC`, architecture hook disabled, allocation-failure injection, physically absent processor namespace objects, duplicate Processor/HID coverage, and firmware behavior changes in subsequent C/P-state methods after `_PDC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_pdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_perflib.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/processor_perflib.c

### Purpose
`processor_perflib.c` implements ACPI processor performance-state support for x86. It parses `_PCT`, `_PSS`, `_PPC`, and `_PSD`, coordinates shared P-state domains, and exposes registration hooks used by cpufreq drivers.

### Important APIs, Types, And Functions
Exports include `acpi_processor_get_performance_info()`, `acpi_processor_get_bios_limit()`, `acpi_processor_notify_smm()`, `acpi_processor_get_psd()`, `acpi_processor_preregister_performance()`, `acpi_processor_register_performance()`, and `acpi_processor_unregister_performance()`. `_PPC` integration is handled by `acpi_processor_ppc_init()`, `acpi_processor_ppc_exit()`, and `acpi_processor_ppc_has_changed()`.

### Control Flow
Cpufreq policy creation adds per-processor max-frequency QoS requests and evaluates `_PPC` if enabled. Performance registration assigns a caller-provided `struct acpi_processor_performance`, parses `_PCT` control/status registers, extracts `_PSS` state packages, applies AMD frequency fixups for older families, validates frequency values, and updates the platform limit. Preregistration parses `_PSD` for all processors, validates domain membership and coordination type, builds shared CPU maps, then clears temporary `pr->performance` assignments until real registration. SMM notification writes FADT `pstate_control` to `smi_command` once and pins the caller module if `_PPC` is in use.

### State, Persistence, And Dependencies
State lives in per-processor performance structures, `performance_platform_limit`, per-CPU cpufreq QoS requests, `ignore_ppc`, `acpi_processor_ppc_in_use`, and the `performance_mutex`. Dependencies include ACPICA package extraction, cpufreq policy constraints, x86 CPUID/MSR helpers, FADT SMI control, and ACPI `_OST`.

### Integration Points
`processor_driver.c` invokes `_PPC` updates on ACPI notify and hooks policy create/remove. cpufreq drivers call the exported register and preregister functions to consume ACPI P-state data and shared-domain maps.

### Risks
Firmware package validation is strict but still accepts adjusted lists after invalid frequency entries. `_PPC` is ignored until cpufreq initialization unless overridden. Module reference handling in `acpi_processor_notify_smm()` intentionally prevents unloading in `_PPC` cases. Shared-domain errors degrade all CPUs to no coordination. x86-only code is conditionally compiled.

### Test Signals
Cover valid and malformed `_PCT`, `_PSS`, `_PPC`, and `_PSD`, invalid or overflowing frequencies, AMD fixup cases, cpufreq policy create/remove, `_PPC` notify with `_OST`, shared-domain mismatches, FADT SMI success/failure, and `ignore_ppc` settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_perflib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_thermal.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/processor_thermal.c

### Purpose
`processor_thermal.c` exposes each ACPI processor as a thermal cooling device. It maps cooling states first to cpufreq max-frequency QoS reductions and then, if needed, to ACPI T-state throttling.

### Important APIs, Types, And Functions
Public hooks are `acpi_processor_thermal_init()`, `acpi_processor_thermal_exit()`, `acpi_thermal_cpufreq_init()`, and `acpi_thermal_cpufreq_exit()`. Cooling callbacks are collected in `processor_cooling_ops`, backed by `processor_get_max_state()`, `processor_get_cur_state()`, and `processor_set_cur_state()`.

### Control Flow
Thermal init registers a `Processor` cooling device and creates reciprocal sysfs links between the ACPI device and cooling device. Cpufreq policy init adds per-CPU max-frequency QoS requests and updates the cooling device. Setting a cooling state uses cpufreq reduction steps up to `cpufreq_thermal_max_step`; higher states clamp cpufreq at the maximum reduction and request ACPI throttling for the remaining state. Reductions are package-wide using the first online CPU in the physical package as storage.

### State, Persistence, And Dependencies
State includes per-package emulated `cpufreq_thermal_reduction_step`, global reduction parameters, per-processor `thermal_req` QoS requests, and `pr->cdev`. Dependencies include cpufreq, thermal cooling devices, CPU topology, ACPI processor throttling, sysfs, and architecture-provided thermal reduction percentage.

### Integration Points
The processor driver calls thermal init/exit during processor start/stop. Cpufreq policy notifier callbacks in `processor_driver.c` call the cpufreq init/exit helpers. Thermal governors drive the cooling-device callbacks.

### Risks
Package state is emulated with per-CPU storage and can be lost temporarily across hot-unplug. The code assumes `per_cpu(processors, i)` exists for online package CPUs before touching QoS state. Frequency reduction parameters must avoid reducing performance to zero. Sysfs link creation has two-step unwind requirements.

### Test Signals
Test with and without `CONFIG_CPU_FREQ`, policy create/remove, package-level multi-CPU policies, cooling states that stay within cpufreq and cross into T-states, hotplug during thermal state changes, sysfs link failure injection, and architecture-specific reduction percentages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_throttling.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/processor_throttling.c

### Purpose
`processor_throttling.c` implements ACPI processor T-state throttling. It supports modern `_PTC`/`_TSS`/`_TPC`/`_TSD` control and legacy FADT P_BLK duty-cycle throttling.

### Important APIs, Types, And Functions
Public functions are `acpi_processor_throttling_init()`, `acpi_processor_get_throttling_info()`, `acpi_processor_set_throttling()`, `acpi_processor_tstate_has_changed()`, and `acpi_processor_reevaluate_tstate()`. Internals parse `_PTC`, `_TSS`, `_TSD`, and `_TPC`, compute FADT states, read/write status and control registers, and coordinate domain-wide changes through `__acpi_processor_set_throttling()`.

### Control Flow
Discovery first attempts modern ACPI throttling packages; if any required modern method is missing or invalid, it falls back to FADT duty-cycle data. `_TSD` domain data is parsed per CPU and later reconciled globally by `acpi_processor_throttling_init()`. Setting a T-state clamps the requested state against thermal, user, and `_TPC` platform limits through a prechange notifier, runs control on the target CPU with `call_on_cpu()`, optionally updates every CPU in shared SW_ALL/HW_ALL domains, then posts final state updates. `_TPC` notifications force current states down or up to the new platform limit.

### State, Persistence, And Dependencies
State resides in `struct acpi_processor_throttling`, per-processor limit fields, shared CPU maps, `ignore_tpc`, and legacy I/O regions. Dependencies include ACPI package extraction, cpumasks, CPU online masks, x86 MSR helpers for fixed hardware throttling, FADT, and cpufreq/thermal limit integration.

### Integration Points
`processor_driver.c` initializes coordination and calls T-state reevaluation on CPU online/dead transitions and ACPI throttling notifications. `processor_thermal.c` calls `acpi_processor_set_throttling()` for cooling states beyond cpufreq reduction.

### Risks
Modern method parsing is all-or-fallback, so partial firmware support becomes legacy throttling if possible. Shared-domain transitions call target functions with CPU affinity and must handle offline CPUs. The FADT path writes raw I/O ports with interrupts disabled. `_TPC` can be disabled with `ignore_tpc`. In `acpi_get_throttling_value()`, the bounds check allows `state == state_count`, which would be out of range if reached; callers otherwise validate `state <= state_count - 1`.

### Test Signals
Cover modern and FADT throttling, malformed `_PTC` bit widths, `_TSS` zero percentages, invalid `_TSD` domains, `_TPC` notifications and ignored mode, CPU online/offline reevaluation, SW_ANY versus SW_ALL/HW_ALL coordination, thermal-driven throttling, and fixed-hardware MSR failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/processor_throttling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/property.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/property.c

### Purpose
`property.c` implements ACPI device-specific properties and ACPI firmware-node operations. It parses `_DSD` property packages, non-device data subnodes, buffer properties, references, graph endpoints, child traversal, DMA metadata, and IRQ lookup through the generic `fwnode` abstraction.

### Important APIs, Types, And Functions
Key public APIs include `acpi_init_properties()`, `acpi_free_properties()`, `acpi_dev_get_property()`, `acpi_node_prop_get()`, `__acpi_node_get_property_reference()`, `is_acpi_device_node()`, and `is_acpi_data_node()`. Important internals include `acpi_extract_properties()`, `acpi_enumerate_nondev_subnodes()`, `acpi_data_get_property_array()`, `acpi_fwnode_get_reference_args()`, `acpi_data_prop_read()`, ACPI graph helpers, and the exported `acpi_device_fwnode_ops` and `acpi_data_fwnode_ops`.

### Control Flow
Initialization creates property/subnode lists, detects ACPI Device Tree namespace compatibility, evaluates `_DSD`, extracts GUID-matched property packages, converts referenced buffer properties, builds non-device subnode trees, tags namespace handles with data nodes, initializes `compatible`, and falls back to Apple property extraction if `_DSD` is unusable. Read paths search property lists by name, validate requested ACPI object types, convert integer/string/buffer arrays into generic device-property values, and resolve references either from local references or string paths. Fwnode operations expose child iteration, named child lookup, property reads, graph endpoint traversal, remote endpoint resolution, DMA attributes, and IRQ access.

### State, Persistence, And Dependencies
Parsed state is retained in `struct acpi_device_data`, `struct acpi_device_properties`, and `struct acpi_data_node` until `acpi_free_properties()`. Buffer property conversion owns separate ACPICA buffers. Dependencies include ACPICA object evaluation and handle tagging, Linux fwnode APIs, GUID helpers, ACPI graph conventions, DMA helpers, ACPI IRQ helpers, and optional Apple property support.

### Integration Points
This file lets drivers use generic firmware-property APIs with ACPI devices and data nodes, mirroring Device Tree-style property and graph access. It is used by driver core property reads, media graph consumers, GPIO/reference consumers, DMA setup, and IRQ lookup.

### Risks
Firmware package shape is complex and partially permissive across multiple equivalent GUIDs. Embedded reference packages can lose namespace scope, making string path references invalid. Lifetime management must not free ACPICA buffers while fwnode users retain references. Graph-node recognition accepts both `reg` plus `port@`/`endpoint@` and compatibility properties. Reference parsing intentionally supports holes and mixed string/reference forms.

### Test Signals
Test valid and malformed `_DSD`, multiple property GUIDs, buffer property GUID evaluation, nested data subnodes, direct and string references with arguments, holes in reference arrays, integer overflow in property reads, string-array reads, ACPI graph endpoint parsing and remote endpoints, property cleanup with tagged subnodes, and Apple fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/reboot.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/reboot.c

### Purpose
`reboot.c` performs ACPI reset-register based reboot when the FADT declares a valid reset register and reset value.

### Important APIs, Types, And Functions
The main API is `acpi_reboot()`. The helper `acpi_pci_reboot()` writes PCI configuration space reset registers when `CONFIG_PCI` is enabled; otherwise it is a no-op. Generic address writes are delegated to `acpi_reset()`.

### Control Flow
`acpi_reboot()` checks `acpi_gbl_FADT.flags` for `ACPI_FADT_RESET_REGISTER`, then verifies the reset register bit width is 8 and bit offset is 0. If the address space is PCI config space it calls `acpi_pci_reboot()`, otherwise it calls `acpi_reset()`. The PCI path locates the root bus, finds the target device/function derived from the reset-register address, writes the reset value to the derived config offset, and waits ten milliseconds.

### State, Persistence, And Dependencies
The file has no persistent state. It depends on FADT global data, ACPICA reset support, PCI bus/device helpers when configured, and delay primitives.

### Integration Points
Architecture reboot paths can call `acpi_reboot()` as a firmware-defined reset mechanism. It bridges ACPI FADT reset metadata to either generic ACPI address-space writes or PCI config writes.

### Risks
Strict width/offset validation rejects non-byte reset registers. PCI reset depends on address encoding, root bus 0 availability, and device lookup. If PCI is disabled, PCI-space reset registers are ignored. Firmware-provided reset registers may be wrong or ineffective.

### Test Signals
Check FADT without reset flag, invalid width/offset, system-memory/system-I/O reset through `acpi_reset()`, PCI reset with present and missing device, PCI-disabled builds, and reboot fallback behavior when reset does not occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/resource.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/resource.c

### Purpose
`resource.c` translates ACPI resource descriptors from methods such as `_CRS` and `_DMA` into Linux `struct resource` lists. It handles memory, I/O, address windows, IRQs, DMA filtering, resource consumers, and platform-specific IRQ override quirks.

### Important APIs, Types, And Functions
Exports include `acpi_dev_resource_memory()`, `acpi_dev_resource_io()`, `acpi_dev_resource_address_space()`, `acpi_dev_resource_ext_address_space()`, `acpi_dev_irq_flags()`, `acpi_dev_get_irq_type()`, `acpi_dev_resource_interrupt()`, `acpi_dev_get_resources()`, `acpi_dev_get_dma_resources()`, `acpi_dev_get_memory_resources()`, `acpi_dev_filter_resource_type()`, `acpi_dev_free_resource_list()`, and `acpi_resource_consumer()`.

### Control Flow
Memory and I/O helpers identify descriptor types, compute start/end ranges, validate length and architecture constraints, and set Linux resource flags. Address-space decoding applies producer translation offsets, detects CPU-address truncation, marks windows, and handles memory/I/O/bus ranges. IRQ decoding converts ACPI trigger/polarity/share/wake fields, applies x86 and DMI override policy for legacy IRQ descriptors, registers GSIs, and marks failed mappings disabled. `acpi_dev_get_resources()` walks `_CRS`, optionally lets callers preprocess each ACPI resource, converts recognized descriptors to `resource_entry` objects, and returns a count. DMA and memory helpers are filters over the same walker.

### State, Persistence, And Dependencies
State is mostly transient resource lists allocated for callers. Static DMI tables encode IRQ override quirks for known machines. Dependencies include ACPICA resource walking, Linux resource lists, IRQ/GSI registration, DMI, architecture IRQ override data, and x86 CPU-feature checks.

### Integration Points
ACPI-enumerated platform, PCI, serial, GPIO, I2C, SPI, and other drivers use these helpers to obtain resources. `acpi_resource_consumer()` scans the ACPI namespace to find which device consumes a given resource.

### Risks
Firmware often reports invalid lengths or IRQ polarity; the code contains compatibility behavior and DMI exceptions. Legacy IRQ overrides differ from extended IRQ descriptors. Resource-window arithmetic can overflow smaller `resource_size_t` architectures and is rejected. Callers must pass an empty list and free it. GSI registration failures still produce a disabled resource entry.

### Test Signals
Exercise all memory/I/O descriptor forms, address16/32/64 and extended address spaces, producer windows with translation offsets, invalid/unassigned resources, x86 I/O range limits, IRQ and extended IRQ descriptors, DMI override systems, `_DMA` filtering, preprocessor skip/abort paths, and resource-consumer namespace scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/Kconfig

### Purpose
`riscv/Kconfig` declares RISC-V-specific ACPI configuration for this directory.

### Important APIs, Types, And Functions
It defines the boolean symbol `ACPI_RIMT`, which controls compilation of RISC-V IOMMU Mapping Table support.

### Control Flow
There is no runtime control flow. Kconfig selection elsewhere enables or disables `CONFIG_ACPI_RIMT`, and the Makefile uses that symbol to include `rimt.o`.

### State, Persistence, And Dependencies
The only state is build configuration. It depends on the surrounding kernel Kconfig system and the RISC-V ACPI build.

### Integration Points
`CONFIG_ACPI_RIMT` gates `drivers/acpi/riscv/rimt.c` and the `riscv_acpi_rimt_init()` call path in `init.c`.

### Risks
The symbol has no prompt in this file, so it must be selected by other configuration logic. If not selected on systems needing RIMT IOMMU discovery, device IOMMU configuration through RIMT will be unavailable.

### Test Signals
Validate build configs with `ACPI_RIMT=y` and unset, confirm `rimt.o` inclusion/exclusion, and boot-test RISC-V ACPI systems with and without RIMT tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/Makefile -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/Makefile

### Purpose
`riscv/Makefile` selects the RISC-V ACPI object files compiled into the kernel.

### Important APIs, Types, And Functions
It always builds `rhct.o`, `init.o`, and `irq.o`; conditionally builds `cpuidle.o` under `CONFIG_ACPI_PROCESSOR_IDLE`, `cppc.o` under `CONFIG_ACPI_CPPC_LIB`, and `rimt.o` under `CONFIG_ACPI_RIMT`.

### Control Flow
There is no runtime control flow. Build-time configuration determines which RISC-V ACPI capabilities are present.

### State, Persistence, And Dependencies
State is the kernel build graph. Dependencies are the corresponding Kconfig symbols and object files.

### Integration Points
The Makefile connects generic ACPI processor idle and CPPC options to RISC-V-specific FFH implementations, and connects `ACPI_RIMT` to IOMMU table support.

### Risks
Missing config symbols omit architecture hooks that generic ACPI code may weakly fall back from. Always-built `init.o`, `irq.o`, and `rhct.o` assume RISC-V ACPI core support is being compiled.

### Test Signals
Build matrix tests should cover idle on/off, CPPC on/off, RIMT on/off, and ensure unresolved symbols do not appear when optional files are omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/cppc.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/cppc.c

### Purpose
`riscv/cppc.c` implements RISC-V CPPC fixed-hardware accessors used by the generic ACPI CPPC library. It supports FFH register encodings backed by SBI CPPC calls and a limited CSR path.

### Important APIs, Types, And Functions
The exported architecture hooks are `cpc_ffh_supported()`, `cpc_read_ffh()`, and `cpc_write_ffh()`. Internal helpers include `sbi_cppc_init()`, `sbi_cppc_read()`, `sbi_cppc_write()`, `cppc_ffh_csr_read()`, and `cppc_ffh_csr_write()`. `struct sbi_cppc_data` carries the register, value, and SBI return.

### Control Flow
At device init, the file probes SBI version and the CPPC extension. Reads and writes reject IRQ-disabled callers, decode the FFH type from the ACPI CPPC register address, and execute the operation on the target CPU using `smp_call_function_single()`. SBI reads/writes call `sbi_ecall()` and map SBI errors to Linux errno. CSR reads currently support only `CSR_TIME`; CSR writes always fail with `-EINVAL`.

### State, Persistence, And Dependencies
The retained state is `cppc_ext_present`. Dependencies include ACPI CPPC register definitions, RISC-V SBI probing/ecalls, CSR accessors, SMP cross-calls, and Linux errno mapping.

### Integration Points
Generic `drivers/acpi/cppc_acpi.c` calls these hooks when CPPC register descriptors use fixed hardware space on RISC-V. `processor_driver.c` indirectly depends on this through `acpi_cppc_processor_probe()`.

### Risks
Calls require interrupts enabled because they send synchronous IPIs. SBI CPPC support is only available with SBI spec 2.0 or later plus extension presence. CSR support is intentionally narrow. Data is stack-local but passed synchronously to the target CPU, so the blocking cross-call is required.

### Test Signals
Test SBI-present and absent systems, reads/writes to SBI-encoded CPPC registers, CSR TIME reads, unsupported CSR writes, unknown FFH type, IRQ-disabled warnings, target CPU offline behavior, and SBI error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/cppc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/cpuidle.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/cpuidle.c

### Purpose
`riscv/cpuidle.c` provides RISC-V ACPI FFH LPI validation and entry hooks for the generic ACPI processor idle driver.

### Important APIs, Types, And Functions
The public hooks are `acpi_processor_ffh_lpi_probe()` and `acpi_processor_ffh_lpi_enter()`. `acpi_cpu_init_idle()` validates all nonzero LPI states for a CPU.

### Control Flow
Probe retrieves the per-CPU ACPI processor, requires `_LPI` state data, requires SBI HSM support, requires more than the baseline state, then validates each state address against the RISC-V FFH encoding: type bits must indicate SBI, reserved bits must be zero, and the low 32-bit SBI power state must be valid. Entry chooses retention or non-retention CPU PM wrappers based on `SBI_HSM_SUSP_NON_RET_BIT` and calls `riscv_sbi_hart_suspend()`.

### State, Persistence, And Dependencies
There is no retained state. Dependencies include ACPI processor LPI data, SBI HSM suspend support, CPU PM idle wrappers, and RISC-V suspend helpers.

### Integration Points
`processor_idle.c` calls these functions from LPI discovery and idle entry when ACPI `_LPI` states use fixed hardware methods on RISC-V.

### Risks
Any invalid LPI address disables the ACPI LPI path for that CPU. The address is a 64-bit ACPI field but the SBI state is truncated to 32 bits after validation. Entry assumes the generic idle layer selected an already-validated LPI state.

### Test Signals
Test absent processor data, no SBI HSM, single-state `_LPI`, invalid type bits, nonzero reserved bits, invalid SBI power states, retention and non-retention entry, and interaction with suspend-to-idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/cpuidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.c

### Purpose
`riscv/init.c` performs RISC-V ACPI architecture initialization.

### Important APIs, Types, And Functions
The file defines `acpi_arch_init()`.

### Control Flow
During ACPI architecture initialization, it initializes RISC-V GSI mapping with `riscv_acpi_init_gsi_mapping()`. If `CONFIG_ACPI_RIMT` is enabled, it also initializes the cached RIMT table through `riscv_acpi_rimt_init()`.

### State, Persistence, And Dependencies
This file owns no state. It depends on declarations in `init.h` and on the implementations in `irq.c` and optionally `rimt.c`.

### Integration Points
The generic ACPI core invokes `acpi_arch_init()` so RISC-V interrupt-controller and IOMMU table discovery are ready before ACPI devices that depend on GSIs or IOMMUs are configured.

### Risks
Initialization order is important: GSI mapping must exist before IRQ dependencies and domain lookup are used. RIMT initialization is compile-time gated.

### Test Signals
Boot-test RISC-V ACPI with PLIC, APLIC, SYSMSI, and RIMT combinations; confirm GSI and IOMMU discovery are available before dependent device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.h -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.h

### Purpose
`riscv/init.h` declares internal RISC-V ACPI initialization hooks shared by the RISC-V ACPI source files.

### Important APIs, Types, And Functions
It declares `riscv_acpi_init_gsi_mapping()` and `riscv_acpi_rimt_init()`.

### Control Flow
There is no runtime control flow in the header.

### State, Persistence, And Dependencies
The header includes `<linux/init.h>` to support `__init` annotations and depends on the matching definitions in `irq.c` and `rimt.c`.

### Integration Points
`init.c` includes this header to call interrupt and RIMT initialization without exporting those functions outside the RISC-V ACPI directory.

### Risks
If optional RIMT compilation and declarations get out of sync, builds can fail. The header intentionally stays narrow, so new initialization hooks need explicit declarations.

### Test Signals
Build with and without `CONFIG_ACPI_RIMT`, and ensure `__init` declarations match definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/irq.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/irq.c

### Purpose
`riscv/irq.c` implements RISC-V ACPI interrupt-controller ordering, GSI-domain mapping, and automatic ACPI scan dependencies for IRQ providers.

### Important APIs, Types, And Functions
Key APIs include `arch_sort_irqchip_probe()`, `riscv_acpi_update_gsi_range()`, `riscv_acpi_get_gsi_info()`, `riscv_acpi_get_gsi_domain_id()`, `riscv_acpi_init_gsi_mapping()`, and `arch_acpi_add_auto_dep()`. The static `ext_intc_list` holds `struct riscv_ext_intc_list` entries for PLIC, APLIC, and SYSMSI-like controllers.

### Control Flow
MADT IRQ-chip probe entries are sorted by subtype so RINTC precedes IMSIC, APLIC, and PLIC. GSI initialization parses PLIC first and maps `RSCV0001` devices, otherwise parses APLIC and maps `RSCV0002`; SYSMSI devices `RSCV0006` are discovered from namespace `_GSB` because they have no MADT entry. Each external interrupt-controller list entry tracks GSI base, IRQ count, IDC count, ID, ACPI handle, and pending range. Later queries resolve GSIs to ACPI fwnodes. Automatic dependency creation scans `_PRT` or `_CRS` IRQ resources and adds scan dependencies from consumers to IRQ provider handles.

### State, Persistence, And Dependencies
State is the global `ext_intc_list`, allocated during `__init` discovery and retained for runtime lookup. Dependencies include MADT parsing, ACPI namespace device lookup, `_GSB`, `_CRS`, `_PRT`, scan dependency APIs, fwnode conversion, and Linux sort/list helpers.

### Integration Points
Interrupt-controller drivers use GSI info and domain IDs to initialize domains. ACPI scan uses `arch_acpi_add_auto_dep()` to defer consumers until interrupt providers are available.

### Risks
Pending GSI ranges are inferred from the next registered base; ordering and firmware `_GSB` correctness matter. Some allocation failures in dependency creation continue without freeing allocated handle arrays after `acpi_scan_add_dep()` ownership assumptions. `_PRT` entries with missing source handles can add null dependencies if GSI lookup fails. The list insertion loop is subtle because it keeps ranges sorted by descending base.

### Test Signals
Test PLIC-only, APLIC-only, SYSMSI-only, mixed APLIC/SYSMSI, pending range update, `_GSB` missing/failing, GSI lookup boundaries, `_PRT` source and direct-GSI entries, extended IRQ producer filtering, and ACPI scan dependency ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/rhct.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/rhct.c

### Purpose
`riscv/rhct.c` reads the RISC-V Hart Capabilities Table to expose per-CPU ISA strings and cache-block operation sizes.

### Important APIs, Types, And Functions
The exported-style functions are `acpi_get_riscv_isa()` and `acpi_get_cbo_block_size()`. `acpi_get_rhct()` caches the RHCT table for runtime use, and `acpi_parse_hart_info_cmo_node()` extracts CMO node data referenced by hart-info nodes.

### Control Flow
`acpi_get_riscv_isa()` maps a Linux CPU to an ACPI CPU UID, obtains either a caller-provided RHCT table or the cached runtime table, scans RHCT nodes for a hart-info node with a matching UID, follows its node offsets, and returns the first referenced ISA string node. `acpi_get_cbo_block_size()` resets requested outputs to zero, scans all hart-info nodes, follows CMO references, and records `BIT(encoded_size)` for CBOM, CBOZ, and CBOP sizes while warning if sizes differ across harts.

### State, Persistence, And Dependencies
The cached RHCT pointer is retained without releasing the ACPI table mapping because runtime callers may reuse it. Dependencies include ACPI table APIs, RHCT struct definitions, ACPI CPU UID lookup, and bit helpers.

### Integration Points
RISC-V architecture code can query ISA strings and CBO block sizes during early boot or runtime. Callers that already own an RHCT mapping can pass it in and release it themselves later.

### Risks
The parser trusts RHCT node lengths and offsets from firmware. Encoded CBO sizes above 30 are ignored. ISA lookup returns `-1` rather than a conventional errno when no matching node is found. Cached-table lifetime follows ACPI core behavior.

### Test Signals
Test absent RHCT, caller-provided table, matching and missing CPU UIDs, multiple ISA references, malformed offsets, consistent and inconsistent CBO sizes, encoded sizes above 30, and ACPI-disabled paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/rhct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/rimt.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/riscv/rimt.c

### Purpose
`riscv/rimt.c` implements RISC-V IOMMU Mapping Table support. It associates RIMT IOMMU nodes with Linux fwnodes and configures PCI or platform devices with ACPI IOMMU fwspecs by walking RIMT ID-mapping chains.

### Important APIs, Types, And Functions
Public hooks include `riscv_acpi_rimt_init()`, `rimt_iommu_register()`, and, under `CONFIG_IOMMU_API`, `rimt_iommu_configure_id()`. Key internals include `rimt_scan_node()`, `rimt_match_node_callback()`, `rimt_set_fwnode()`, `rimt_get_fwnode()`, `rimt_node_map_id()`, `rimt_node_map_platform_id()`, and `rimt_iommu_xlate()`.

### Control Flow
Initialization caches the RIMT table mapping for runtime use. IOMMU drivers register themselves by finding their RIMT IOMMU node via PCI segment/BDF or platform MMIO base, creating a static fwnode for PCI IOMMUs if needed, and storing the node-to-fwnode association in a locked list. Device configuration scans the RIMT for the device's PCI root complex or platform-device node, walks ID mapping entries toward an IOMMU node, translates request IDs to destination IDs, defers probing if the target IOMMU fwnode is not registered, adds a device link to enforce removal ordering, and initializes the ACPI IOMMU fwspec. PCI root-complex ATS support is propagated to the fwspec flag.

### State, Persistence, And Dependencies
State includes the cached `rimt_table` pointer and the spinlock-protected `rimt_fwnode_list`. Dependencies include ACPI RIMT table structures, PCI and platform device APIs, IOMMU fwspec helpers, device links, ACPI full-path lookup, and optional `CONFIG_IOMMU_API`.

### Integration Points
RISC-V IOMMU drivers call `rimt_iommu_register()`. ACPI/IOMMU core code calls `rimt_iommu_configure_id()` to attach devices to the correct IOMMU. `init.c` calls `riscv_acpi_rimt_init()` when enabled.

### Risks
Firmware-provided RIMT offsets and ID ranges are trusted with bounds checks limited to scan end and null-destination warnings. `rimt_id_map()` treats `source_id_base + num_ids` as inclusive, which is worth validating against the table spec. `rimt_pci_iommu_init()` maps the same PCI alias twice before translation, likely redundant. Probe deferral is expected until IOMMU drivers register fwnodes.

### Test Signals
Test absent and malformed RIMT, PCI IOMMU registration, platform IOMMU registration, PCI root-complex mapping with DMA aliases, platform devices with explicit and implicit IDs, missing IOMMU fwnode deferral, ATS flag propagation, invalid/null destination offsets, and shutdown ordering via device links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/riscv/rimt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sbs.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/sbs.c

### Purpose
`sbs.c` implements the ACPI Smart Battery System platform driver. It exposes SBS chargers and up to four smart batteries through the Linux power-supply subsystem using ACPI SMBus host-controller transactions.

### Important APIs, Types, And Functions
The driver defines `struct acpi_sbs`, `struct acpi_battery`, power-supply descriptors and property arrays, `acpi_sbs_probe()`, `acpi_sbs_remove()`, `acpi_sbs_callback()`, battery info/state/alarm helpers, charger helpers, and resume handling. SMBus field readers are described by `struct acpi_battery_reader` arrays.

### Control Flow
Probe obtains the ACPI companion and parent SMBus host-controller data, allocates `acpi_sbs`, registers a charger if charger status is valid, queries the SBS manager unless running on Apple x86, registers all manager-reported battery slots or falls back to battery 0, and registers an SMBus callback. Battery registration selects charge-based or energy-based property sets depending on battery mode, reads static info on presence changes, caches dynamic state for `cache_time`, and registers power supplies with an `alarm` sysfs attribute. The callback updates charger presence and battery presence and emits `power_supply_changed()` notifications. Remove unregisters callback, batteries, charger, and frees state under a mutex.

### State, Persistence, And Dependencies
State is in the allocated `acpi_sbs` and embedded battery array: cached static strings, capacities, state values, update timestamps, presence flags, and charger flags. Dependencies include `sbshc` ACPI SMBus helpers, power-supply core, jiffies caching, Apple platform detection, platform driver binding, and ACPI device IDs.

### Integration Points
The driver binds ACPI HID `ACPI0002` as a platform child of an SBS host controller. Userspace observes `BAT0`-style batteries and `sbs-charger` through power-supply sysfs and uevents.

### Risks
SMBus block reads write directly into fixed-size battery string buffers and rely on host helper behavior respecting `ACPI_SBS_BLOCK_MAX`. Dynamic state is cached even after read failure. Manager selection writes to selector registers before battery reads. Apple systems skip manager probing. Remove assumes valid driver data and serializes only its own teardown, while callbacks depend on host-controller unregister semantics.

### Test Signals
Test charger-present/absent and invalid charger status, manager-present multi-battery systems, no-manager fallback, Apple x86 path, battery insertion/removal callbacks, cache expiration, charge versus energy mode property reporting, alarm show/store, SMBus read/write failures, resume refresh, and module removal during callback activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sbs.c -->
