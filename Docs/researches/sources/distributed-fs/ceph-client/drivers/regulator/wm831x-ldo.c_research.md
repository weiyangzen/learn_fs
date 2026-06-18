<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm831x-ldo.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/wm831x-ldo.c

Purpose: Provides WM831x general-purpose LDO, analogue LDO, and alive LDO regulator support through three platform subdrivers.

Important APIs and types: `struct wm831x_ldo` stores generated names, supply names, descriptor, base register, parent MFD pointer, and regulator device. GP LDOs support voltage ranges, suspend voltage, mode selection, status, bypass, and optimum-mode selection. ALDOs support a different voltage range and idle/normal mode mapping. Alive LDOs use a compact linear range and status-only reporting.

Control flow: Each probe derives the regulator ID, maps the register base from IORESOURCE_REG, fills descriptor registers and masks, applies platform init data, registers the regulator, and requests UV IRQs for GP/ALDO rails. Module init registers all LDO subdrivers as a group.

State and persistence: Driver state is per-device descriptor/private data. Voltage, enable, bypass, sleep voltage, mode, and UV status persist in WM831x registers.

Dependencies and integration points: Depends on WM831x MFD core, regmap, IRQ translation, platform data, platform resources, and regulator consumers.

Risks: Probe assumes platform data array layout matches platform IDs. GP LDO mode changes require coordinated writes to control and ON registers. Status paths depend on matching LDO ID to status-bit layout. Alive LDOs do not register UV IRQs.

Test signals: GP/ALDO/alive probes, voltage selector boundaries, bypass toggles, suspend voltage writes, mode get/set, optimum-mode thresholds, UV IRQ notification, and platform resource failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm831x-ldo.c -->
