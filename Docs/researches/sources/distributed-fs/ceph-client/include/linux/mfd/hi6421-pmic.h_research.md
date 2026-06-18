# sources/distributed-fs/ceph-client/include/linux/mfd/hi6421-pmic.h

Purpose: This small header defines the HiSilicon HI6421 PMIC core interface. It provides bus-address conversion, over-current protection debounce settings, the parent PMIC state, and chip type identifiers.

Important APIs, types, and constants: `HI6421_REG_TO_BUS_ADDR(x)` shifts logical register numbers for the PMIC bus format. `HI6421_REG_MAX` bounds register access. OCP debounce/control macros define register address, selection mask, debounce intervals from 8 ms to 64 ms, debounce enable, and auto-stop enable. `struct hi6421_pmic` holds the device, regmap, IRQ, and optional chip pointer. `enum hi6421_type` distinguishes supported PMIC variants.

Control flow, state, and persistence: Runtime flow is in the MFD core and child drivers that use regmap with shifted addresses. Hardware state includes OCP debounce policy, OCP auto-stop behavior, IRQ state, and regulator/PMIC registers behind this map. The header has no executable logic.

Dependencies and integration points: It integrates with regmap, IRQ handling, regulator children, and platform/DT matching for variant selection.

Risks and test signals: Risks include forgetting the two-bit bus-address stride, programming the wrong OCP debounce value, and incomplete variant matching. Test signals include regmap address translation checks, OCP interrupt/debounce testing, regulator child probe, and IRQ handling under fault injection.
