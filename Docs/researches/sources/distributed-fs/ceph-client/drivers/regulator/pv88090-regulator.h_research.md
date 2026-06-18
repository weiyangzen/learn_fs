# sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.h

Purpose: defines PV88090 register addresses and bit masks used by `pv88090-regulator.c`.

Important APIs/types/functions: no functions or structs are provided. Constants cover system event/mask registers, BUCK1-3 config registers, LDO control registers, BUCK_FOLD_RANGE, event and mask bits, enable bits, voltage selector masks, current-limit masks, buck mode encodings, and VDAC/range-gain selectors.

Control flow: none directly. The C driver uses these constants for descriptor macro expansion, buck mode/current-limit operations, interrupt masking/clearing, and dynamic BUCK2/3 voltage range selection.

State and persistence: none in the header. It documents hardware register fields whose values persist in PMIC state.

Dependencies and integration: guarded by `__PV88090_REGISTERS_H__` and included by the PV88090 driver. Naming is coupled to `PV88090_BUCK`/`PV88090_LDO` token-pasting macros.

Risks and test signals: wrong masks or shifts would break current-limit reporting and range selection. The header defines `PV88090_REG_LDO3_CONT` though the C driver registers only LDO1 and LDO2, which may confuse future changes. Test through compile coverage, register read/write validation for generated fields, event handling, and voltage range selection.
