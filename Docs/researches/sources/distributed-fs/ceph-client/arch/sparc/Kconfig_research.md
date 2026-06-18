<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sparc/Kconfig

## Purpose
This is the main SPARC architecture configuration file. It defines 32-bit versus 64-bit SPARC selection, architecture capabilities, CPU/SMP/memory options, boot command-line defaults, LEON/U-Boot support, bus options, PCI variants, compatibility mode, and compiler user flags.

## Important APIs, Types, and Functions
Key symbols are `64BIT`, `SPARC`, `SPARC32`, `SPARC64`, `MMU`, `HIGHMEM`, `PGTABLE_LEVELS`, `SMP`, `NR_CPUS`, `EMULATED_CMPXCHG`, `EARLYFB`, `HOTPLUG_CPU`, `US3_MC`, `NUMA`, `ARCH_FORCE_MAX_ORDER`, `CMDLINE_BOOL`, `CMDLINE`, `SUN_PM`, `SPARC_LED`, `SERIAL_CONSOLE`, `SPARC_LEON`, U-Boot address symbols, `SBUS`, `SUN_LDOMS`, `PCIC_PCI`, `LEON_PCI`, `SPARC_GRPCI1/2`, `SUN_OPENPROMFS`, `SPARC64_PCI`, `SPARC64_PCI_MSI`, `COMPAT`, `ARCH_CC_CAN_LINK`, and `ARCH_USERFLAGS`. It also selects many generic kernel capabilities used by common code.

## Control Flow
The `64BIT` choice derives from `ARCH=sparc64` by default, then `SPARC32` and `SPARC64` def_bool branches select their capability sets. Menus expose processor, memory, LEON boot, and bus options. Several symbols are internal helper gates for Makefiles rather than user-facing features.

## State and Persistence Behavior
The file persists selected build configuration in `.config`. Runtime behavior changes through compiled-in options: page size, SMP limits, PCI/LDOM support, compatibility ABI, power management, serial console defaults, and boot command line.

## Dependencies and Integration Points
It integrates with generic Kconfig files (`kernel/Kconfig.hz`, `kernel/power/Kconfig`, `drivers/cpufreq/Kconfig`, `drivers/sbus/char/Kconfig`) and feeds SPARC Makefiles, MM code, boot code, PCI, SBUS, crypto, vDSO, tracing, audit, perf, and compatibility subsystems.

## Risks
Capability selections are broad and cross-cutting. Incorrect 32/64-bit gating can produce incompatible compiler flags, page-table layout, or ABI exposure. `CMDLINE` can override PROM bootargs, and `EMULATED_CMPXCHG` on SPARC32 is explicitly not fully atomic, so lock-free assumptions are risky there.

## Test Signals
Run `olddefconfig` and build SPARC32, SPARC64, SMP, NUMA, LEON, PCI, and COMPAT configurations. Verify compiler flag tests for `ARCH_CC_CAN_LINK`, generated `.config` selections, boot logs for selected buses, and 32-bit user compatibility on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kconfig -->
