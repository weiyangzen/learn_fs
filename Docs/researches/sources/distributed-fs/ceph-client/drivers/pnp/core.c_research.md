<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/core.c

Purpose: Core PnP protocol and device registration, global device lists, allocation/release, and bus initialization.

Important APIs/types/functions: global `pnp_protocols`, `pnp_global`, `pnp_lock`, and `pnp_platform_devices`. Functions include `pnp_register_protocol()`, `pnp_alloc_dev()`, `__pnp_add_device()`, `pnp_add_device()`, `pnp_free_resources()`, `pnp_free_resource()`, and release helpers.

Control flow: `pnp_init()` registers the `pnp` bus at `subsys_initcall`. Protocols register with the lowest unused protocol number and a parent device name `pnpN`. Backends allocate devices with protocol/number/initial ID, initialize resources/options, and call `pnp_add_device()` or `__pnp_add_device()`. Add path applies quirks, marks device ready, links into global/protocol lists under `pnp_lock`, registers with driver core, and sets wakeup capability if protocol supports it.

State/persistence: global lists persist for lookup and enumeration. Each `pnp_dev` owns ID, resource, and option lists freed by `pnp_release_device()`. `pnp_platform_devices` records whether ACPI/BIOS found platform devices to suppress blind legacy probes.

Dependencies/integration: driver core bus/device APIs, DMA mask setup, PnP resource/options helpers, and protocol backends.

Risks: protocol number assignment scans with a restart pattern that assumes list order/locking is correct. Device registration failure must delist before release. Backends passing malformed PnP IDs can affect matching and modalias.

Test signals: register multiple protocols, add/remove failed devices, wakeup-capable protocols, and global list iteration under concurrent driver probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/core.c -->
