<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_dev.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_dev.c

## Purpose
Implements the top-level `bng_re` RoCE auxiliary driver: module registration, auxiliary-bus probe/remove, device allocation, Ethernet-side registration, chip context setup, HWRM ring and stats allocation, RCFW channel bring-up, debugfs attachment, and orderly teardown.

## Important APIs, Types, And Functions
- Module metadata declares author, `BNG_RE_DESC`, and dual BSD/GPL licensing.
- `bng_re_dev_add()` allocates `struct bng_re_dev` with `ib_alloc_device()`, binds netdev, auxiliary device, BNGE auxiliary device, and PCI function id.
- `bng_re_register_netdev()` / `bnge_unregister_dev()` connect and disconnect the RDMA provider from the BNGE Ethernet auxiliary device.
- `bng_re_setup_chip_ctx()` and `bng_re_destroy_chip_ctx()` allocate/free chip context and device attributes, and wire `rdev->bng_res` and `rdev->rcfw` references.
- `bng_re_init_hwrm_hdr()` and `bng_re_fill_fw_msg()` are small HWRM message helpers used by ring and stats operations.
- `bng_re_net_ring_alloc()` / `bng_re_net_ring_free()` issue HWRM ring allocation/free commands through `bnge_send_msg()`.
- `bng_re_stats_ctx_alloc()` / `bng_re_stats_ctx_free()` issue HWRM stats context allocation/free commands using the DMA memory allocated by `bng_re_alloc_stats_ctx_mem()`.
- `bng_re_query_hwrm_version()` caches HWRM interface version and command timeout in `bng_re_chip_ctx`.
- `bng_re_dev_init()` is the main bring-up sequence; `bng_re_dev_uninit()` is the teardown sequence.
- `bng_re_probe()`, `bng_re_remove()`, `bng_re_mod_init()`, and `bng_re_mod_exit()` integrate with the auxiliary bus and module loader.

## Control Flow
Module init creates the debugfs root and registers an auxiliary driver named `rdma` that matches `bng_en.rdma`. Probe allocates `bng_re_en_dev_info`, stores BNGE auxiliary state in driver data, allocates an RDMA device, and calls `bng_re_dev_init()`.

`bng_re_dev_init()` registers with the Ethernet device, verifies at least two MSI-X vectors, allocates chip context and device attributes, queries HWRM version, allocates the RCFW command/event queues, copies MSI-X records into `rdev->nqr`, allocates a CREQ network ring through HWRM, maps/enables the firmware channel, queries device attributes via `bng_re_get_dev_attr()`, creates debugfs, allocates coherent stats memory, allocates a firmware stats context, initializes firmware via RCFW, and marks `BNG_RE_FLAG_RCFW_CHANNEL_EN`.

Every failure label unwinds only the resources already acquired: stats context, coherent stats memory, RCFW channel mappings and IRQ, CREQ ring, `nqr`, firmware channel queues, chip context, and netdev registration. Remove calls `bng_re_dev_uninit()`, which removes debugfs, deinitializes firmware if enabled, frees firmware and stats resources, frees `nqr`, destroys chip context, unregisters from BNGE, and deallocates the RDMA device.

## State And Persistence
Persistent driver state lives in `struct bng_re_dev`: embedded `ib_device`, flags, netdev and auxiliary device pointers, BNGE auxiliary pointer, chip context, function id, resource root, RCFW channel, MSI-X/NQ record, device attributes, debugfs root, and stats context. HWRM-allocated state includes CREQ ring id and stats context id; DMA state includes stats memory and firmware command/event queues. Flags track netdev registration and firmware channel enablement to make teardown conditional.

## Dependencies And Integration Points
Depends on Linux module, PCI, auxiliary bus, RDMA core allocation, BNGE auxiliary APIs (`bnge_register_dev()`, `bnge_unregister_dev()`, `bnge_send_msg()`), BNGE HWRM structures, `bng_fw` channel functions, `bng_res` allocation helpers, `bng_sp` device-attribute query, and debugfs helpers. It bridges the Ethernet BNGE driver and RDMA core provider instance.

## Risks And Edge Cases
Bring-up ordering is sensitive: RCFW enablement requires a CREQ ring id and MSI-X vector, and firmware initialization requires device attributes and stats context. `bng_re_dev_init()` adds debugfs before stats allocation; failures after that jump to `disable_rcfw` and do not remove the per-device debugfs directory, so a stats or firmware-init failure can leave a debugfs child until broader cleanup occurs. `bng_re_net_ring_free()` logs `req.ring_id`, which is little-endian. Resource cleanup depends on `BNG_RE_FLAG_RCFW_CHANNEL_EN`; partial channel setup before the flag is set must be fully unwound by failure labels.

## Test Signals
Module load/unload should create and remove the debugfs root and register/unregister the auxiliary driver. Probe with insufficient MSI-X vectors should fail cleanly after netdev registration is unwound. Successful probe should show HWRM version query, CREQ ring allocation, IRQ request, firmware initialization, stats context allocation, and no leaks on remove. Fault injection at each `bng_re_dev_init()` step should verify reverse-order cleanup, especially debugfs, stats, ring, and RCFW channel resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_dev.c -->
