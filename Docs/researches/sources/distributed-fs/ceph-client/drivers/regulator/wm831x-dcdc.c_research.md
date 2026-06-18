<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm831x-dcdc.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/wm831x-dcdc.c

Purpose: Provides WM831x DC-DC regulator support for voltage bucks, programmable bucks, boost converters, and external power-enable outputs using separate platform subdrivers.

Important APIs and types: `struct wm831x_dcdc` stores names, descriptor, base register, MFD pointer, regulator device, optional DVS GPIO, and cached ON/DVS selectors. Shared helpers map regulator modes, suspend modes, and status from WM831x registers. `wm831x_buckv_set_voltage_sel()` implements DVS selector/GPIO behavior, while `wm831x_dcdc_uv_irq()` and `_oc_irq()` notify regulator events.

Control flow: Each subdriver derives an ID from platform ID and optional WM831x instance number, reads IORESOURCE_REG for the block base, fills a descriptor with register/mask data, applies platform init data, registers the regulator, requests fault IRQs where applicable, and stores private data. Module init registers all four platform drivers.

State and persistence: Cached ON and DVS selectors mirror hardware selector registers for BUCKV rails. Mode, voltage, enable, current limit, and status persist in WM831x registers. DVS GPIO state is maintained in software.

Dependencies and integration points: Depends on WM831x MFD core, regmap, IRQ translation, platform resources, platform data arrays, optional GPIO descriptors, and regulator consumers.

Risks: Several code paths assume platform data arrays exist, especially boost and EPE ID expressions. DVS setup logs failures but continues with reduced behavior. IRQ registration failures abort regulator probe after registration under devm cleanup. Mode/status interpretation is register-bit sensitive.

Test signals: Probe all subdriver names, missing REG resources, BUCKV DVS GPIO success/failure, voltage and suspend voltage programming, UV/HC IRQ notifier events, boost/EPE enable status, and module init unwind across multi-driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm831x-dcdc.c -->
