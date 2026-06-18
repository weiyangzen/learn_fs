# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.h

Purpose: this header defines the NBIO RAS dispatch interface.

Important types and APIs: `struct ras_nbio_ip_func` contains operations to handle RAS controller interrupts without BIF ring, handle ATHUB error-event interrupts without BIF ring, and read the current memory partition/NPS mode. `struct ras_nbio` stores the NBIO IP version, selected IP function table, and system callback table. Public functions are `ras_nbio_hw_init()`, `ras_nbio_hw_fini()`, and `ras_nbio_handle_irq_error()`.

Control flow and state: no active behavior exists here. NBIO state is held inside the core context.

Dependencies and integration: it includes `ras.h` and is used by core initialization, IRQ handling, and UMC NPS discovery. Risks are callback-contract issues: interrupt handlers are optional in the function table but memory partition mode is assumed by UMC initialization. Test signals should verify `get_memory_partition_mode` is available for every supported IP and that IRQ paths tolerate missing individual handlers.
