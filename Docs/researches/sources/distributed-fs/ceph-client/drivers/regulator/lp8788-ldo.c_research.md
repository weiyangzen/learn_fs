<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-ldo.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp8788-ldo.c

Purpose: LP8788 MFD child driver for twelve digital LDOs and ten analog LDOs, split across DLDO and ALDO platform drivers.

Important APIs/types/functions: `struct lp8788_ldo` stores parent, descriptor, regulator, and optional enable GPIO. Voltage tables cover chip-specific DLDO/ALDO groups. `lp8788_config_ldo_enable_mode()` maps selected rails to external enable IDs and optional GPIOs.

Control flow: module init registers both DLDO and ALDO platform drivers. Each probe allocates state, configures external-enable mode if applicable, fills regulator config from parent platform data, and registers one descriptor. Enable-time callbacks decode per-rail startup registers.

State and persistence: optional enable GPIO ownership is transferred to the regulator core. Hardware registers store voltage selectors, enable bits, enable-source selection, and startup timing.

Dependencies and integration: LP8788 MFD accessors, GPIO descriptors, platform children, regulator table/linear helpers, and parent platform data arrays.

Risks and test signals: external-enable GPIO absence deliberately forces default register-enable mode, while GPIO acquisition errors abort probe. Some voltage tables contain repeated values for reserved selectors. Test every DLDO/ALDO ID, external enable IDs and indexes, enable-time reads, fixed/table voltage behavior, and platform-data constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-ldo.c -->
