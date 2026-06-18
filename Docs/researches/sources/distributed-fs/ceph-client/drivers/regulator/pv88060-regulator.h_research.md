# sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.h

Purpose: defines the PV88060 register map and bit masks consumed by `pv88060-regulator.c`.

Important APIs/types/functions: this header has no functions or types. It defines event/mask registers (`PV88060_REG_EVENT_A`, `PV88060_REG_MASK_A/B/C`), regulator configuration registers for BUCK1, LDO1-7, and SW1-6, event bits (`PV88060_E_VDD_FLT`, `PV88060_E_OVER_TEMP`), interrupt mask bits, enable bits, voltage selector masks, buck current-limit mask, and buck mode encodings.

Control flow: none directly. The C driver uses these constants to build regulator descriptors, set and get buck mode, mask/unmask interrupts, and clear event latches.

State and persistence: none in the header. It describes persistent PMIC register fields used by runtime code.

Dependencies and integration: guarded by `__PV88060_REGISTERS_H__` and included only by the PV88060 regulator implementation. Its names are tightly coupled to descriptor macros such as `PV88060_REG_##regl_name##_CONF`.

Risks and test signals: incorrect register addresses or masks would cause wrong regulator control or missed fault interrupts. Because macro-generated descriptor fields rely on exact naming patterns, renaming constants can break builds. Test signals are compile coverage of macro expansions and hardware/regmap tests for event bits, enable masks, selector masks, current limits, and buck mode values.
