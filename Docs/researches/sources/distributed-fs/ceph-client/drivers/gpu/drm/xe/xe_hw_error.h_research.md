# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.h

Purpose: public hardware error init and IRQ handling contract.

Important APIs: `xe_hw_error_irq_handler(struct xe_tile *tile, const u32 master_ctl)` and `xe_hw_error_init(struct xe_device *xe)`.

Control flow/state: device init calls `xe_hw_error_init`; IRQ code calls the handler with a tile and master interrupt control bits.

Dependencies/integration: forward-declares tile and device and includes Linux types.

Risks/test signals: callers must pass the correct tile matching the MMIO master status. Tests should verify init is a no-op for non-DGFX and SR-IOV VF.
