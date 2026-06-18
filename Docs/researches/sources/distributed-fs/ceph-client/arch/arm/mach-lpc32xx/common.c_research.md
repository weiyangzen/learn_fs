# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.c

Purpose: Common LPC32xx platform helpers for static IO mapping, unique ID reporting, IRAM size detection, and Ethernet PHY pin mode selection.

Important APIs/types/functions: Defines `lpc32xx_get_uid()`, `lpc32xx_return_iram()`, `lpc32xx_set_phy_interface_mode()`, `lpc32xx_map_io()`, and `lpc32xx_check_uid()` arch initcall.

Control flow: Map IO installs static AHB0/AHB1/FABAPB/IRAM mappings. UID reads four clock/power device ID registers and uses them for `system_serial_*` if unset. IRAM detection probes whether the second 128K bank aliases the first by temporary write/read. PHY mode updates MAC clock-control pin mux bits for MII or RMII.

State and persistence: Persistent state includes cached `iram_size` and global ARM `system_serial_low/high`. Hardware state includes static mappings and MAC pin selection register.

Dependencies and integration points: Depends on `lpc32xx.h` address macros, ARM `iotable_init`, system_info serial globals, and exported NXP misc API users.

Risks: IRAM probing writes to IRAM and assumes it is safe to modify/restore that location. `lpc32xx_set_phy_interface_mode()` treats every non-MII mode as RMII. Raw MMIO accesses depend on static mappings existing first.

Test signals: Boot LPC32xx, check printed UID/system serial, call IRAM helper from a user driver, and validate Ethernet pin mode on MII/RMII boards.
