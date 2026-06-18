# sources/distributed-fs/ceph-client/arch/x86/kernel/early-quirks.c

## Purpose
Applies very early PCI/chipset workarounds before the normal PCI subsystem and timers are available.

## Important APIs, Types, And Functions
`early_quirks()` starts bus scanning. `check_dev_quirk()` matches devices against `early_qrk`. Quirk handlers adjust HyperTransport APIC broadcast, VIA GART IOMMU policy, NVIDIA/ATI timer overrides, Intel IRQ remapping brokenness, Intel graphics stolen memory reservation, Baytrail HPET disablement, and Apple AirPort reset. `intel_graphics_stolen_res` exports reserved graphics memory.

## Control Flow
If early PCI config access is allowed, bus 0 is scanned slot/function by slot/function, recursing into PCI bridges. For each device, config space class/vendor/device are compared to quirk entries; apply-once entries set flags. Intel graphics matching uses a large device-ID table with per-generation stolen-memory base/size callbacks, then reserves the stolen range in E820.

## State, Persistence, And Dependencies
State changes include PCI config writes, ACPI timer override flags, IOMMU disable flags, IRQ remapping broken state, `boot_hpet_disable`, E820 reserved ranges, exported graphics stolen resource, and device reset side effects. It depends on direct PCI config access, E820, APIC/IO-APIC/HPET, GART, irq remapping, early ioremap, DRM Intel PCI IDs, and Apple platform detection.

## Integration Points
Runs before normal PCI quirks to protect timers, interrupts, IOMMU, graphics stolen memory, and problematic devices during early boot.

## Risks
Direct PCI probing can touch fragile devices, so matching and single-function handling matter. Stolen-memory calculations are generation-specific. Reserving wrong E820 ranges can hide usable RAM or expose stolen RAM to MMIO.

## Test Signals
Affected chipsets should log expected quirks, avoid timer override regressions, reserve Intel graphics stolen memory, disable unreliable HPET, mark broken IRQ remapping, and leave normal PCI enumeration intact.
