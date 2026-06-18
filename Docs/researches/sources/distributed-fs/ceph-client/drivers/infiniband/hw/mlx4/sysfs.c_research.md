# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/sysfs.c

## Purpose
This file builds the mlx4 InfiniBand SR-IOV sysfs surface. It exposes master-only IOV port trees for administrative alias GUIDs, operational GIDs, physical P_Keys, multicast group attributes, per-VF virtual-to-physical P_Key mappings, GID index views, and SMI enablement controls.

## Important APIs, types, and functions
Public entry points are `mlx4_ib_device_register_sysfs`, `mlx4_ib_device_unregister_sysfs`, `add_sysfs_port_mcg_attr`, and `del_sysfs_port_mcg_attr`. Key helpers include `show_admin_alias_guid`, `store_admin_alias_guid`, `show_port_gid`, `show_phys_port_pkey`, `add_port_entries`, `register_pkey_tree`, `unregister_pkey_tree`, `add_port`, `add_vf_smi_entries`, and `remove_vf_smi_entries`. The local `struct mlx4_port` wraps a kobject plus attribute groups for per-slave/port P_Key and GID mappings.

## Control flow
Registration only runs on master devices. It creates an `iov` kobject under the IB device, a physical `ports` subtree, and for each RDMA port creates `admin_guids`, `gids`, `pkeys`, and `mcgs` subdirectories. Each admin GUID file can be read and written; writes update the cached alias GUID record under `ag_work_lock`, mark the record idle/pending, set the admin GUID in mlx4 core, update the component mask, and queue alias GUID work. GID and physical P_Key entries are read-only views backed by mlx4 query helpers.

The P_Key tree creates one device directory per PF/VF and a `ports/<port>/pkey_idx` group for active ports. Dom0/master mappings are read-only; VF mappings can be written on InfiniBand ports, update `virt2phys_pkey`, synchronize the hardware P_Key table, and generate a P_Key event. The `gid_idx` group exposes the slave id. Non-Ethernet non-master VF ports also receive `smi_enabled` and `enable_smi_admin` files.

Unregistration tears down alias GUID trees, P_Key trees, sysfs groups, optional SMI files, and kobject references.

## State and persistence behavior
The sysfs tree reflects runtime driver state. Writes mutate in-memory SR-IOV structures and hardware/admin-guid state through mlx4 core, but this file does not persist configuration to disk. Kobject lifetimes and reference counts are the main persistence concern across register/unregister.

## Dependencies and integration points
This code integrates with Linux sysfs/kobject APIs, mlx4 SR-IOV alias GUID and P_Key management, RDMA port/GID/P_Key query helpers, active port discovery, VF SMI controls, and the driver's multicast group sysfs hooks.

## Risks
Risks include kobject reference-count imbalance, partial-registration cleanup ordering, fixed-length sysfs attribute names, unchecked `sscanf` conversions for admin GUID writes, concurrent alias GUID updates, exposing writes on unsupported transport modes, and cleanup assumptions around multiple `kobject_put` calls. Incorrect P_Key mapping can disrupt VF isolation and traffic authorization.

## Test signals
Validate master versus non-master behavior, full sysfs tree creation/removal with kmemleak/refcount diagnostics, admin GUID read/write including reserved GUID 0 behavior, P_Key VF remap and event generation, SMI toggles on IB but not Ethernet ports, MCG attribute add/remove, failure injection at every kobject allocation step, and concurrent sysfs access during device unregister.
