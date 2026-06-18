# sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.h

Purpose: defines PV88080 event, mask, regulator register, voltage-range, current-limit, and mode bit constants for both AA and BA register-layout variants.

Important APIs/types/functions: no functions or structs are declared. The header provides AA and BA addresses for HVBUCK and BUCK1-3 control/config registers, event and mask bits, enable masks, voltage selector masks, current-limit masks, buck mode encodings, and VDAC/range-gain selectors.

Control flow: none directly. The C driver maps these constants into `struct pv88080_compatible_regmap` tables, then uses them to fill mutable regulator descriptors and calculate runtime voltage ranges.

State and persistence: none. Constants describe PMIC register fields that back persistent hardware state.

Dependencies and integration: guarded by `__PV88080_REGISTERS_H__` and included by `pv88080-regulator.c`. The constants are coupled to both variant regmap tables and regulator descriptor initialization.

Risks and test signals: AA/BA address mismatches would silently control the wrong registers. Current-limit masks are per buck but mode operations use the BUCK1 mode mask constant for all bucks, so mask equivalence matters. Test by compiling both match-data tables, validating AA/BA register access, reading VDAC/range-gain fields, and exercising event/mask bits.
