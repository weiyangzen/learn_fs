# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l85.c

Purpose: CS47L85/WM1840 group table for the Madera pinctrl core.

Important APIs/types/functions: defines MIF1-3, AIF1-4, DMIC4-6, and PDM speaker groups. `cs47l85_pin_chip` exports `CS47L85_NUM_GPIOS` and the group table.

Control flow: Madera core chooses this table for parent types `CS47L85` and `WM1840` when `CONFIG_PINCTRL_CS47L85` is enabled.

State and persistence: immutable group data only; common core writes hardware registers.

Dependencies/integration: Madera MFD chip constants and common pinctrl structures.

Risks: speaker groups use interleaved pins (`pdmspk1` 36/38 and `pdmspk2` 37/39), so group ordering is deliberate. Any mismatch with codec GPIO count truncates common pin descriptors.

Test signals: probe CS47L85/WM1840, inspect all 12 alternate groups, and apply AIF, MIF, DMIC, and speaker mux states to ensure common core handles high GPIO indices.
