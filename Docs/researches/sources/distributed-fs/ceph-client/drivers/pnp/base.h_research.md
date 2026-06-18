<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/base.h -->
# sources/distributed-fs/ceph-client/drivers/pnp/base.h

Purpose: Private PnP core header shared by the bus core, resource manager, protocol backends, sysfs interface, and quirks.

Important APIs/types/functions: declares global `pnp_lock`, `pnp_bus_type`, protocol/device/card allocation APIs, resource option structs (`pnp_port`, `pnp_irq`, `pnp_dma`, `pnp_mem`, `pnp_option`), dependent-set flag helpers, resource registration helpers, resource list helpers, conflict checkers, fixup entry point, debug macro, and `pnp_resource` wrapper.

Control flow: no standalone runtime flow; inline helpers encode/decode dependent resource set, priority, and option flags. `pnp_new_dependent_set()` increments `dev->num_dependent_sets`.

State/persistence: defines the in-memory model for possible resource options and current assigned resources. Resource lists persist on `struct pnp_dev` until freed by core release or reconfiguration.

Dependencies/integration: relies on public `linux/pnp.h`, `struct resource`, Linux list APIs, and optional ISA DMA support.

Risks: `PNP_OPTION_*` bit packing is shared across parsers, manager, interface, and quirks; changing it breaks all option traversal. `pnp_new_dependent_set()` clips invalid priority but still creates a set, so callers must validate firmware data where possible.

Test signals: parser tests for dependent option grouping, resource registration/freeing, and debug-on/debug-off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/base.h -->
