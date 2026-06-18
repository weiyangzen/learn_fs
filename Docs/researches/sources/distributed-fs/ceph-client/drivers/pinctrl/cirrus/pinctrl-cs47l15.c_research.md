# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l15.c

Purpose: CS47L15 chip-specific Madera pin-group table.

Important APIs/types/functions: static pin arrays define `aif1`, `aif2`, `aif3`, and `pdmspk1` groups. Exported `const struct madera_pin_chip cs47l15_pin_chip` reports `CS47L15_NUM_GPIOS`, group pointer, and group count.

Control flow: no probe here; `pinctrl-madera-core.c` selects this exported table when the Madera parent type is `CS47L15` and `CONFIG_PINCTRL_CS47L15` is enabled.

State and persistence: immutable table data only; runtime mux/pinconf state is managed by the Madera core in codec registers.

Dependencies/integration: includes Madera core header for chip constants and `pinctrl-madera.h` for shared table structures. Function names intentionally match group names for alternate functions.

Risks: pin numbers are zero-indexed relative to datasheet numbering; off-by-one edits would misroute codec audio pins. Missing hidden Kconfig selection causes the common core to reject CS47L15 with `-ENODEV`.

Test signals: compile with CS47L15 support, probe Madera pinctrl on a CS47L15 parent, and verify debugfs exposes 15 pins plus the four alternate groups.
