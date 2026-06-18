# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/setup.c

Purpose: defines the PowerMac machine descriptor and early platform setup. It detects PowerMac compatibility, initializes chipset features, NVRAM, interrupt and PCI callbacks, CPU/cache settings, default root selection, restart/poweroff paths, OF platform devices, and `/proc/cpuinfo` reporting.

Important APIs/types/functions: important symbols include `pmac_newworld`, exported `sys_ctrler`, `pmac_show_cpuinfo`, fallback `find_via_cuda`, `find_via_pmu`, `smu_init`, `pmac_setup_arch`, `pmac_late_init`, `note_bootable_part`, `pmac_restart`, `pmac_power_off`, `pmac_halt`, `pmac_init`, `pmac_declare_of_platform_devices`, `check_pmac_serial_console`, `pmac_probe`, and `define_machine(powermac)`.

Control flow: `pmac_probe` checks OF compatibility, sets DMA mode constants on 32-bit, installs `pm_power_off`, and calls `pmac_init`. `pmac_init` optionally enables early debug, runs `pmac_feature_init`, initializes udbg backends, performs DART early setup on PPC64, and sets up SMP early. `pmac_setup_arch` computes provisional `loops_per_jiffy`, detects NewWorld by interrupt-controller presence, initializes OHare/L2 cache on PPC32, probes CUDA/PMU/SMU, initializes NVRAM, selects a default root device on PPC32, and honors `adb_sync`. The machine descriptor then wires setup, PCI discovery, IRQ init, time, RTC, restart, halt, feature calls, and platform-specific PCI post-init hooks into the PowerPC core.

State and persistence: tracks `has_l2cache`, `pmac_newworld`, `current_root_goodness`, and `initializing`. `note_bootable_part` mutates `ROOT_DEV` only during initialization and only if the command line lacks `root=`. Power-off/restart state is delegated to CUDA, PMU, or SMU controllers. No file-backed persistence is performed here.

Dependencies/integration: depends on OF tree queries, `pmac_feature_init`, NVRAM, PCI, PIC, time/RTC code, ADB CUDA/PMU/SMU subsystems, btext/udbg console code, IOMMU/DART, SMP setup, and Linux machine descriptor registration.

Risks: setup order is critical: feature probing precedes PCI and IRQ setup, SMP runs before interrupt stack allocation, and NVRAM setup depends on controller detection. Fallback stubs for disabled CUDA/PMU/SMU only warn or no-op, so unsupported kernels may hang on restart/poweroff. `note_bootable_part` can change root selection based on device discovery order and goodness while initialization is still true.

Test signals: boot detection for `Power Macintosh` and `MacRISC`; NewWorld vs OldWorld detection; `/proc/cpuinfo` fields; root-device override behavior with and without `root=`; CUDA, PMU, and SMU restart/poweroff paths; early serial console selection from `linux,stdout-path`; OF platform-device creation for video, SMU, and fan controller nodes; build/boot across PPC32/PPC64 and SMP variants.
