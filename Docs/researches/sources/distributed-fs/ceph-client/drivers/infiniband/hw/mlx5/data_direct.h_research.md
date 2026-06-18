<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.h

## Purpose
Declares the mlx5 Data Direct PCI-device representation and the registration hooks used by the mlx5 IB driver and module lifecycle.

## Important APIs, Types, And Functions
- `struct mlx5_data_direct_dev` stores the Linux `device`, owning `pci_dev`, VUID string, and global-list linkage for a Data Direct function.
- `mlx5_data_direct_ib_reg()` / `mlx5_data_direct_ib_unreg()` register or unregister an IB device by VUID.
- `mlx5_data_direct_driver_register()` / `mlx5_data_direct_driver_unregister()` expose PCI driver lifecycle entry points.

## Control Flow
The header has no executable control flow. It supplies declarations for `data_direct.c` and any mlx5 IB device lifecycle code that needs to register an IB device for Data Direct binding.

## State And Persistence
No state is stored in the header. The declared structure is persisted in memory by `data_direct.c` for each probed PCI Data Direct device.

## Dependencies And Integration Points
The header forward-declares `struct mlx5_ib_dev` and relies on includers to have definitions for `struct device`, `struct pci_dev`, and `struct list_head` through surrounding mlx5 or Linux headers. It is the integration contract between the Data Direct PCI shim and the rest of mlx5 IB.

## Risks And Edge Cases
The header is intentionally minimal and not standalone: direct inclusion without the common mlx5/Linux headers would miss type declarations for `device`, `pci_dev`, and `list_head`. The `vuid` pointer lifetime is implementation-owned and must be freed by the PCI remove path.

## Test Signals
Header self-containment checks may flag missing type includes if included standalone. Normal build coverage should confirm prototypes match `data_direct.c` and call sites in the mlx5 IB lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/data_direct.h -->
