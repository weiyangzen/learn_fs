# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.c

Purpose: this is the generic NBIO RAS dispatch layer. It selects the NBIO IP function table, enables/disables NBIO RAS interrupt sources through system callbacks, and forwards IRQ handling.

Important APIs: `ras_nbio_hw_init()` installs `nbio_sys_fn`, selects `ras_nbio_v7_9` for IP versions 7.9.0 and 7.9.1, and enables RAS controller and ATHUB error-event IRQs if callbacks are present. `ras_nbio_hw_fini()` disables those IRQs. `ras_nbio_handle_irq_error()` calls IP-specific handlers for controller and ATHUB interrupts and returns true.

Control flow and state: state is the configured NBIO IP version, system callback table, and selected IP function table. No persistence is owned here. IRQ enablement is a hardware side effect during core hardware init/fini.

Dependencies and integration: core delegates NBIO interrupts to this layer. UMC asks core for current NPS mode, which forwards to `nbio->ip_func->get_memory_partition_mode`. Risks include unconditional true return even if handlers fail, optional callback omissions silently leaving interrupts disabled, and no null checks in current NPS mode beyond the core wrapper. Test signals should cover supported/unsupported IP init, missing sys callbacks, IRQ enable/disable calls, handler error propagation expectations, and NPS mode reads.
