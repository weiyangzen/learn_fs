# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.c

Purpose: this file implements NBIO v7.9 register-level RAS interrupt clearing and memory partition mode discovery.

Important functions: `nbio_v7_9_handle_ras_controller_intr_no_bifring()` reads `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, checks the RAS controller interrupt status bit, sets the clear bit, and writes it back. A TODO remains for controller interrupt handling. `nbio_v7_9_handle_ras_err_event_athub_intr_no_bifring()` clears ATHUB error-event interrupt status and calls `ras_core_handle_fatal_error()`. `nbio_v7_9_get_memory_partition_mode()` reads `regBIF_BX_PF0_PARTITION_MEM_STATUS`, extracts the NPS mode mask, and returns `ffs(mem_mode)`. `ras_nbio_v7_9` exports the handlers.

Control flow and state: this file is stateless; all effects are MMIO register reads/writes and fatal-error notification. No persistence exists.

Dependencies and integration: it uses SOC15 register access macros, field macros, and core fatal handling. UMC hardware init depends on the NPS mode value returned here. Risks include the controller interrupt TODO, assuming `ffs()` of the NPS bitmask maps directly to NPS mode, missing synchronization around interrupt clear, and fatal handling during reset. Test signals should mock register values for no interrupt, controller interrupt, ATHUB interrupt, combined bits, invalid/zero NPS mode, and verify clear-bit writes plus fatal notification.
