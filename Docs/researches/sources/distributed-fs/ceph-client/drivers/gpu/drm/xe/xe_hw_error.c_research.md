# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.c

Purpose: handles discrete GPU hardware error interrupts, logs and counts RAS errors, processes PVC GT/SOC error registers, handles Battlemage CSC firmware errors, and processes boot-time hardware errors.

Important functions/data: error severity mapping, PVC error name tables with `static_assert` sizes, `fault_inject_csc_hw_error`, `csc_hw_error_work`, `csc_hw_error_handler`, logging helpers, `gt_hw_error_handler`, `soc_slave_ieh_handler`, `soc_hw_error_handler`, `hw_error_source_handler`, `xe_hw_error_irq_handler`, `hw_error_info_init`, `process_hw_errors`, and `xe_hw_error_init`.

Control flow: init skips non-DGFX and SR-IOV VF, initializes CSC error work on the root tile, initializes RAS info for PVC, then reads and processes boot-time master IRQ state. IRQ handler iterates hardware error classes signaled in master control, reads `DEV_ERR_STAT`, handles CSC errors specially, maps source bits to RAS components, dispatches GT/SOC platform handlers, logs/counts, clears status registers, and un/masks SOC event controls when needed.

State/persistence: RAS counters live in `xe->ras`; CSC error work schedules runtime survivability mode enablement. Error status is persisted in hardware registers until read/cleared.

Dependencies/integration: uses hardware error/GSC/IRQ registers, Xe DRM RAS, MMIO, survivability mode, Linux fault injection, IRQ lock, and platform checks for PVC/Battlemage.

Risks/test signals: register clear order matters to avoid losing or re-reporting errors. CSC firmware errors make the device unrecoverable and trigger survivability mode. Platform guards mean most logic is PVC or Battlemage specific. Test fault injection, blank status registers, correctable/nonfatal/fatal paths, PVC GT vector counters, SOC master/slave handling, CSC survivability work scheduling, and boot-time preexisting errors.
