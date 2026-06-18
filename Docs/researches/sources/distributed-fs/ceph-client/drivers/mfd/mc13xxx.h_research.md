# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx.h

Purpose: Private header shared by the MC13xxx core and bus drivers. It defines chip-wide register/IRQ constants, variant descriptors, the private `struct mc13xxx`, and common init/exit prototypes.

Important APIs, types, and functions: `MC13XXX_NUMREGS`, `MC13XXX_IRQ_REG_CNT`, and `MC13XXX_IRQ_PER_REG` define regmap and IRQ geometry. `struct mc13xxx_variant` carries the variant name and revision printer. `struct mc13xxx` stores regmap, device, variant, regmap-irq arrays, mutex, physical IRQ, flags, and ADC busy flags. Extern variant symbols and `mc13xxx_common_init()`/`mc13xxx_common_exit()` are the private contract.

Control flow: I2C and SPI front ends allocate `struct mc13xxx`, set transport-specific fields, then pass the owning device into `mc13xxx_common_init()`, which consumes the fields defined here.

State and persistence: this header describes all core in-memory state, including child IRQ metadata and ADC serialization. It has no executable persistence behavior by itself.

Dependencies and integration points: includes mutex, regmap, and public MC13xxx MFD definitions. It is intentionally local to `drivers/mfd`, preventing child drivers from depending on private internals.

Risks: the public/private split means changing this structure affects both bus drivers and core code but not external child drivers. The fixed-size IRQ array assumes two 24-bit banks for all supported variants. Test signals are compile-time: all MC13xxx transport and core objects must agree on struct layout, variant declarations, and IRQ constants.
