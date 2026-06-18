<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm831x-isink.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/wm831x-isink.c

Purpose: Registers WM831x current sinks as regulator-current devices with current limit selection and over-current notification.

Important APIs and types: `struct wm831x_isink` stores generated name, descriptor, register offset, parent WM831x pointer, and regulator device. `wm831x_isink_enable()` performs the required two-stage enable: current sink enable followed by drive enable, rolling back if drive enable fails. `wm831x_isink_disable()` clears drive then enable. Ops use regmap current-limit helpers with `wm831x_isinkv_values`.

Control flow: Probe obtains parent MFD data and platform data, rejects absent per-sink init data, reads the register resource, builds an ISINK descriptor, registers the regulator, translates the platform IRQ through `wm831x_irq()`, requests a threaded IRQ, and stores private data. Init uses `subsys_initcall()`.

State and persistence: No software state beyond descriptor/private pointers. Enable, drive, and current selection persist in the current-sink register. IRQ notification state is managed by devm.

Dependencies and integration points: Depends on WM831x MFD core, platform data, IORESOURCE_REG, IRQ resource, regmap, and regulator current consumers.

Risks: ID computation uses `pdev->id % ARRAY_SIZE(pdata->isink)` before checking `pdata`, so a missing parent platform-data pointer would be unsafe. Hardware requires both enable bits for `is_enabled()`. IRQ notification maps all sink IRQs to over-current.

Test signals: Valid and missing platform data, enable rollback on drive failure, current limit selector programming, IRQ notifier delivery, missing resources, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm831x-isink.c -->
