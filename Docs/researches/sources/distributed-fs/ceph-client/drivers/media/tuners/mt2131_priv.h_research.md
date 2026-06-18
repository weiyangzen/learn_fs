# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131_priv.h

Purpose: private MT2131 constants and state layout used by `mt2131.c`.

Important APIs/types: defines selected register aliases (`MT2131_PWR`, `MT2131_UPC_1`, `MT2131_AGC_RL`, `MT2131_MISC_2`), fixed frequency constants in kHz (`MT2131_IF1 1220`, `MT2131_IF2 44000`, `MT2131_FREF 16000`), and `struct mt2131_priv` with config pointer, I2C adapter pointer, and cached `frequency`.

Control flow and integration: the C file uses the IF/reference constants in PLL calculations and private state in every I2C/tuner callback. The register aliases are only partly used by name; several implementation writes still use raw numeric addresses.

State and persistence: private state is transient kernel memory attached to `fe->tuner_priv`; no persistent storage is involved.

Dependencies: requires `struct mt2131_config`, `struct i2c_adapter`, and integer types supplied through the including C file/header chain.

Risks: IF constants are hard-coded despite the public attach function accepting `if1`. Register aliases are sparse, so raw numeric register writes in the C file remain harder to audit. Unit comments say kHz, and calculations depend on that unit convention.

Test signals: verify PLL calculations when constants are changed, check all raw register writes against aliases/documentation, and confirm private frequency cache matches the tuned RF after rounding.
