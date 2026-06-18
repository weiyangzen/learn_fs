# Research: sources/distributed-fs/ceph-client/include/linux/mfd/max77686-private.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77686-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77686-private.h

**Purpose:** Internal register, IRQ, and device-state definitions for MAX77686 and MAX77802 PMIC/RTC MFD support.

**Important APIs and types:** Provides PMIC and RTC register enums for MAX77686 and MAX77802, IRQ source/group enums, PMIC and RTC IRQ IDs, interrupt masks, `struct max77686_dev`, and `enum max77686_types`.

**Control flow:** Parent probe selects MAX77686 or MAX77802, configures a regmap and IRQ handling, then child regulator and RTC drivers use the correct register enum namespace. IRQ masks are cached in `irq_masks_cur` and `irq_masks_cache` under `irqlock`.

**State and persistence:** Runtime state includes I2C, regmap, IRQ number, IRQ lock, current/cache masks, and type. Hardware state includes regulator settings, PMIC status, RTC time/alarm/update registers, and interrupt masks.

**Dependencies and integration:** Depends on I2C, regmap, module, mutex, regulator and RTC child drivers, and MFD IRQ infrastructure.

**Risks:** MAX77686 RTC registers start at 0 while MAX77802 RTC registers are offset into the PMIC map; selecting the wrong type corrupts accesses. Some IRQ enum values restart at zero for RTC group, so group context is required. Cached masks must stay synchronized with hardware.

**Test signals:** Variant-specific register access tests, IRQ mask sync tests, RTC alarm/time register tests for both address layouts, and probe failure unwind tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77686-private.h -->
