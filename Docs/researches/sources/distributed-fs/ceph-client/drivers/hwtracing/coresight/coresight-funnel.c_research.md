# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-funnel.c

## Purpose
This file implements the CoreSight funnel link driver. A funnel merges multiple input trace streams into one output stream. The driver supports static platform-described funnels and dynamic AMBA funnels with programmable registers.

## Important APIs, Types, And Functions
`struct funnel_drvdata` stores MMIO base, optional `atclk` and `pclk`, the registered `coresight_device`, port priority, and a raw spinlock. `funnel_enable()` and `funnel_disable()` implement `coresight_ops_link` and manage `in->dest_refcnt` so the same input port can be shared by nested paths. Dynamic hardware operations are handled by `dynamic_funnel_enable_hw()` and `dynamic_funnel_disable_hw()`, which unlock CoreSight management registers, claim/disclaim the device, set hold time, toggle the selected input bit in `FUNNEL_FUNCTL`, and write `FUNNEL_PRICTL`. Sysfs attributes expose `priority` and read-only `funnel_ctrl`.

## Control Flow And State
Probe flows through `funnel_platform_probe()` or `dynamic_funnel_probe()` into common `funnel_probe()`. The common path allocates a unique CoreSight name, enables clocks, maps MMIO when a resource is present, gets firmware topology with `coresight_get_platform_data()`, and registers a `CORESIGHT_DEV_TYPE_LINK` with subtype `CORESIGHT_DEV_SUBTYPE_LINK_MERG`. Enable/disable is serialized by `drvdata->spinlock`; hardware programming occurs only on the first enable or last disable for a port.

## Dependencies And Integration Points
The driver uses platform and AMBA registration through `coresight_init_driver()`, runtime PM clock callbacks, firmware matching for OF and ACPI, and common CoreSight claim/lock helpers from `coresight-priv.h`. It depends on connection state maintained by the CoreSight path builder through `struct coresight_connection`.

## Risks And Test Signals
Refcount underflow on disable would incorrectly clear an active port, so path construction and balanced enable/disable are important. `priority_store()` accepts any hex value and does not mask to implemented fields, so invalid priority values rely on hardware tolerance. Dynamic funnels without MMIO behave as static links and skip register programming. Test signals include OF/ACPI probe, sysfs `funnel_ctrl` reads under runtime PM, multiple simultaneous paths sharing an input, claim failure handling on first enable, and suspend/resume clock sequencing.
