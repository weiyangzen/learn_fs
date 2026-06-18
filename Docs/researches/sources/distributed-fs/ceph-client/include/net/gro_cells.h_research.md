# sources/distributed-fs/ceph-client/include/net/gro_cells.h

Purpose: declares per-CPU GRO cells used by virtual or tunnel devices to feed received skbs into GRO safely and scalably.

Important APIs/types: `struct gro_cells` contains a per-CPU pointer to `struct gro_cell` storage. `gro_cells_init()` allocates/initializes cells for a net device, `gro_cells_receive()` queues an skb into the appropriate cell/GRO path, and `gro_cells_destroy()` tears them down.

Control flow and state: this header only exposes lifecycle and receive entry points. Runtime state is per-CPU, tied to the device, and destroyed when the owning device exits. Receive code uses the per-CPU cell to avoid global contention before normal GRO/NAPI processing.

Dependencies and integration: depends on skbuffs, slab allocation, and netdevice definitions. It integrates with tunnel devices and virtual netdevices that do not receive packets from hardware NAPI directly.

Risks: teardown must not race with in-flight receive. Per-CPU allocation failures and device unregister paths need coverage. Tests should exercise init/receive/destroy, CPU migration stress, device down/unregister with queued skbs, and GRO aggregation behavior through tunnel devices.
