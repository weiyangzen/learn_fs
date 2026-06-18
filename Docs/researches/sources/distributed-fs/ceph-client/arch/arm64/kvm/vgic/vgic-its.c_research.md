# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-its.c

## Purpose
`vgic-its.c` implements the emulated GICv3 Interrupt Translation Service for KVM guests. It exposes an ITS KVM device, decodes guest ITS commands, maps device/event pairs to LPIs, injects MSIs, tracks ITS device/collection/translation state, supports GICv4 VLPI acceleration hooks, and saves/restores the ITS table ABI used by migration.

## Important APIs, Types, And Functions
The main userspace ABI surface is `kvm_arm_vgic_its_ops`, with `vgic_its_create()`, `vgic_its_destroy()`, `vgic_its_set_attr()`, `vgic_its_get_attr()`, and `vgic_its_has_attr()`. `kvm_vgic_register_its_device()` registers this device when GICv3 VGIC support is registered. `vgic_its_abi` describes table entry sizes and save/restore/commit callbacks; only ABI revision 0 is present, with 8-byte CTE/DTE/ITE entries. LPI-facing APIs include `vgic_add_lpi()`, `vgic_its_resolve_lpi()`, `vgic_its_inject_msi()`, `vgic_its_inject_cached_translation()`, `vgic_msi_to_its()`, `vgic_its_inv_lpi()`, and `vgic_its_invall()`.

ITS state is held in `struct vgic_its` plus linked lists of `its_device`, `its_collection`, and `its_ite`. LPIs live in the VM distributor `lpi_xa`; each ITE holds a reference to a `struct vgic_irq`. The translation cache is an xarray keyed by `(devid,eventid)` and stores extra IRQ references for software MSI fast paths.

## Control Flow
Device creation allocates an ITS, initializes locks/lists/cache, marks the VM as requiring MSI device IDs, initializes BASER/PROPBASER defaults, and commits the ABI. Userspace assigns the ITS MMIO frame through `KVM_DEV_ARM_VGIC_GRP_ADDR`, which registers an `IODEV_ITS` on the KVM MMIO bus.

Guest command processing starts when the guest writes CWRITER or enables CTLR. `vgic_its_process_commands()` walks the circular command buffer at CBASER from CREADR to CWRITER, reads 32-byte commands from guest RAM, and dispatches them through `vgic_its_handle_command()`. MAPD creates or removes devices and ITTs, MAPC creates or retargets collections, MAPI/MAPTI creates ITEs and LPIs, MOVI/MOVALL retarget LPIs, DISCARD/CLEAR remove mappings or pending state, INT injects an LPI, and INV/INVALL reload LPI properties.

MSI injection first tries `vgic_its_inject_cached_translation()`. On a cache miss, `vgic_msi_to_its()` resolves the doorbell GPA to the registered ITS iodev, the ITS lock is taken, and `vgic_its_trigger_msi()` resolves the LPI. Software LPIs set `pending_latch` and queue the IRQ; GICv4-backed LPIs call `irq_set_irqchip_state()` on the host IRQ.

## State And Persistence
Persistent state includes `enabled`, CBASER/CREADR/CWRITER, device and collection BASERs, PROPBASER, device tables, collection tables, ITTs, LPI target, priority, enable, pending, and VLPI hardware mapping. Save/restore is explicit through `KVM_DEV_ARM_ITS_SAVE_TABLES` and `KVM_DEV_ARM_ITS_RESTORE_TABLES`. Save sorts device and ITE lists, writes sparse next-offset encoded DTE/ITE records into guest RAM, and writes CTEs until a terminating invalid entry. Restore scans direct or indirect device tables, collection tables, and ITTs to rebuild lists and LPI references. `kvm_arch_allow_write_without_running_vcpu()` permits table writes during save when `table_write_in_progress` is set, covering dirty-ring tracking.

## Dependencies And Integration Points
This file depends on the common VGIC MMIO dispatcher (`kvm_io_gic_ops`), GICv3 register definitions, KVM guest-memory helpers, xarray, KVM device attributes, VCPU lookup by ID, and GICv4 ITS driver hooks such as `its_map_vlpi()`, `its_unmap_vlpi()`, `its_prop_update_vlpi()`, `its_invall_vpe()`, and vPE data in `vgic_v3_cpu_if`. It integrates with `vgic-mmio-v3.c` via LPI enable/PROP/PEND BASER handling and with `vgic-v3.c` pending table save.

## Risks
The highest-risk areas are lock ordering between `cmd_lock`, `its_lock`, KVM `config_lock`, all-vCPU locking, and xarray reference lifetimes; guest memory validation for direct and indirect BASER tables; migration correctness for sparse next-offset tables; and GICv4 state that cannot be saved on pre-v4.1 hardware. Cache invalidation is deliberately broad after retargeting/unmapping, and missing an invalidation could deliver an MSI to a stale LPI. Several command errors are architected positive ITS error codes rather than Linux errno, so callers must preserve that distinction.

## Test Signals
Useful signals are KVM VGIC ITS device attribute tests, MSI injection tests with valid and invalid DEVID/EVENTID pairs, guest ITS command sequences for MAPD/MAPC/MAPTI/MOVI/DISCARD/INV/INT, migration save/restore of sparse and indirect tables, LPI enable and pending-table synchronization tests, GICv4/v4.1 VLPI forwarding tests when hardware is available, and lockdep/KCSAN coverage for command processing and concurrent MSI injection.
