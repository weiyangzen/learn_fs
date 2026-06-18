# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l35.c

Purpose: CS47L35 chip-specific group table for the shared Madera pinctrl driver.

Important APIs/types/functions: defines pin arrays for `aif1`, `aif2`, `aif3`, `mif1`, and `pdmspk1`, then exports `cs47l35_pin_chip` with `CS47L35_NUM_GPIOS`.

Control flow: selected by Madera core during probe when parent type is `CS47L35` and hidden config support is enabled. The core combines these alternate groups with generated single-GPIO groups and shared functions.

State and persistence: static descriptor state only.

Dependencies/integration: Madera MFD constants, `pinctrl-madera.h`, and common Madera core.

Risks: `mif1` spans non-contiguous pins 6 and 15, so tests must not assume each group is contiguous. Zero-indexed datasheet conversion is a common maintenance hazard.

Test signals: build with CS47L35 table linked, verify group membership for non-contiguous `mif1`, and apply an `aif`/`pdmspk1` alternate function through DT or pdata mappings.
