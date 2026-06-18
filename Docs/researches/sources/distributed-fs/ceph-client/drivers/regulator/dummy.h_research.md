# sources/distributed-fs/ceph-client/drivers/regulator/dummy.h

Purpose: Declares the dummy regulator rdev and initialization entry point for regulator framework fallback support.

Important APIs, types, and symbols: It forward-declares `struct regulator_dev`, exports `extern struct regulator_dev *dummy_regulator_rdev`, and declares `void __init regulator_dummy_init(void)`.

Control flow support: The regulator core can include this header to initialize and reference the dummy regulator implemented in `dummy.c`.

State and persistence: The only state contract is the external global pointer. This header does not define ownership rules beyond the dummy implementation's faux-device lifetime.

Dependencies and integration points: Private to the regulator subsystem and paired with `dummy.c`.

Risks and test signals: Ensure all users see the same global declaration and that initialization order makes the dummy regulator available before fallback consumers require it.
