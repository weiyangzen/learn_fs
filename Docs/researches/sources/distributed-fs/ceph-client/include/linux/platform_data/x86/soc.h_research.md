# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h

## Purpose
`soc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing macros, constants, or
function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_SOC_H`, `SOC_INTEL_IS_CPU`. Types: none visible in this
header. Declared or inline functions: `SOC_INTEL_IS_CPU`, `soc`, `soc_intel_is_byt`,
`soc_intel_is_cht`, `soc_intel_is_apl`, `soc_intel_is_glk`, `soc_intel_is_cml`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/sound/soc/sof/sof-pci-dev.c`, `sources/distributed-fs/ceph-
client/sound/soc/intel/boards/bytcr_wm5102.c`, `sources/distributed-fs/ceph-
client/sound/soc/intel/common/soc-intel-quirks.h`, `sources/distributed-fs/ceph-
client/sound/soc/intel/avs/boards/da7219.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `linux/mod_devicetable.h`, `asm/cpu_device_id.h`. Direct source-tree
consumers found by include search are `sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-
dev.c`, `sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_wm5102.c`,
`sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-intel-quirks.h`,
`sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/da7219.c`, `sources/distributed-
fs/ceph-client/drivers/mmc/host/sdhci-acpi.c`, `sources/distributed-fs/ceph-
client/drivers/mfd/intel_soc_pmic_crc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int0002_vgpio.c`, `sources/distributed-fs/ceph-
client/drivers/input/misc/axp20x-pek.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h` completely for this pass (70 lines, 1358 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h_research.md`.
