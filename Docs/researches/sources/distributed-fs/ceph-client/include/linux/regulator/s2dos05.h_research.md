# sources/distributed-fs/ceph-client/include/linux/regulator/s2dos05.h

Purpose: this header describes the Samsung S2DOS05 regulator PMIC register map, regulator IDs, IRQ bits, voltage selector geometry, enable masks, ramp delay, and enable timing constants.

Important APIs/types/functions: no functions are declared. `enum S2DOS05_reg` gives register offsets for device ID, status, enable, LDO/buck config, IRQ mask/status, thermal/short-circuit, and over-current registers. `enum S2DOS05_regulators` exposes `S2DOS05_LDO1` through `S2DOS05_BUCK1`. Macros define IRQ bits, minimum voltages, selector steps, VSEL/fast-discharge masks, enable bits, ramp delay, enable times, and voltage count calculations.

Control flow: a regulator driver uses these constants to decode IRQ status, configure voltage selectors, enable or disable specific rails through `S2DOS05_REG_EN`, and report ramp/enable delays to the regulator core. Fast-discharge and buck/LDO selector masks constrain register update operations.

State and persistence: hardware registers hold the state. This header does not allocate memory or own kernel state, but its constants describe persistent PMIC enable, voltage, interrupt, and fault state.

Dependencies and integration points: depends on common bit macros and integrates with regulator core, regmap/I2C access, PMIC IRQ handling, and Samsung/Qualcomm board power descriptions using S2DOS05.

Risks: voltage constants directly affect regulator constraints; an off-by-one voltage count or wrong enable bit can expose unsafe rail behavior. Test signals include voltage list/range tests, enable mask verification, IRQ injection or fault decoding, and regulator boot/suspend checks on hardware.
