# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l92.c

Purpose: CS42L92/CS47L92/CS47L93 group table for the shared Madera pinctrl driver.

Important APIs/types/functions: defines `pdmspk1`, `aif1`, `aif2`, and `aif3` pin arrays, exported through `cs47l92_pin_chip` with `CS47L92_NUM_GPIOS`.

Control flow: Madera core selects this table for parent types `CS42L92`, `CS47L92`, and `CS47L93` when `CONFIG_PINCTRL_CS47L92` is enabled.

State and persistence: static table only.

Dependencies/integration: Madera MFD chip constants and the common pinctrl core.

Risks: this family has fewer alternate groups than larger Madera codecs; DT/pdata copied from CS47L85/90 may request nonexistent MIF/DMIC groups and fail. Pin numbering is zero-indexed.

Test signals: probe each supported parent type, inspect four alternate groups, and validate AIF plus PDM speaker muxing through pinctrl state application.
