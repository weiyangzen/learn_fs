# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/internal.h

Purpose: private endpoint-side MHI contract. It offsets generic MHI registers into endpoint BAR space, defines endpoint interrupt/doorbell registers, ring/channel/event state structs, and prototypes shared across endpoint `main`, `mmio`, `ring`, and `sm`.

Important types: `struct mhi_ep_ring` tracks cached host ring context, descriptor cache, offsets, DB registers, event interrupt vector/moderation, and started state. `struct mhi_ep_chan` tracks channel name, paired endpoint device, transfer callback, state, direction, partial TRE state, and lock. `union mhi_ep_ring_ctx` overlays command/event/channel/generic contexts.

Control flow role: this header describes how endpoint code maps host-owned contexts and doorbells. `main.c` queues work using these structures; `ring.c` starts/resets/cache-updates rings; `mmio.c` reads/writes endpoint registers; `sm.c` transitions MHI states.

State and persistence: in-memory state mirrors host ring pointers and channel states while the endpoint is powered. The actual host contexts live in shared memory mapped through controller `alloc_map()` callbacks.

Dependencies and integration: depends on common MHI protocol definitions and public `mhi_ep` controller/device types. It exposes `mhi_ep_bus_type` to endpoint code and links the endpoint object files.

Risks: interrupt mask registers use inverted naming semantics where writing one enables interrupts; ring offsets and DB register calculations are protocol-critical; channel pairing assumptions live outside this header but depend on `mhi_ep_chan`. Test signals include endpoint power-up, channel doorbells across all mask rows, event ring moderation, command ring processing, reset, suspend/resume, and build coverage.
