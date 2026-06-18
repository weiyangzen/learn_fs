# subset-b-005835 Research

Grouped research for Linux header files under `sources/distributed-fs/ceph-client/include/linux`. Each section is source-tree-aligned and delimited for deterministic split into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/pl08x.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/pl08x.h

## Purpose
Defines the platform-facing contract for ARM PrimeCell PL08x DMA controllers. It supplies channel descriptors, DMA bus-width/burst enums, controller-wide platform data, and the optional `pl08x_filter_id()` DMA-engine filter used by board/platform code to match DMA slave channels.

## Important APIs, Types, And Functions
`struct pl08x_channel_data` describes one logical peripheral channel with `bus_id`, signal range, mux value, FIFO/device `addr`, single-vs-burst behavior, and permitted AHB buses. `struct pl08x_platform_data` aggregates channels, memcpy defaults, signal acquire/release callbacks, LLI/memory bus masks, and the `dma_slave_map` table. `enum pl08x_burst_size` and `enum pl08x_bus_width` encode hardware transfer sizing. `pl08x_filter_id()` is declared only with `CONFIG_AMBA_PL08X`; otherwise it returns false.

## Control Flow, State, And Persistence
The header itself has no runtime state. It defines static platform configuration consumed during PL08x driver probe and DMA channel matching. The stateful path is delegated to platform callbacks: `get_xfer_signal()` reserves/muxes a signal before transfer and `put_xfer_signal()` releases it afterward.

## Dependencies And Integration Points
Depends on `linux/dmaengine.h` for `dma_addr_t`, `dma_chan`, and slave maps, and `linux/interrupt.h` for platform integration. Consumers include AMBA platform registration code and DMA clients that request channels by `bus_id`.

## Risks And Test Signals
Incorrect signal ranges, mux values, or bus masks can cause channel conflicts, silent transfer stalls, or DMA to the wrong peripheral FIFO. Tests should cover DMA slave matching, memcpy defaults, mux callback failure paths, concurrent channel allocation, and build coverage with and without `CONFIG_AMBA_PL08X`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/pl08x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/serial.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/serial.h

## Purpose
Provides register offsets and bit definitions for AMBA PL010/PL011 UARTs and several vendor variants, plus small platform-data hooks for AMBA serial drivers.

## Important APIs, Types, And Functions
The file defines PL010/PL011 offsets such as `UART01x_DR`, `UART011_IBRD`, `UART011_LCRH`, `UART011_IMSC`, `UART011_ICR`, and `UART011_DMACR`, ST-specific registers such as `ST_UART011_DMAWM`, and ZTE `ZX_UART011_*` offsets. It exposes bit masks for status, receive errors, modem signals, line control, FIFO trigger levels, interrupt masks/status/clear bits, and DMA enable bits. `struct amba_pl010_data` contains a `set_mctrl()` callback. `struct amba_pl011_data` contains DMA filter parameters, RX polling settings, and optional init/exit callbacks.

## Control Flow, State, And Persistence
There is no stored state in the header. Driver control flow uses the offsets to program UART registers, clear interrupts, configure FIFOs and DMA watermarks, and route DMA channels through the platform hooks. The platform data persists as device configuration for the UART lifetime.

## Dependencies And Integration Points
Uses `linux/bitfield.h`, `linux/bits.h`, and `linux/types.h`. It is consumed by PL010/PL011 serial drivers, early console/uncompress code, DMA-engine integration, and board/vendor-specific register layout handling.

## Risks And Test Signals
The main risk is mixing register layouts: ZTE offsets and ST extensions are not interchangeable with the baseline PL011 map. Incorrect interrupt clear or DMA bits can wedge console I/O. Test signals include boot console output, normal TTY transmit/receive, modem-control changes, DMA RX/TX operation, interrupt storm absence, and build checks for assembly inclusion where only constants are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/sp810.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/sp810.h

## Purpose
Defines ARM PrimeXsys SP810 system controller register offsets and a small reset helper.

## Important APIs, Types, And Functions
The header lists system-controller offsets from `SCCTRL` through PrimeCell ID registers and defines `SCCTRL_TIMERENnSEL_SHIFT(n)` for timer clock selection fields. `sysctl_soft_reset(void __iomem *base)` writes slow mode to `SCCTRL`, then writes `SCSYSSTAT` to trigger a system reset.

## Control Flow, State, And Persistence
The only executable flow is the inline reset sequence. It mutates system-controller MMIO state and may reset the whole machine, so it is effectively terminal control flow from the caller perspective.

## Dependencies And Integration Points
Depends on `linux/io.h` for `writel()` and `__iomem`. Integrated by ARM platform code controlling SP810 clocks, timers, and reset behavior.

## Risks And Test Signals
Calling `sysctl_soft_reset()` on the wrong mapping or wrong hardware can corrupt unrelated MMIO or reset unexpectedly. Tests are mostly platform/boot validation: correct DT/ACPI mapping, timer clock selection, reset path confirmation, and no compile warnings on platforms that include but do not invoke the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/sp810.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amd-iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/amd-iommu.h

## Purpose
Declares AMD IOMMU discovery, interrupt remapping/guest AVIC hooks, performance-counter accessors, and SEV-SNP/TIO support helpers.

## Important APIs, Types, And Functions
`amd_iommu_detect()` is real only with `CONFIG_AMD_IOMMU`. Guest/GA log functions such as `amd_iommu_register_ga_log_notifier()`, `amd_iommu_update_ga()`, `amd_iommu_activate_guest_mode()`, and `amd_iommu_deactivate_guest_mode()` are available only when both AMD IOMMU and IRQ remapping are enabled. Performance counter helpers include `amd_iommu_get_num_iommus()`, `amd_iommu_pc_supported()`, bank/counter limit accessors, and `amd_iommu_pc_{set,get}_reg()`. `amd_iommu_snp_disable()` and `amd_iommu_sev_tio_supported()` are gated by `CONFIG_KVM_AMD_SEV`.

## Control Flow, State, And Persistence
The header does not own state. It gates call sites so nonconfigured builds compile to harmless no-ops or false returns. Real state lives in AMD IOMMU core objects represented by opaque `struct amd_iommu`.

## Dependencies And Integration Points
Depends on `linux/types.h` and interacts with x86 IOMMU, KVM AMD, IRQ remapping, SEV-SNP, and IOMMU performance-counter code.

## Risks And Test Signals
Stubbed success returns can hide disabled feature paths if callers do not separately check capabilities. Tests should cover config matrices, KVM guest mode activation/deactivation, GA log notification, performance-counter bounds, SNP disable behavior, and build coverage without AMD IOMMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amd-iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amd-pmf-io.h -->
# sources/distributed-fs/ceph-client/include/linux/amd-pmf-io.h

## Purpose
Defines the interface between AMD Platform Management Framework consumers and PMF/SFH firmware-facing providers for sensor and NPU metric queries.

## Important APIs, Types, And Functions
`enum sfh_message_type` selects HPD, ambient light, or SRA data. `enum sfh_hpd_info` describes human-presence state. `struct amd_sfh_info` carries ambient light, user presence, platform type, and laptop placement. `enum laptop_placement` names placement states such as table, lap motion, in bag, and out of bag. `struct amd_pmf_npu_metrics` reports NPU clock, per-engine busy array, power, MPNPU clock, and read/write bandwidth. Exported functions are `amd_get_sfh_info()` and `amd_pmf_get_npu_data()`.

## Control Flow, State, And Persistence
The header only describes synchronous query calls. Runtime state is supplied by PMF/SFH firmware and copied into caller-provided output structures. No persistence is defined beyond the current sample returned by the PMF driver.

## Dependencies And Integration Points
Depends on `linux/types.h`. Integrates PMF, AMD Sensor Fusion Hub/MP2 firmware, platform profile, presence sensing, ambient-light handling, and NPU telemetry consumers.

## Risks And Test Signals
Risks include stale firmware data, struct layout mismatches across providers, and consumers assuming units or enum values not guaranteed by firmware. Tests should validate NULL/invalid output handling in implementations, unit ranges, HPD state transitions, NPU busy array bounds, and build linkage when PMF providers are modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amd-pmf-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/annotate.h -->
# sources/distributed-fs/ceph-client/include/linux/annotate.h

## Purpose
Provides objtool annotation macros for assembly and inline assembly so the kernel can describe special control-flow, instrumentation, CFI, retpoline, ENDBR, and livepatch data cases.

## Important APIs, Types, And Functions
With `CONFIG_OBJTOOL`, `__ASM_ANNOTATE()` emits records into discardable annotate sections. C-facing macros include `ASM_ANNOTATE_LABEL()`, `ASM_ANNOTATE()`, `ASM_ANNOTATE_DATA()`, `ANNOTATE_NOENDBR`, `ANNOTATE_RETPOLINE_SAFE`, `ANNOTATE_INSTR_BEGIN/END`, `ANNOTATE_IGNORE_ALTERNATIVE`, `ANNOTATE_INTRA_FUNCTION_CALL`, `ANNOTATE_UNRET_BEGIN`, `ANNOTATE_REACHABLE`, `ANNOTATE_NOCFI_SYM`, and `ANNOTATE_DATA_SPECIAL`. Assembly mode defines `ANNOTATE` and `ANNOTATE_DATA` macros.

## Control Flow, State, And Persistence
The macros do not change runtime state. They add metadata sections consumed by objtool during build-time validation and discarded from the final runtime image as appropriate.

## Dependencies And Integration Points
Depends on `linux/objtool_types.h` for annotation type constants. Integrates with objtool, x86/arm64 assembly, retpoline validation, CFI validation, alternatives, instrumentation markers, and livepatch extraction.

## Risks And Test Signals
Annotations can suppress real control-flow or CFI issues if overused, especially `ANNOTATE_NOCFI_SYM`. Test signals are objtool warnings, build coverage with and without `CONFIG_OBJTOOL`, section emission inspection, and architecture assembly builds using the macros from both C and assembly contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/annotate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/anon_inodes.h -->
# sources/distributed-fs/ceph-client/include/linux/anon_inodes.h

## Purpose
Declares anonymous inode helpers used by subsystems that need file descriptors or `struct file` objects without a named filesystem inode.

## Important APIs, Types, And Functions
The API includes `anon_inode_getfile()`, `anon_inode_getfile_fmode()`, and `anon_inode_create_getfile()` for file objects, plus `anon_inode_getfd()` and `anon_inode_create_getfd()` for installed file descriptors. The create variants accept a `context_inode` for security and ownership context.

## Control Flow, State, And Persistence
The header only declares constructors. Runtime implementations allocate or reuse anonymous inodes, attach caller-provided `file_operations` and `priv`, apply flags/fmode, and optionally install an fd. Lifetime is governed by normal file reference counting and fops release paths.

## Dependencies And Integration Points
Depends on `linux/types.h` and forward declarations for `file_operations` and `inode`. Integrated by eventfd, timerfd, io_uring, KVM, perf, BPF, and other fd-producing kernel APIs.

## Risks And Test Signals
Risks include incorrect flags, missing release handlers for `priv`, wrong `context_inode` for LSM checks, and fd leaks on error. Tests should validate fd install failure cleanup, fops callbacks, close/release behavior, LSM labeling, and poll/read/write behavior for each anon-inode consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/anon_inodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aperture.h -->
# sources/distributed-fs/ceph-client/include/linux/aperture.h

## Purpose
Declares helpers for graphics/framebuffer aperture ownership and removal of conflicting framebuffer or VGA devices.

## Important APIs, Types, And Functions
When `CONFIG_APERTURE_HELPERS` is enabled, the API includes `devm_aperture_acquire_for_platform_device()`, `aperture_remove_conflicting_devices()`, `__aperture_remove_legacy_vga_devices()`, and `aperture_remove_conflicting_pci_devices()`. Stubs return success when helpers are disabled. `aperture_remove_all_conflicting_devices()` is an inline wrapper over the full resource range.

## Control Flow, State, And Persistence
The helpers coordinate device ownership around memory apertures. They may unregister or remove existing framebuffer/graphics devices so a new driver can safely claim display memory. Devm acquisition persists until the platform device is detached.

## Dependencies And Integration Points
Uses `linux/types.h` and forward declarations for PCI and platform devices. Integrates DRM, fbdev, VGA legacy cleanup, platform display drivers, and resource management.

## Risks And Test Signals
Disabled stubs returning success can allow callers to skip conflict removal in unsupported configs. Runtime risks include removing the wrong framebuffer range or leaving active legacy VGA owners. Tests should cover DRM driver probe over EFI/simplefb, overlapping aperture ranges, platform devm release, PCI VGA removal, and config-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aperture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/apm-emulation.h -->
# sources/distributed-fs/ceph-client/include/linux/apm-emulation.h

## Purpose
Defines architecture-neutral APM emulation status data and event injection hooks for systems that emulate APM behavior without a PC BIOS implementation.

## Important APIs, Types, And Functions
`struct apm_power_info` contains AC line state, battery state/flags, battery life, remaining time, and time units. It declares the function pointer `apm_get_power_status` for machine-specific population and `apm_queue_event(apm_event_t event)` for queuing suspend-related APM events.

## Control Flow, State, And Persistence
Consumers call `apm_get_power_status()` through the global function pointer to fill status with safe defaults for unspecified fields. `apm_queue_event()` feeds the APM event stream. Persistent battery state is not stored here; it is sampled from architecture/platform code.

## Dependencies And Integration Points
Includes `linux/apm_bios.h` for APM event types and BIOS constants. Integrates handheld/ARM APM emulation, userspace APM interfaces, and suspend event reporting.

## Risks And Test Signals
Risks include uninitialized status fields, wrong units, and event ordering differences from BIOS-backed APM. Tests should inspect `/proc/apm` style output where available, verify suspend event delivery, handle unknown battery values, and build architectures that set or omit `apm_get_power_status`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/apm-emulation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/apm_bios.h -->
# sources/distributed-fs/ceph-client/include/linux/apm_bios.h

## Purpose
Defines kernel-side APM BIOS constants, persistent APM information, BIOS function codes, and device selection helpers.

## Important APIs, Types, And Functions
The header imports the UAPI APM definitions, defines segment selectors `APM_CS`, `APM_CS_16`, and `APM_DS`, installation flags such as `APM_16_BIT_SUPPORT`, and BIOS function constants from `APM_FUNC_INST_CHECK` through timer/ring operations. `struct apm_info` stores BIOS information and persistent driver policy flags. Global `apm_info` is declared, and `APM_DEVICE_BALL` selects all-device IDs based on connection version.

## Control Flow, State, And Persistence
`struct apm_info` is explicitly persistent across APM module unload/load, carrying BIOS metadata and quirk flags. Control flow using this header is low-level BIOS-call orchestration in architecture APM code.

## Dependencies And Integration Points
Depends on `uapi/linux/apm_bios.h` and architecture GDT definitions. Integrated with x86 APM setup, power-off, idle, suspend/resume, and legacy userspace APM interfaces.

## Risks And Test Signals
Incorrect function codes or segment assumptions can break BIOS calls on legacy systems. Risks also include stale persistent quirk flags after reload. Tests are legacy-platform focused: APM detection, power status calls, suspend/resume events, power-off behavior, and module reload persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/apm_bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/apple-gmux.h -->
# sources/distributed-fs/ceph-client/include/linux/apple-gmux.h

## Purpose
Defines Apple gmux detection helpers and register/port constants for the GPU mux microcontroller found in dual-GPU Mac systems.

## Important APIs, Types, And Functions
Constants cover gmux ACPI HID, PIO ports for version, display/DDC/external switching, discrete power, brightness, indexed I/O, and MMIO command selection. `enum apple_gmux_type` distinguishes PIO, indexed, and MMIO. With `CONFIG_APPLE_GMUX`, helpers include `apple_gmux_is_indexed()`, `apple_gmux_is_mmio()`, `apple_gmux_detect()`, and `apple_gmux_present()`. Disabled builds return false.

## Control Flow, State, And Persistence
`apple_gmux_detect()` optionally finds the ACPI PNP device, checks I/O resources first, reads version bytes, probes indexed mode on invalid version bytes, otherwise tests MEM resources for MMIO by mapping 16 bytes and reading the command register. It temporarily references ACPI/PNP/device objects and releases them before return.

## Dependencies And Integration Points
Depends on ACPI, I/O port/MMIO helpers, PNP resources, and device references. Integrated by backlight, GPU switching, runtime PM, and Apple-specific quirk code.

## Risks And Test Signals
Detection performs real I/O; probing the wrong resource can have side effects. The disabled-config prototype for `apple_gmux_detect()` uses a different second-argument type than the enabled path, so callers must include under compatible expectations. Tests should cover PIO, indexed, and MMIO machines, false-positive ACPI devices, reference cleanup, backlight control, and no-gmux systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/apple-gmux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arch_topology.h -->
# sources/distributed-fs/ceph-client/include/linux/arch_topology.h

## Purpose
Declares generic architecture topology interfaces for CPU capacity, frequency invariance, hardware pressure, and CPU sibling masks.

## Important APIs, Types, And Functions
Exports capacity/frequency functions such as `topology_normalize_cpu_scale()`, `topology_parse_cpu_capacity()`, `topology_set_freq_scale()`, `topology_scale_freq_invariant()`, and `topology_scale_freq_tick()`. Per-CPU variables include `capacity_freq_ref`, `arch_freq_scale`, and `hw_pressure`, with inline getters. `enum scale_freq_source` and `struct scale_freq_data` describe frequency-scale providers. `struct cpu_topology` stores thread/core/cluster/package IDs and sibling masks. Under `CONFIG_GENERIC_ARCH_TOPOLOGY`, macros expose topology IDs/masks and functions manage CPU topology lifecycle.

## Control Flow, State, And Persistence
State is held in per-CPU scale/pressure values and, when enabled, the global `cpu_topology[NR_CPUS]` table. Control flow spans boot parsing, CPU hotplug storage/removal, frequency tick updates, and scheduler-facing topology queries.

## Dependencies And Integration Points
Depends on `linux/types.h`, `linux/percpu.h`, cpumasks, OF/ACPI topology parsing, cpufreq/CPPC/virtual frequency providers, and scheduler capacity code.

## Risks And Test Signals
Wrong sibling masks or stale frequency scale values can distort scheduler placement and capacity accounting. Tests should cover DT/ACPI parsing, CPU hotplug, SMT detection through `thread_id`, frequency invariance updates, hardware pressure updates, and config fallback where `topology_core_has_smt()` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arch_topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/args.h -->
# sources/distributed-fs/ceph-client/include/linux/args.h

## Purpose
Provides small preprocessor utilities for variadic argument counting and token concatenation.

## Important APIs, Types, And Functions
`COUNT_ARGS(X...)` counts variadic arguments up to 15 and yields the 16th argument if exceeded. `CONCATENATE(a, b)` expands arguments before token pasting through `__CONCAT`.

## Control Flow, State, And Persistence
This is compile-time macro logic only. It stores no runtime state and emits no code by itself.

## Dependencies And Integration Points
It is standalone within Linux headers. A visible integration point in this subset is `arm-smccc.h`, which uses `COUNT_ARGS()` and `CONCATENATE()` to dispatch variadic SMCCC invocation macros to the correct register declaration/constraint helpers.

## Risks And Test Signals
Miscounting beyond 15 arguments or using macro arguments with side effects in generated expansions can create hard-to-debug compile issues. Tests are preprocessor/build tests: variadic macro users should compile with zero through maximum supported arguments and fail clearly outside supported arity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm-cci.h -->
# sources/distributed-fs/ceph-client/include/linux/arm-cci.h

## Purpose
Declares Linux interfaces for ARM CCI cache-coherent interconnect probing and port control.

## Important APIs, Types, And Functions
`cci_probed()` reports whether CCI is available. With `CONFIG_ARM_CCI400_PORT_CTRL`, callers can get ACE ports from device tree nodes, disable a port by CPU MPIDR, or enable/disable ports by device node or index through `__cci_control_port_by_device()` and `__cci_control_port_by_index()`. Convenience macros map enable/disable names to the internal control functions. Stubs return `-ENODEV` when port control is disabled. `cci_enable_port_for_self()` is always declared.

## Control Flow, State, And Persistence
The header does not hold state. Implementations coordinate CCI port enable/disable around CPU/device coherency transitions. Stub control flow makes unsupported port control explicit to callers.

## Dependencies And Integration Points
Depends on `linux/errno.h`, `linux/types.h`, and `asm/arm-cci.h`. Integrated by ARM platform boot, CPU hotplug, power management, and device-tree based coherent-interconnect setup.

## Risks And Test Signals
Incorrect port control can break cache coherency. Tests should cover probe detection, device-tree ACE port lookup, CPU power transitions, unsupported-config error handling, and SMP coherency stress on CCI platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm-cci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm-smccc.h -->
# sources/distributed-fs/ceph-client/include/linux/arm-smccc.h

## Purpose
Defines ARM SMC Calling Convention IDs, return values, version/conduit helpers, KVM and standard service IDs, and inline/assembly-backed invocation APIs for SMC/HVC calls.

## Important APIs, Types, And Functions
The header builds function IDs with `ARM_SMCCC_CALL_VAL()` and extracts call properties with `ARM_SMCCC_IS_FAST_CALL()`, `ARM_SMCCC_IS_64()`, `ARM_SMCCC_FUNC_NUM()`, and `ARM_SMCCC_OWNER_NUM()`. It defines owner ranges, SMCCC versions 1.0-1.3, architecture feature/workaround IDs, KVM vendor hypervisor IDs for PTP, pKVM memory share/unshare, MMIO guard, implementation discovery, PV time calls, TRNG calls, and return codes. Runtime APIs include `arm_smccc_1_1_get_conduit()`, `arm_smccc_get_version()`, `arm_smccc_version_init()`, SoC ID getters, `arm_smccc_hypervisor_has_uuid()`, `smccc_res_to_uuid()`, `smccc_uuid_to_reg()`, low-level `__arm_smccc_smc()`/`__arm_smccc_hvc()`, v1.2 register calls on arm64, and variadic `arm_smccc_1_1_{smc,hvc,invoke}()` plus `arm_smccc_1_2_invoke()`.

## Control Flow, State, And Persistence
SMCCC call flow packages up to eight arguments into fixed registers for v1.1 or `a0..a17` for v1.2, issues `smc #0` or `hvc #0` based on conduit, and writes result registers back to caller-provided structures. If no conduit is valid, the invoke macros place `SMCCC_RET_NOT_SUPPORTED` in `a0`. Persistent state is the initialized SMCCC version/conduit maintained by architecture code, not by the header.

## Dependencies And Integration Points
Depends on `linux/args.h`, `linux/init.h`, `linux/uuid.h`, `linux/linkage.h`, `linux/types.h`, and architecture opcode definitions. Integrated by ARM/arm64 firmware, PSCI-like services, KVM guests/hosts, pKVM protected memory, TRNG, PV time, Spectre/erratum workarounds, and SoC ID discovery.

## Risks And Test Signals
Register constraints and variadic macro arity are sensitive; wrong argument count or width can corrupt firmware calls. Missing conduit handling must return not-supported rather than executing invalid instructions. Tests should cover SMC and HVC conduits, no-conduit fallback, UUID conversion, KVM feature probing, TRNG/PV time callers, arm64 v1.2 extended registers, and builds across ARM, ARM64, and non-SMCCC configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm-smccc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm_ffa.h -->
# sources/distributed-fs/ceph-client/include/linux/arm_ffa.h

## Purpose
Defines Arm Firmware Framework for Arm A-profile (FF-A) function IDs, error/version encoding, FF-A bus/driver structures, partition information, direct/indirect messaging payloads, memory-sharing descriptors, and operation tables.

## Important APIs, Types, And Functions
`FFA_SMC_32()`/`FFA_SMC_64()` build SMCCC function IDs for FF-A calls such as version/features, RX/TX map/unmap, partition info, direct messaging, memory donate/lend/share/retrieve/reclaim, notifications, secondary entry registration, memory permissions, console log, and direct request2/response2. `FFA_FN_NATIVE()` selects 64-bit or 32-bit IDs by kernel word size. `struct ffa_device`, `struct ffa_driver`, `struct ffa_device_id`, `ffa_register()`, `ffa_unregister()`, and `module_ffa_driver()` implement the FF-A bus contract. Memory structures include `ffa_mem_region_addr_range`, `ffa_composite_mem_region`, `ffa_mem_region_attributes`, `ffa_mem_region`, and `ffa_mem_ops_args`. Ops tables are split into `ffa_info_ops`, `ffa_msg_ops`, `ffa_mem_ops`, `ffa_cpu_ops`, `ffa_notifier_ops`, and aggregate `ffa_ops`.

## Control Flow, State, And Persistence
The transport registers discovered partitions as `ffa_device` instances. Drivers bind by UUID and call ops for version/partition info, direct or indirect messages, memory share/lend/reclaim, vCPU run, and notifications. Memory descriptor helper flow computes endpoint memory access descriptor sizes and offsets depending on FF-A version, preserving pre-1.1 and 1.2 layout differences.

## Dependencies And Integration Points
Depends on bitfield/device/module/types/uuid helpers and SMCCC constants from `arm-smccc.h`. Integrates with the ARM FF-A transport driver, secure partitions, hypervisors/SPM, scatterlists, Linux driver core, module registration, notifications, and memory-sharing users.

## Risks And Test Signals
Descriptor layout is version-sensitive: wrong EMAD size, offsets, handle packing, or native-width function choice can break secure memory transactions. Tests should cover FF-A 1.0/1.1/1.2 negotiation, 32-bit partition restrictions for direct request2, RX/TX buffer mapping, partition registration/unregistration, UUID binding, direct and indirect messages, memory share/lend/reclaim, notification callbacks, and stub returns without `CONFIG_ARM_FFA_TRANSPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm_ffa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm_mpam.h -->
# sources/distributed-fs/ceph-client/include/linux/arm_mpam.h

## Purpose
Declares Arm MPAM integration with Linux resctrl, ACPI MPAM parsing, MSC resource creation, requestor registration, and architecture hooks for closid/rmid scheduling and monitoring.

## Important APIs, Types, And Functions
`enum mpam_msc_iface` distinguishes MMIO and PCC MSC interfaces. `enum mpam_class_types` describes cache, memory, or unknown classes, with `MPAM_CLASS_ID_DEFAULT`. ACPI helpers `acpi_mpam_parse_resources()` and `acpi_mpam_count_msc()` are gated by `CONFIG_ACPI_MPAM`; `mpam_ris_create()` is gated by `CONFIG_ARM64_MPAM_DRIVER`. Resctrl architecture APIs include allocation/monitoring capability checks, CPU/task closid/rmid setters, scheduler hook `resctrl_arch_sched_in()`, match helpers, RMID index encode/decode, monitor context allocation/free, and no-op enable/disable helpers. `mpam_register_requestor()` lets requestors advertise PARTID/PMG limits.

## Control Flow, State, And Persistence
MPAM driver setup parses ACPI resources, creates RIS instances for MSCs, and registers requestor limits before user-visible resctrl sizes are finalized. Runtime scheduling writes CPU/requestor MPAM state when closid/rmid changes. Persistent state lives in MPAM MSC/resource objects and resctrl task/CPU assignments.

## Dependencies And Integration Points
Depends on ACPI MPAM structures, `linux/resctrl_types.h`, task structs, and resctrl resources/events. Integrates Arm64 MPAM driver, ACPI, resctrl filesystem, scheduler context switches, monitoring, and allocation control.

## Risks And Test Signals
Late requestor registration can conflict with values already advertised to userspace. Wrong RMID encoding or scheduling hooks can attribute monitoring data to the wrong control group. Tests should cover ACPI parsing failures, no-driver stubs returning `-EINVAL`, closid/rmid context switch behavior, resctrl alloc/mon capabilities, monitor context lifecycle, and requestor registration before/after exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm_mpam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm_sdei.h -->
# sources/distributed-fs/ceph-client/include/linux/arm_sdei.h

## Purpose
Declares Arm Software Delegated Exception Interface event registration, GHES integration, CPU masking, and architecture event-handler data structures.

## Important APIs, Types, And Functions
`sdei_event_callback` is the NMI-context callback type. APIs include `sdei_event_register()`, `sdei_event_unregister()`, `sdei_event_enable()`, `sdei_event_disable()`, `sdei_register_ghes()`, `sdei_unregister_ghes()`, `sdei_mask_local_cpu()`, `sdei_unmask_local_cpu()`, `acpi_sdei_init()`, `sdei_handler_abort()`, `sdei_event_handler()`, and `sdei_api_event_context()`. `struct sdei_registered_event` carries interrupted registers, callback, callback arg, event number, and priority.

## Control Flow, State, And Persistence
Firmware-described events are registered and enabled, then architecture entry code passes a `struct sdei_registered_event` back into `sdei_event_handler()` when an event arrives. Unregister can return `-EINPROGRESS` and must be retried. Registered events are driver-maintained state, with private events represented per CPU.

## Dependencies And Integration Points
Depends on UAPI SDEI definitions, ACPI GHES, and `asm/sdei.h` when enabled. Integrates firmware SDEI, GHES/RAS error handling, CPU hotplug/masking, NMI-context callbacks, and architecture exception entry.

## Risks And Test Signals
Callbacks run in NMI context, so sleeping, locking, or allocation mistakes are severe. Retry semantics for unregister are easy to miss. Tests should cover registration/enable/disable/unregister, GHES normal and critical callbacks, CPU mask/unmask, private per-CPU events, firmware absent stubs, and abort path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/arm_sdei.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/armada-37xx-rwtm-mailbox.h -->
# sources/distributed-fs/ceph-client/include/linux/armada-37xx-rwtm-mailbox.h

## Purpose
Defines message payload structures for the Armada 37xx rWTM BIU mailbox.

## Important APIs, Types, And Functions
`struct armada_37xx_rwtm_tx_msg` contains a 16-bit command and sixteen 32-bit arguments. `struct armada_37xx_rwtm_rx_msg` contains a 32-bit return value and sixteen 32-bit status words.

## Control Flow, State, And Persistence
The header stores no state. Mailbox client/provider code fills a TX message, sends it through the mailbox channel, and interprets the RX status returned by firmware.

## Dependencies And Integration Points
Depends on `linux/types.h`. Integrated by Armada 37xx firmware mailbox drivers and clients issuing commands to the rWTM.

## Risks And Test Signals
Struct layout and argument count must match firmware. Tests should validate command serialization, response status parsing, endian assumptions, oversized command rejection in implementation code, and timeout/error propagation from the mailbox framework.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/armada-37xx-rwtm-mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/array_size.h -->
# sources/distributed-fs/ceph-client/include/linux/array_size.h

## Purpose
Defines generic compile-time array sizing helpers.

## Important APIs, Types, And Functions
`ARRAY_SIZE(arr)` returns element count and adds `__must_be_array(arr)` to reject pointers. `ARRAY_END(arr)` returns a pointer one element past the final array entry.

## Control Flow, State, And Persistence
These are compile-time/runtime-expression macros without independent state. They typically fold to constants for true arrays.

## Dependencies And Integration Points
Depends on `linux/compiler.h` for `__must_be_array`. Integrated widely throughout kernel code for fixed-array bounds and iteration endpoints.

## Risks And Test Signals
The primary risk is passing pointer-like objects where an array is required; `__must_be_array` is the guard. Tests are compile-time: pointer misuse should fail, fixed arrays should compile, and flexible array members should not be mis-sized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/array_size.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ascii85.h -->
# sources/distributed-fs/ceph-client/include/linux/ascii85.h

## Purpose
Provides small inline helpers for ASCII85 length calculation and encoding of 32-bit words.

## Important APIs, Types, And Functions
`ASCII85_BUFSZ` is 6 bytes for five encoded characters plus terminator. `ascii85_encode_len(long len)` returns the number of 4-byte chunks rounded up. `ascii85_encode(u32 in, char *out)` returns `"z"` for a zero word or writes a five-character base-85 encoding plus NUL terminator into `out`.

## Control Flow, State, And Persistence
Encoding is stateless. For nonzero input, the loop fills output backward using modulo/divide by 85 and adds the ASCII offset `'!'`.

## Dependencies And Integration Points
Depends on `linux/math.h` for `DIV_ROUND_UP` and `linux/types.h` for `u32`. Used by kernel code that needs compact ASCII85 serialization.

## Risks And Test Signals
Callers must supply at least `ASCII85_BUFSZ` bytes for nonzero values and handle the zero special case returning a string literal rather than `out`. Tests should cover zero, maximum `u32`, round chunk length for unaligned byte counts, and buffer termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ascii85.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1.h -->
# sources/distributed-fs/ceph-client/include/linux/asn1.h

## Purpose
Defines common ASN.1 BER/DER/CER class, primitive/constructed, tag, and indefinite-length constants.

## Important APIs, Types, And Functions
`enum asn1_class` defines universal, application, context, and private classes plus `ASN1_CLASS_BITS`. `enum asn1_method` defines primitive and constructed plus `ASN1_CONS_BIT`. `enum asn1_tag` covers universal tags from EOC through BMP string and long-form tag. `ASN1_INDEFINITE_LENGTH` defines the BER indefinite-length marker.

## Control Flow, State, And Persistence
The header is declarative and stateless. Parsers and encoders use these constants to construct or interpret tag bytes and length encodings.

## Dependencies And Integration Points
No direct nonstandard dependencies. Integrated by the ASN.1 bytecode decoder, encoder, certificate/key parsers, and other DER/BER consumers.

## Risks And Test Signals
Wrong tag/class interpretation can cause parser acceptance or rejection bugs in security-sensitive data. Tests should cover primitive/constructed encoding, long tags, indefinite lengths, DER restrictions, and consumers such as X.509 or key parsers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1_ber_bytecode.h -->
# sources/distributed-fs/ceph-client/include/linux/asn1_ber_bytecode.h

## Purpose
Defines internal bytecode and action contracts for the kernel ASN.1 BER/DER/CER decoder state machine.

## Important APIs, Types, And Functions
`asn1_action_t` is the callback signature receiving context, header length for ANY, tag for ANY, value pointer, and value length. `struct asn1_decoder` points to a bytecode machine, its length, and an action table. `enum asn1_opcode` defines match, skip, act, jump, any, conditional, fail, complete, maybe-act, end sequence/set/of variants, and return opcodes with bit masks describing opcode families. Helper macros `_tag()`, `_tagn()`, `_jump_target()`, and `_action()` build bytecode operands.

## Control Flow, State, And Persistence
Decoder implementations interpret `machine` bytes, match tags in input data, optionally invoke action callbacks, jump for nested structures, and finish on complete/return opcodes. Runtime state lives in the decoder interpreter stack and caller context, not the header.

## Dependencies And Integration Points
Depends on `linux/asn1.h` and kernel `size_t` types. Integrated with generated ASN.1 grammars, `asn1_ber_decoder()`, crypto/key/certificate parsers, and DER validation code.

## Risks And Test Signals
Opcode values are part of the generated-decoder contract; reordering can break generated bytecode. Tests should run generated ASN.1 parsers against valid/invalid DER, exercise ANY actions, optional skip paths, nested SEQUENCE/SET OF endings, callback error propagation, and malformed length/tag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1_ber_bytecode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1_decoder.h -->
# sources/distributed-fs/ceph-client/include/linux/asn1_decoder.h

## Purpose
Declares the public ASN.1 BER decoder entry point.

## Important APIs, Types, And Functions
`asn1_ber_decoder(const struct asn1_decoder *decoder, void *context, const unsigned char *data, size_t datalen)` interprets a compiled ASN.1 decoder over an input buffer and caller-owned context.

## Control Flow, State, And Persistence
The decoder walks input bytes according to the provided bytecode and invokes action callbacks stored in `struct asn1_decoder`. State is transient for the decode call and caller-owned through `context`.

## Dependencies And Integration Points
Depends on `linux/asn1.h`, `linux/types.h`, and the forward-declared bytecode structure. Integrated by generated ASN.1 parser modules and security-sensitive parsers for keys, certificates, and signatures.

## Risks And Test Signals
Risks include accepting malformed BER/DER, out-of-bounds data reads, and callback context misuse. Tests should include fuzzed ASN.1 inputs, valid DER fixtures, truncated buffers, action callback failures, and grammar-specific parser validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1_encoder.h -->
# sources/distributed-fs/ceph-client/include/linux/asn1_encoder.h

## Purpose
Declares helpers for bounded ASN.1 DER-like encoding of integers, OIDs, tags, octet strings, sequences, and booleans.

## Important APIs, Types, And Functions
`asn1_oid_len(oid)` computes OID element count. Encoding helpers take a current output pointer and `end_data` bound and return the advanced pointer or an implementation-defined failure indication. APIs include `asn1_encode_integer()`, `asn1_encode_oid()`, `asn1_encode_tag()`, `asn1_encode_octet_string()`, `asn1_encode_sequence()`, and `asn1_encode_boolean()`.

## Control Flow, State, And Persistence
Encoding is caller-buffer based and stateless. Each helper appends one ASN.1 object to a bounded buffer and advances the caller's write cursor.

## Dependencies And Integration Points
Depends on types, ASN.1 constants, and ASN.1 bytecode definitions. Integrated by crypto/key code or protocol code needing kernel-generated ASN.1 blobs.

## Risks And Test Signals
Buffer-bound mistakes and nonminimal integer/OID encodings are the key risks. Tests should cover exact-fit buffers, overflow rejection, negative and positive integer encodings, boolean values, nested sequence length calculation, and OID edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/asn1_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/assoc_array.h -->
# sources/distributed-fs/ceph-client/include/linux/assoc_array.h

## Purpose
Declares the public generic associative-array API used for key-indexed object storage.

## Important APIs, Types, And Functions
With `CONFIG_ASSOCIATIVE_ARRAY`, `struct assoc_array` holds the root pointer and leaf count. `struct assoc_array_ops` supplies key chunk extraction, object key chunk extraction, object comparison, object difference, and object free callbacks. APIs include `assoc_array_init()`, `assoc_array_iterate()`, `assoc_array_find()`, `assoc_array_destroy()`, `assoc_array_insert()`, `assoc_array_insert_set_object()`, `assoc_array_delete()`, `assoc_array_clear()`, `assoc_array_apply_edit()`, `assoc_array_cancel_edit()`, and `assoc_array_gc()`.

## Control Flow, State, And Persistence
Edits are prepared as `struct assoc_array_edit` objects, then either applied or canceled. The array persists through its root pointer and leaf count. Insert/delete/clear/GC mutate the tree only when edits are applied, allowing preallocation and rollback.

## Dependencies And Integration Points
Depends on `linux/types.h` and the private implementation. Integrated by keyrings and other kernel subsystems needing RCU-friendly associative lookup over caller-defined keys.

## Risks And Test Signals
Callback consistency is critical: `get_key_chunk`, `compare_object`, and `diff_objects` must describe the same key space. Tests should cover insert/find/delete, duplicate insertion, edit cancellation, GC filtering, destroy freeing, iteration ordering expectations, and config-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/assoc_array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/assoc_array_priv.h -->
# sources/distributed-fs/ceph-client/include/linux/assoc_array_priv.h

## Purpose
Defines private node, shortcut, edit, and pointer-tagging internals for the generic associative-array implementation.

## Important APIs, Types, And Functions
Constants define a 16-way fanout, fan masks, level step, and key chunk masks. `struct assoc_array_node` stores back pointer, parent slot, 16 tagged slots, and branch leaf count. `struct assoc_array_shortcut` compresses shared key prefixes. `struct assoc_array_edit` carries preallocated metadata, excised subtrees, count adjustments, parent-slot updates, and pointer assignments. Tagged-pointer helpers distinguish leaf/meta, node/shortcut, strip tags, and create tagged leaf/node/shortcut pointers.

## Control Flow, State, And Persistence
The implementation navigates an N-way tree by key segments. Metadata pointers use low bits as tags, so nodes and shortcuts can be identified without dereferencing. Edits stage multiple structural mutations and count adjustments before committing to the persistent tree.

## Dependencies And Integration Points
Depends on `linux/assoc_array.h` and `CONFIG_ASSOCIATIVE_ARRAY`. Integrated only by the associative-array implementation; public consumers should not rely on these internals.

## Risks And Test Signals
Pointer tagging assumes alignment leaves low bits free. Incorrect tag stripping or shortcut level math can corrupt the tree. Tests should stress shared-prefix keys, branch splits, shortcut insertion/removal, RCU freeing, GC excision, and sanitizer coverage for misaligned or stale pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/assoc_array_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/async.h -->
# sources/distributed-fs/ceph-client/include/linux/async.h

## Purpose
Declares the kernel asynchronous function-call framework used mainly to improve boot/probe parallelism.

## Important APIs, Types, And Functions
`async_cookie_t` is a 64-bit sequencing cookie. `async_func_t` is the async callback signature. `struct async_domain` tracks pending work and whether the domain participates in global synchronization. `ASYNC_DOMAIN()` and `ASYNC_DOMAIN_EXCLUSIVE()` initialize registered or exclusive domains. Scheduling APIs include `async_schedule_node()`, `async_schedule_node_domain()`, inline `async_schedule()`, `async_schedule_domain()`, `async_schedule_dev()`, `async_schedule_dev_nocall()`, and `async_schedule_dev_domain()`. Synchronization APIs include `async_synchronize_full()`, `async_synchronize_full_domain()`, `async_synchronize_cookie()`, `async_synchronize_cookie_domain()`, `current_is_async()`, and `async_init()`.

## Control Flow, State, And Persistence
Scheduling queues a function and returns a cookie used as a synchronization checkpoint. Domain state is a pending list plus registration flag. Device variants choose a NUMA node from the device. Exclusive domains can go out of scope after their own pending work finishes and do not participate in global full synchronization.

## Dependencies And Integration Points
Depends on list, NUMA, device, and type helpers. Integrated by driver core and subsystem init/probe code that can run independent setup asynchronously.

## Risks And Test Signals
Async callbacks must not outlive data or domain lifetime. Missing synchronization before freeing resources can cause use-after-free. Tests should cover global and domain-specific waits, cookie ordering, device NUMA scheduling, exclusive-domain lifetime, atomic-context scheduling, and `current_is_async()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/async.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/async_tx.h -->
# sources/distributed-fs/ceph-client/include/linux/async_tx.h

## Purpose
Declares the async_tx DMA offload framework for memory copy, XOR, RAID6 syndrome generation/validation, recovery, and callback chaining.

## Important APIs, Types, And Functions
`struct dma_chan_ref` tracks DMA channels in the async pool. `enum async_tx_flags` controls zero/drop destination behavior, immediate ACK, dependency fences, and PQ XOR destination behavior. `struct async_submit_ctl` carries flags, dependency descriptor, callback, callback parameter, and scribble space. Channel functions include `async_tx_issue_pending_all()`, `async_tx_issue_pending()`, and `async_tx_find_channel()`, with DMA-engine/config stubs when unavailable. Helpers include `async_tx_sync_epilog()`, `addr_conv_t`, `init_async_submit()`, `async_tx_submit()`, and operations `async_xor()`, `async_xor_offs()`, `async_xor_val_offs()`, `async_memcpy()`, `async_trigger_callback()`, `async_gen_syndrome()`, `async_syndrome_val()`, `async_raid6_2data_recov()`, `async_raid6_datap_recov()`, and `async_tx_quiesce()`.

## Control Flow, State, And Persistence
Operations choose a DMA channel when available and fall back to synchronous execution otherwise. Dependency descriptors chain operations; `ASYNC_TX_FENCE` marks data dependencies, and callbacks run at completion or immediately in synchronous fallback. Channel refs are RCU/list/atomic-count managed by the core.

## Dependencies And Integration Points
Depends on dmaengine, spinlocks, interrupts, pages, and optional architecture channel selection. Integrated by RAID, MD, lib/raid6, storage, and memory offload users.

## Risks And Test Signals
The async/sync semantic split is risky: flags such as `ASYNC_TX_XOR_ZERO_DST` and `ASYNC_TX_XOR_DROP_DST` differ between paths. Tests should cover DMA and no-DMA configs, dependency chains, callback order, issue-pending behavior, RAID6 recovery correctness, channel switching, and quiesce waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/async_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ata.h -->
# sources/distributed-fs/ceph-client/include/linux/ata.h

## Purpose
Defines core ATA/ATAPI/SATA constants, command values, register/status bits, IDENTIFY word offsets, feature-detection helpers, transfer-limit helpers, and port multiplier helpers for libata and related drivers.

## Important APIs, Types, And Functions
The large enum covers global limits, IDENTIFY DEVICE word indexes, PIO/SWDMA/MWDMA/UDMA masks, PRD/DMA constants, command-block bits, ATA/ATAPI commands, NCQ subcommands, log pages, SET FEATURES values, SMART, DSM/TRIM, ATAPI packet flags, SATA PMP registers, cable types, SCR indexes, and SError bits. `enum ata_prot_flags` describes taskfile protocol types. `struct ata_bmdma_prd` defines BMDMA PRD entries. Inline helpers inspect IDENTIFY data for LBA, DMA, NCQ, FUA, flush, LBA48, HPA, write cache, power management, read-log DMA, sense reporting, SCT features, ATA version, SATA, TPM/trusted, unload, WWN, form factor, rotation, NCQ capabilities, TRIM/zero-after-trim, CHS validity, CFA, SSD, zoned capability, IORDY, cable type, ATAPI CDB length, command packet set, DMADIR, status OK, LBA28/LBA48 bounds, and PMP GSCR fields.

## Control Flow, State, And Persistence
The header is stateless but encodes many validation flows as inline helpers. Most helpers first check version/validity marker bits before trusting IDENTIFY words. LBA helpers enforce hardware sector-count and address limits. Protocol enum values let libata select PIO, DMA, NCQ, or ATAPI handling.

## Dependencies And Integration Points
Depends on `linux/bits.h`, `linux/string.h`, and fixed-width types. Integrated by libata core, host drivers, SCSI translation, disk feature detection, NCQ, zoned ATA, power management, SMART/security/trusted command paths, and SATA port multipliers.

## Risks And Test Signals
This is a hardware ABI header: wrong constants can cause data loss. Subtle risks include trusting invalid IDENTIFY words, off-by-one LBA limits, 40-wire cable misdetection, and NCQ/log feature misclassification. Tests should cover representative IDENTIFY fixtures, old ATA versions, SATA vs PATA, LBA28/LBA48 boundary values, TRIM and zero-after-trim detection, flush/FUA/wcache flags, zoned capability, ATAPI packet lengths, and real or emulated libata probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ata_platform.h -->
# sources/distributed-fs/ceph-client/include/linux/ata_platform.h

## Purpose
Declares platform data and probe helper contracts for platform PATA/SATA drivers.

## Important APIs, Types, And Functions
`struct pata_platform_info` contains `ioport_shift` for nonstandard register spacing. `__pata_platform_probe()` accepts device, I/O/control/IRQ resources, ioport shift, PIO mask, SCSI host template, and 16-bit access flag. `struct mv_sata_platform_data` carries a Marvell SATA port count.

## Control Flow, State, And Persistence
The header does not implement control flow. Probe implementations use the declared helper to map resources, initialize libata host structures, and register ports. Platform data persists for device lifetime.

## Dependencies And Integration Points
Uses forward declarations for `struct device`, `struct resource`, and `struct scsi_host_template` from included contexts. Integrates platform bus resources, PATA platform driver, Marvell SATA platform data, libata, and SCSI host registration.

## Risks And Test Signals
Incorrect resource ordering or `ioport_shift` causes register misaddressing. Tests should cover platform probe with shifted I/O ports, IRQ absence/error paths, 16-bit access devices, PIO mask enforcement, and Marvell port-count handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ata_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atalk.h -->
# sources/distributed-fs/ceph-client/include/linux/atalk.h

## Purpose
Defines internal AppleTalk protocol structures, DDP/AARP headers, route/interface/socket state, exported global tables, and subsystem init/cleanup hooks.

## Important APIs, Types, And Functions
Structures include `atalk_route`, `atalk_iface`, `atalk_sock`, `ddpehdr`, `elapaarp`, and `aarp_iter_state`. Inline helpers convert `struct sock` to `atalk_sock` and locate DDP/AARP headers in skb transport data. Constants define AARP timing, hash size, retransmit limit, interface probe flags, and AARP operation codes. Exports include datalink protocols, route/interface/socket lists and locks, default route, AARP init/send/probe/proxy/remove/cleanup functions, address and route lookups, sysctl/proc init/exit with config stubs, and `aarp_seq_ops`.

## Control Flow, State, And Persistence
AppleTalk keeps global route, interface, and socket lists protected by rwlocks. Interfaces can be probing or failed. AARP maintains resolution state and timers. DDP send flow resolves hardware addresses via AARP before transmitting. Proc/sysctl registration is optional by config.

## Dependencies And Integration Points
Depends on network socket/skbuff/device types, Ethernet address length, and UAPI AppleTalk definitions. Integrates the AppleTalk socket family, datalink layer, AARP, procfs, sysctl, and net devices via `dev->atalk_ptr`.

## Risks And Test Signals
Global list locking, device removal, and AARP timeout handling are the key risks. Tests should cover interface bring-up/down, address probe collision, AARP resolution and retransmit limit, route lookup/default route, socket list iteration, proc/sysctl availability, and build behavior without CONFIG_ATALK where only selected helpers exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atalk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atm.h -->
# sources/distributed-fs/ceph-client/include/linux/atm.h

## Purpose
Provides kernel-side inclusion of general ATM UAPI declarations and a compat ioctl structure.

## Important APIs, Types, And Functions
The header includes `uapi/linux/atm.h`. With `CONFIG_COMPAT`, `struct compat_atmif_sioc` mirrors ATM interface ioctl arguments using a compat user pointer.

## Control Flow, State, And Persistence
No runtime control flow or state is defined. It exists as a type bridge for ATM kernel code and compat ioctl handling.

## Dependencies And Integration Points
Depends on UAPI ATM definitions and `linux/compat.h` when compat is enabled. Integrated by ATM sockets, ATM device ioctl handlers, and 32-bit userspace compatibility on 64-bit kernels.

## Risks And Test Signals
Compat layout mismatches can break 32-bit ATM tools. Tests should cover native and compat ioctl argument translation, build coverage with/without `CONFIG_COMPAT`, and UAPI inclusion stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atm_tcp.h -->
# sources/distributed-fs/ceph-client/include/linux/atm_tcp.h

## Purpose
Declares driver-specific operations for the ATMTCP virtual ATM driver.

## Important APIs, Types, And Functions
`struct atm_tcp_ops` provides `attach()`, `create_persistent()`, `remove_persistent()`, and module owner fields. The global `atm_tcp_ops` is exported for driver-specific utilities and users. It also imports the UAPI ATMTCP definitions.

## Control Flow, State, And Persistence
The global ops table routes attach and persistent-interface management to the active ATMTCP implementation. Persistent interface state is owned by that driver, not by the header.

## Dependencies And Integration Points
Depends on UAPI ATMTCP definitions and forward-declared `atm_vcc` and `module`. Integrates with ATM VCC setup, ATMTCP driver module ownership, and management utilities.

## Risks And Test Signals
An uninitialized or stale ops table can route calls into absent modules. Tests should cover attach failure, persistent interface create/remove, module reference ownership, and UAPI command compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atm_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmdev.h -->
# sources/distributed-fs/ceph-client/include/linux/atmdev.h

## Purpose
Defines core in-kernel ATM device and VCC structures, statistics, operations, socket accounting helpers, registration APIs, ioctl hooks, and notifier hooks.

## Important APIs, Types, And Functions
Statistics structures use atomic counters for AAL stats. VCC flags enumerate address, ready, partial, registered, bound, released, listen, meta, session, SAP, close, waiting, and CLIP states; `ATM_VF2VS()` maps flags to visible socket state. `struct atm_vcc` embeds `struct sock` first and stores VPI/VCI, options, device, QoS/SAP, callbacks (`push`, `pop`, `push_oam`, `send`, release), protocol/device data, stats, SVC addresses, session pointer, and user backlink. `struct atm_dev` stores ops, PHY ops, type/number, data, flags, address lists, ESI, CI range, stats, signal, link rate, refcount, lock, proc entry, class device, and list linkage. `struct atmdev_ops` and `struct atmphy_ops` declare driver callbacks. APIs include device register/lookup/deregister, signal change, VCC release, socket insertion, charging/allocation, PCR goal, async release, ioctl register/deregister, and device notifier register/unregister. Inline helpers convert socket types, account TX/RX memory, test send allowance, and hold/put devices.

## Control Flow, State, And Persistence
ATM runtime state is substantial: global VCC hash table and socket list lock, per-device refcounts and lists, per-VCC flags and callbacks, and socket memory accounting. `atm_dev_put()` closes devices only after removal is flagged and refcount reaches zero. TX accounting stores the skb truesize at charge time in `ATM_SKB(skb)` so later skb expansion does not corrupt accounting.

## Dependencies And Integration Points
Depends on wait queues, time, net/socket/skbuff/uio, atomic/refcount, UAPI ATM device definitions, procfs, and compat. Integrated by ATM core, device drivers, PHY drivers, CLIP/br2684, proc/sysfs, ioctl extension modules, and network notifier clients.

## Risks And Test Signals
Risks include refcount bugs, skb accounting imbalance, callback lifetime/module ownership, VCC flag races, and device removal while VCCs remain. Tests should cover device register/deregister, VCC open/close/send, signal notifier events, TX/RX accounting under skb resizing, ioctl extension handling, compat ioctls, proc entries, and refcount release assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmel-isc-media.h -->
# sources/distributed-fs/ceph-client/include/linux/atmel-isc-media.h

## Purpose
Defines custom V4L2 control IDs for Microchip/Atmel ISC white-balance gain and offset controls.

## Important APIs, Types, And Functions
`enum atmel_isc_ctrl_id` allocates four gain controls for R, B, GR, and GB Bayer components and four offset controls for the same components starting at `V4L2_CID_USER_ATMEL_ISC_BASE`.

## Control Flow, State, And Persistence
The comments describe control semantics: auto white balance clusters the controls, AWB-on makes manual controls inactive but volatile/readable, AWB-off allows manual gain/offset, and a one-shot white-balance action can update coefficients. The header itself only assigns IDs; control state lives in the ISC V4L2 driver.

## Dependencies And Integration Points
Requires V4L2 control base definitions in including code. Integrated by the Atmel ISC media driver and userspace V4L2 control APIs.

## Risks And Test Signals
Control ID mismatch breaks userspace ABI. Tests should verify V4L2 control enumeration, AWB auto/manual cluster behavior, volatile reads, one-shot white balance update, value ranges/formats, and persistence of saved coefficients across driver reload where userspace restores them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmel-isc-media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmel-ssc.h -->
# sources/distributed-fs/ceph-client/include/linux/atmel-ssc.h

## Purpose
Defines platform data, shared device structure, request/free API, register offsets, bitfield constants, PDC offsets, and access macros for Atmel Synchronous Serial Controller devices.

## Important APIs, Types, And Functions
`struct atmel_ssc_platform_data` describes DMA usage and extended frame-sync length support. `struct ssc_device` stores list linkage, physical base, mapped registers, platform device, platform data, clock, user count, IRQ, RK-pin clock flag, and sound DAI flag. APIs are `ssc_request()` and `ssc_free()`. Register definitions cover control, clock mode, RX/TX clock/frame modes, hold/sync/compare registers, status, interrupt enable/disable/mask, and PDC pointer/counter/control/status registers. Bitfield helpers `SSC_BIT()`, `SSC_BF()`, `SSC_BFEXT()`, and `SSC_BFINS()` construct/extract/insert fields. `ssc_readl()` and `ssc_writel()` perform raw MMIO access by symbolic register name.

## Control Flow, State, And Persistence
SSC users request a shared controller, configure clock/frame registers, enable RX/TX, manage interrupts or PDC DMA, and free the controller when done. Device state includes MMIO register contents, clock enablement managed by implementations, and the `user` count in `struct ssc_device`.

## Dependencies And Integration Points
Depends on platform devices, lists, I/O helpers, clocks, DMA addresses, and Atmel platform data. Integrated by audio/I2S/PCM drivers, SPI-like synchronous serial users, PDC DMA, and Atmel SoC platform code.

## Risks And Test Signals
Raw MMIO macros do not enforce ordering or field range beyond masks. Wrong `has_fslen_ext` handling can program frame lengths incorrectly on older SoCs. Tests should cover request/free exclusivity, register field construction, RX/TX enable/disable, interrupt bits, PDC transfer setup, clock selection, DMA vs non-DMA operation, and audio DAI probe/use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmel-ssc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmel_pdc.h -->
# sources/distributed-fs/ceph-client/include/linux/atmel_pdc.h

## Purpose
Defines common Atmel Peripheral Data Controller register offsets and transfer-control bits.

## Important APIs, Types, And Functions
Offsets cover receive/transmit current and next pointer/counter registers (`ATMEL_PDC_RPR`, `RCR`, `TPR`, `TCR`, `RNPR`, `RNCR`, `TNPR`, `TNCR`), transfer control/status (`ATMEL_PDC_PTCR`, `ATMEL_PDC_PTSR`), enable/disable bits for RX/TX, and `ATMEL_PDC_SCND_BUF_OFF` for first-to-second buffer spacing.

## Control Flow, State, And Persistence
The header is declarative. Drivers program pointer/counter pairs, enable transfer with `RXTEN`/`TXTEN`, disable with `RXTDIS`/`TXTDIS`, and inspect status. Runtime state is the peripheral's PDC register set.

## Dependencies And Integration Points
No direct includes beyond constants. Integrated by Atmel peripheral drivers that share the PDC layout, including SSC and serial-like devices.

## Risks And Test Signals
Wrong pointer/counter programming can DMA from/to invalid memory. Tests should cover RX/TX enable-disable sequences, next-buffer handoff, zero-count behavior, interrupt completion in consuming drivers, and consistency with peripheral-specific PDC offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atmel_pdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atomic.h -->
# sources/distributed-fs/ceph-client/include/linux/atomic.h

## Purpose
Defines machine-independent atomic operation wrappers, conditional atomic reads, and generic acquire/release/full-fence construction around architecture relaxed atomics.

## Important APIs, Types, And Functions
Includes architecture `asm/atomic.h` and barrier definitions. `atomic_cond_read_acquire()`, `atomic_cond_read_relaxed()`, and 64-bit equivalents use conditional load primitives. Fence hook macros default to `smp_mb__after_atomic` or `smp_mb__before_atomic` unless the architecture overrides them. `__atomic_op_acquire()`, `__atomic_op_release()`, and `__atomic_op_fence()` wrap relaxed operations with acquire, release, or full ordering. It then includes generated/fallback, atomic-long, and instrumented atomic headers.

## Control Flow, State, And Persistence
The header layers memory-order semantics over architecture operations. Atomic state lives in `atomic_t`/`atomic64_t` objects supplied by callers. Acquire wrappers fence after relaxed load-modify operations; release wrappers fence before; full wrappers fence before and after.

## Dependencies And Integration Points
Depends on `linux/types.h`, architecture atomic/barrier headers, and Linux generated atomic fallback/instrumentation headers. Integrated everywhere kernel code uses atomics, refcounts, locks, wait loops, and memory-order-sensitive synchronization.

## Risks And Test Signals
Memory-ordering mistakes can be architecture-specific and intermittent. Tests should include LKMM litmus coverage, KCSAN/race detection, build coverage for architectures with and without overrides, atomic64 availability, instrumented atomic behavior, and users of conditional reads waiting for state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/atomic.h -->
