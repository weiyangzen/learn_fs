<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_of.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_of.c

Purpose: Open Firmware / Device Tree transport wrapper for the shared Xillybus core.

Important APIs/types/functions: Device matches `xillybus,xillybus-1.00.a` and deprecated `xlnx,xillybus-1.00.a`. `xilly_drv_probe()` initializes an endpoint, maps the platform MMIO resource, requests the platform IRQ using `xillybus_isr()`, and calls `xillybus_endpoint_discovery()`. `xilly_drv_remove()` calls `xillybus_endpoint_remove()`.

Control flow: probe allocates devres-managed endpoint state, stores it as driver data, sets module owner, ioremaps resource 0, obtains IRQ 0, requests the IRQ, and delegates all discovery/device-node setup to the core. Remove delegates cleanup/quiesce to the core.

State and persistence: only runtime endpoint state stored on the platform device; devres owns MMIO/IRQ lifetime.

Dependencies and integration: depends on OF matching, platform devices, devm MMIO/IRQ helpers, and the shared Xillybus core/class modules.

Risks: probe returns directly on MMIO mapping failure after endpoint allocation, relying on devres cleanup. `platform_get_irq()` result is not explicitly checked before `devm_request_irq()`, so negative IRQ handling depends on request helper behavior. Device Tree resource correctness is mandatory.

Test signals: boot with matching DT node, verify MMIO/IRQ resources, successful endpoint discovery and device nodes, interrupt-driven I/O, remove/unbind cleanup, and deprecated compatible support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_of.c -->
