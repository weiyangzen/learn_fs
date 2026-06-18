## sources/distributed-fs/ceph-client/include/linux/mfd/bcm2835-pm.h

Purpose: This minimal header defines shared state for the Raspberry Pi/Broadcom BCM2835-family power-management MFD driver.

Important APIs, types, and constants: `enum bcm2835_soc` distinguishes BCM2835, BCM2711, and BCM2712 integration variants. `struct bcm2835_pm` stores the parent device, mapped PM register base, ASB base, RP1/video ASB base, and selected SoC type. The header includes `linux/regmap.h`, although this struct itself uses raw `void __iomem *` mappings rather than a regmap pointer.

Control flow: No functions are declared. Runtime flow is in the MFD/platform driver: map MMIO regions, select SoC variant, populate `struct bcm2835_pm`, and register child functions that use the base pointers.

State and persistence: State is MMIO hardware register state plus runtime mapping pointers. No persistent kernel data is defined.

Dependencies and integration points: Integrates with platform/MMIO resource mapping, Raspberry Pi PM domains, reset/power subdrivers, and SoC variant handling.

Risks: Different SoCs have different ASB/RPIVID address availability; consumers must check the selected `soc` and valid mapped bases. Raw MMIO access requires correct barriers and register definitions elsewhere.

Test signals: Probe on each compatible SoC, validate resource mapping success, confirm child drivers only access available ASB blocks, and exercise power/reset domains that rely on the shared PM object.
