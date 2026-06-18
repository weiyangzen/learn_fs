<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.c

## Purpose
Implements mlx5 Data Direct auxiliary PCI-device discovery and affiliation with mlx5 IB devices. It binds an RDMA device to a matching Data Direct PCI function by comparing VUID strings read from PCI VPD, allowing the IB device to use a separate data-direct device when present.

## Important APIs, Types, And Functions
- Global registries: `mlx5_data_direct_dev_list` tracks probed Data Direct PCI functions and `mlx5_data_direct_reg_list` tracks IB-device registrations waiting for a matching VUID.
- `struct mlx5_data_direct_registration` stores an `mlx5_ib_dev` pointer and fixed-size VUID copy for deferred matching.
- `mlx5_data_direct_vpd_get_vuid()` reads PCI VPD and extracts the read-only `VU` keyword into `dev->vuid`.
- `mlx5_data_direct_set_dma_caps()` configures 64-bit DMA, falls back to 32-bit DMA, and sets a 2 GiB max segment size.
- Public IB hooks: `mlx5_data_direct_ib_reg()` and `mlx5_data_direct_ib_unreg()` add/remove an IB device registration and call `mlx5_ib_data_direct_bind()` or `mlx5_ib_data_direct_unbind()` on matches.
- PCI lifecycle: `mlx5_data_direct_probe()`, `mlx5_data_direct_remove()`, and `mlx5_data_direct_shutdown()` enable/disable the PCI device and update the global matching lists.
- Module-facing hooks: `mlx5_data_direct_driver_register()` and `mlx5_data_direct_driver_unregister()` register/unregister the local `pci_driver`.

## Control Flow
When an mlx5 IB device with a VUID appears, it calls `mlx5_data_direct_ib_reg()`. The function allocates a registration, locks `mlx5_data_direct_mutex`, scans already-probed Data Direct devices for the same VUID, binds immediately if found, and then appends the registration for future device probes. When a Data Direct PCI device probes, the driver allocates `mlx5_data_direct_dev`, enables bus mastering and DMA capabilities, attempts to enable PCIe atomics, reads the VUID from VPD, and calls `mlx5_data_direct_dev_reg()`. That function binds all existing IB registrations with the same VUID and then makes the Data Direct device available for later IB registrations.

Removal reverses the order: `mlx5_data_direct_dev_unreg()` removes the PCI device from the global list first to block new affiliations, unbinds matching registered IB devices, then `mlx5_data_direct_remove()` disables PCI and frees the VUID/device allocation. `mlx5_data_direct_ib_unreg()` removes the IB registration and warns if the IB device was not registered.

## State And Persistence
The state is process-kernel memory only: two global lists protected by `mlx5_data_direct_mutex`, one VUID allocation per probed Data Direct device, and one registration allocation per registered IB device. Hardware state is limited to PCI enablement, bus mastering, DMA masks, max segment size, and attempted atomic-op enablement. No on-disk state is written.

## Dependencies And Integration Points
The file depends on PCI core, PCI VPD helpers, DMA API, mlx5 IB private definitions, and `data_direct.h`. It integrates with mlx5 IB device lifecycle through `mlx5_data_direct_ib_reg()` / `mlx5_data_direct_ib_unreg()` and with PCI module lifecycle through `pci_register_driver()`. The actual bind/unbind behavior is delegated to `mlx5_ib_data_direct_bind()` and `mlx5_ib_data_direct_unbind()` in the broader mlx5 IB driver.

## Risks And Edge Cases
All list operations require the global mutex; missed locking would race PCI probe/remove against IB registration/unregistration. `mlx5_data_direct_ib_reg()` uses `strcpy()` into a fixed buffer sized for the hardware VUID field plus NUL, so caller-provided VUID length must match that contract. If VPD lacks keyword `VU`, the PCI function is rejected. PCI atomic enablement failures are logged only at debug level and do not fail probe. Remove order assumes unbind callbacks tolerate being called while the PCI device is still enabled but already removed from the visible list.

## Test Signals
Test with a matching ConnectX-8 Data Direct PCI ID and VUID-bearing mlx5 IB device to verify immediate and deferred bind paths. Negative tests should cover missing VPD `VU`, VUID mismatch, IB unregister without registration, probe/remove races, 64-bit DMA fallback, PCI atomic-op unavailable platforms, module unload after active registrations, and KASAN/leak checks for registration and VUID allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.c -->
