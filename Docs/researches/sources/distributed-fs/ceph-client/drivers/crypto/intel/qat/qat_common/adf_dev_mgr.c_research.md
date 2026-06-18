# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dev_mgr.c

## Purpose
This file maintains the global QAT device registry and user-visible device IDs. It tracks PFs, guest VFs, host VFs, detached VF ID mappings, device reference counts, class indexes, reset/started status queries, and total device count.

## Important APIs, Types, And Functions
Public APIs include `adf_devmgr_add_dev()`, `adf_devmgr_rm_dev()`, `adf_devmgr_pci_to_accel_dev()`, `adf_devmgr_get_dev_by_id()`, `adf_devmgr_verify_id()`, `adf_devmgr_get_num_dev()`, `adf_devmgr_update_class_index()`, `adf_clean_vf_map()`, `adf_dev_in_use()`, `adf_dev_get()`, `adf_dev_put()`, `adf_devmgr_in_reset()`, and `adf_dev_started()`. Internal state includes `accel_table`, `vfs_table`, `table_lock`, `num_devices`, and `id_map`.

## Control Flow
Add-dev assigns IDs differently for PFs/guest VFs versus host VFs with a PF. PF-like devices get a free ID and a synthetic VF map entry. Host VFs either reuse detached mappings or allocate new mappings based on BDF-derived VF number. Remove-dev frees PF-like IDs but keeps detached host VF mappings for stable numbering. Lookup by user ID first maps fake VF IDs to real IDs. Refcount helpers also pin/unpin the owning module on first/last use.

## State And Persistence Behavior
Registry state is global and volatile for the loaded base module. Detached VF mappings can persist after VF removal until `adf_clean_vf_map()` is called, preserving user-visible numbering across VF detach/reattach.

## Dependencies And Integration Points
It depends on PCI BDF data, common config constants, module refcounting, and all PCI PF/VF drivers. Control ioctl status/start/stop paths use it heavily.

## Risks
ID-map accounting must stay balanced with list operations. Host VF fake-ID shifting is subtle and can affect user tools. Returning device pointers after unlocking assumes lifecycle synchronization by callers. `adf_dev_put()` assumes balanced gets.

## Test Signals
Probe/remove PFs and VFs, detach/reattach host VFs, query device count/status, start/stop by ID/all devices, refcount/module pin behavior under active crypto users, and cleanup on module unload validate this file.
