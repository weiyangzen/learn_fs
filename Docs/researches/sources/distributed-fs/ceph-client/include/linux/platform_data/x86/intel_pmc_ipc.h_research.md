# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h

## Purpose
`intel_pmc_ipc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pmc_ipc_cmd` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `INTEL_PMC_IPC_H`, `IPC_SOC_REGISTER_ACCESS`, `IPC_SOC_SUB_CMD_READ`,
`IPC_SOC_SUB_CMD_WRITE`, `PMC_IPCS_PARAM_COUNT`, `VALID_IPC_RESPONSE`. Types: `struct pmc_ipc_cmd`,
`struct pmc_ipc_rbuf`. Declared or inline functions: `intel_pmc_ipc`. Important struct details:
struct pmc_ipc_cmd fields include `u32 cmd`, `u32 sub_cmd`, `u32 size`, `u32 wbuf[4]`; struct
pmc_ipc_rbuf fields include `u32 buf[4]`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/acpi.h`, `linux/cleanup.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c`. It
integrates through `struct platform_device` platform data, board files, MFD child registration, and
legacy non-DT setup paths; many modern systems may replace parts of this contract with Device Tree,
ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h` completely for this pass (98 lines, 2418 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h_research.md`.
