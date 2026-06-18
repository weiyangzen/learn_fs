# sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_vdpa.h

## Purpose
This header defines mlx5 firmware interface objects for vDPA/virtio-net queue offload. It is an ABI layer for creating, modifying, querying, destroying, and counting virtio queue objects through mlx5 general object commands.

## Important APIs, Types, And Data
- Queue event mode enums select no MSI-X, QP-backed events, or MSI-X events.
- Queue type enums distinguish split and packed virtio rings. Capability bits expose split/packed support via `BIT()`.
- `struct mlx5_ifc_virtio_q_bits` is the low-level virtio queue context: queue type/index/size, event mode, feature toggles, event QPN or MSI-X vector, emulation id, descriptor/used/available addresses, queue mkey, tunnel descriptor limit, error type, three UMEM windows, counter set, PD, and descriptor-group mkey.
- `struct mlx5_ifc_virtio_net_q_object_bits` wraps queue state, modify field mask, VHCA id, feature bits, dirty bitmap logging fields, TIS/QPN target, hardware available/used indexes, and the nested queue context.
- `mlx5_ifc_create/query/modify/destroy_virtio_net_q_*` structs use mlx5 general object command headers.
- `MLX5_VIRTQ_MODIFY_MASK_*` enumerates writable fields for queue modify operations.
- `MLX5_VIRTIO_NET_Q_OBJECT_STATE_*` defines INIT, RDY, SUSPEND, and ERR object states; `MLX5_VIRTIO_NET_Q_OBJECT_NONE` is a sentinel for no object.
- `struct mlx5_ifc_virtio_q_counters_bits` and related create/destroy/query command structures expose descriptor and error counters.

## Control Flow
A vDPA driver allocates an mlx5 general object for each virtio-net queue, initializes queue memory addresses and keys, transitions the object state to ready, optionally updates indexes/features/dirty logging through modify masks, queries state or counters, and destroys the object during queue teardown. Dirty bitmap fields support live migration flows where logging is enabled, queried or dumped elsewhere, and later disabled.

## State And Persistence
Persistent state is firmware-resident per queue object: queue state, ring addresses, mkeys, queue indexes, dirty bitmap parameters, and counters. Host state consists of command buffers and software handles to the firmware object ids. Counters persist until destroyed or reset by firmware semantics outside this header.

## Dependencies And Integration Points
The header relies on `mlx5_ifc_general_obj_in_cmd_hdr_bits` and `mlx5_ifc_general_obj_out_cmd_hdr_bits` from the broader mlx5 IFC definitions. It integrates with the mlx5 vDPA driver, virtio/vhost memory registration, protection domains, UMEM/mkey setup, MSI-X or QP event wiring, and live migration dirty logging.

## Risks
Firmware compatibility is highly sensitive to bit offsets. Split versus packed queue support must be checked before programming `virtio_q_type`. Ring addresses, queue size, and mkeys must correspond to valid DMA/IOMMU mappings; stale mappings can corrupt guest memory. Modify operations must set the right `modify_field_select` bit or firmware may ignore changed fields. Dirty bitmap size/address/mkey mismatches risk incorrect live migration data.

## Test Signals
Useful signals include create/modify/query/destroy cycles for split and packed queues, transitions through INIT/RDY/SUSPEND/ERR paths, event delivery in MSI-X and QP modes, dirty bitmap enable/disable during migration tests, counter increments for received/completed descriptors, and negative tests for unsupported queue type or invalid mkey/address combinations.
