<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/manager.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/manager.c

Purpose: PnP resource assignment, conflict resolution, activation, and disabling.

Important APIs/types/functions: global `pnp_res_mutex`; resource assignment helpers `pnp_assign_port/mem/irq/dma()`, `pnp_assign_resources()`, `pnp_auto_config_dev()`, `pnp_start_dev()`, `pnp_stop_dev()`, `pnp_activate_dev()`, and `pnp_disable_dev()`.

Control flow: auto-config tries independent resources and dependent set 0, then subsequent dependent sets until assignment succeeds. Assignment clears auto resources, iterates option list for selected set, and chooses IO/mem ranges by walking alignment until `pnp_check_*()` accepts them; IRQ/DMA use fixed priority tables and optional disable semantics. Activation auto-configures then calls protocol `set`; disable calls protocol `disable`, clears active, and frees auto resources.

State/persistence: mutates `dev->resources` and `dev->active`. Firmware/device persistence is delegated to protocol callbacks. Auto-assigned resources are marked `IORESOURCE_AUTO` for later cleanup.

Dependencies/integration: PnP option/resource lists from firmware parsers, conflict checkers, protocol set/disable callbacks, optional ISA DMA API.

Risks: IRQ/DMA priority tables are i386-centric. `pnp_activate_dev()` comment warns it does not validate or set resources beyond auto-config path. Resource assignment can preserve user-set resources by updating flags. Power/probe callers must respect active/attached state.

Test signals: option sets with conflicts, optional IRQs, disabled zero-size resources, preconfigured resources, protocol set failure, and auto-resource cleanup after disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/manager.c -->
