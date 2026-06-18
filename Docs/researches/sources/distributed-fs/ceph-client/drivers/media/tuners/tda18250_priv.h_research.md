# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250_priv.h

Purpose: private register map, IRQ constants, power constants, and state type for the TDA18250 driver.

Important APIs and types: defines register offsets `R00_ID1` through `R5C_AGC_DEBUG`, `TDA18250_NUM_REGS`, power states, IRQ masks for calibration/init/tune, and `struct tda18250_dev`.

Control flow: the implementation uses these symbols for regmap volatile ranges, init tables, power transitions, AGC programming, IF/RF programming, IRQ polling, and PLL adjustment.

State and persistence: `struct tda18250_dev` captures device configuration and runtime cache: mutex, frontend/client/regmap links, crystal frequency, IF values, current IF, variant flags, warm-init flag, and a register array that is not materially used by the current C file.

Dependencies and integration points: includes the public TDA18250 header. It is private to the tuner module.

Risks: the large flat register list has minimal field masks, so call sites must supply correct masks manually. IRQ constants combine multiple bits and are compared with equality-mask semantics in wait code. The unused `regs` member can mislead maintainers into assuming a software shadow exists.

Test signals: compile coverage for all register references, regmap volatile read behavior, IRQ mask polling tests, and review of power/standby register traces against hardware documentation.
