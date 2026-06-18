<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/dsa.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/dsa.c

## Purpose
Implements the libvfio driver backend for Intel DSA/IDXD devices, providing DMA memcpy and MSI generation operations.

## Important APIs, Types, and Functions
dsa_ops, dsa_probe/init/remove, dsa_command, dsa_register_cache_init, dsa_wq_init, dsa_group_init, dsa_memcpy_start/wait, dsa_send_msi.

## Control Flow
Probes Intel DSA device IDs, rejects devices requiring interrupt-handle requests, enables PCI memory/master, resets/configures device/workqueue/group, enables WQ and MSI-X, submits copy or batch descriptors through BAR2, polls completion records and SWERR, and resets on remove.

## State and Persistence
Stores descriptors, completions, cached registers, max limits, and MSI buffers in device->driver.region; mutates hardware registers and MSI-X state.

## Dependencies and Integration Points
Depends on libvfio PCI/IOMMU helpers, linux/idxd.h, DSA register definitions, Intel DSA hardware, MMIO BAR0/BAR2, and mapped DMA region.

## Risks and Edge Cases
Hardware-specific and privileged; polling loops can hang until assertion timeout; SWERR is fatal; batching has special handling for count==1 and count==2 edge cases.

## Test Signals
VFIO driver tests validate init/remove, memcpy success/error, MSI, and storm behavior through this ops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/drivers/dsa/dsa.c -->
