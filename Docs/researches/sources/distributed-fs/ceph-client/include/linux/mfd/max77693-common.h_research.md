# Research: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-common.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-common.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77693-common.h

**Purpose:** Shared device-state definition for the related MAX77693, MAX77705, and MAX77843 MFD families.

**Important APIs and types:** `enum max77693_types` identifies supported family members. `struct max77693_dev` stores parent device, multiple I2C clients, type, regmaps for PMIC/MUIC/haptic/charger/LEDs, IRQ chip data for LED/top-system/charger/MUIC, and the host IRQ.

**Control flow:** Family-specific parent code initializes only the I2C clients/regmaps/IRQ domains present for the detected chip, then children share this structure.

**State and persistence:** Runtime state is the multi-regmap, multi-IRQ-chip parent structure. Hardware state persists in the individual PMIC, MUIC, haptic, charger, and LED register blocks.

**Dependencies and integration:** Relies on forward-declared device/I2C/regmap/IRQ types through including C files. Integrates with charger, MUIC/extcon, haptic, flash LED, RGB LED, and top-system IRQ children.

**Risks:** Not every pointer is valid for every chip type; child drivers must gate on `type` or presence. Multiple slave addresses make probe and cleanup ordering important.

**Test signals:** Probe/remove matrix across all `TYPE_MAX77693*` values, child registration tests for absent optional regmaps, and IRQ-domain tests per available sub-block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-common.h -->
