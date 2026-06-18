# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h

## Purpose
`intel_scu_ipc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct intel_scu_ipc_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_X86_INTEL_SCU_IPC_H_`, `intel_scu_ipc_register`,
`devm_intel_scu_ipc_register`. Types: `struct intel_scu_ipc_data`. Declared or inline functions:
`intel_scu_ipc_unregister`, `intel_scu_ipc_dev_put`, `intel_scu_ipc_dev_command`. Important struct
details: struct intel_scu_ipc_data fields include `struct resource mem`, `int irq`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/x86/platform/intel-mid/intel-mid.c`, `sources/distributed-fs/ceph-
client/arch/x86/include/asm/intel_telemetry.h`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_ipc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_ipcutil.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/init.h`, `linux/ioport.h`, `linux/types.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c`,
`sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h`, `sources/distributed-
fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_ipcutil.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_pcidrv.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_pltdrv.c`, `sources/distributed-fs/ceph-
client/drivers/mfd/intel_soc_pmic_mrfld.c`, `sources/distributed-fs/ceph-
client/drivers/mfd/intel_pmc_bxt.c`. It integrates through `struct platform_device` platform data,
board files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace
parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h` completely for this pass (72 lines, 2310 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h_research.md`.
