# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_hsspi.h

**Purpose:** Declares registration for the BCM63xx high-speed SPI controller.

**Important APIs/types/functions:** Exports `bcm63xx_hsspi_register()` and includes `<linux/types.h>`.

**Control flow:** Board/device setup calls the registration helper when the active SoC has an HSSPI register set and IRQ.

**State and persistence behavior:** No local state. The implementation registers platform-device resources for HSSPI hardware.

**Dependencies and integration points:** Depends on CPU register-set/IRQ tables, SPI core, flash/device board data, and HSSPI-capable SoCs such as BCM6328/6362.

**Risks:** Calling registration on a SoC with `0xdeadbeef` HSSPI base or zero IRQ would create invalid resources. HSSPI and legacy SPI support must be selected correctly.

**Test signals:** Boot HSSPI-capable boards, verify SPI controller probe, flash/peripheral enumeration, transfer speed, IRQ handling, and absence on unsupported SoCs.
