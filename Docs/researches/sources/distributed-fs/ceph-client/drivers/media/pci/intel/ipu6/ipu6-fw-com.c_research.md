# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.c

## Purpose
This file implements the generic IPU6 firmware communication layer. It allocates shared queue memory, builds firmware syscom configuration, starts/stops the firmware communication cell, and provides ring-token operations for host-to-firmware and firmware-to-host queues.

## Important APIs, types, and functions
Internal ABI structs are `ipu6_fw_sys_queue`, `ipu6_fw_sys_queue_res`, and `ipu6_fw_syscom_config`; they describe queue buffers and DMEM read/write index registers. `ipu6_fw_com_prepare()` builds one DMA allocation containing config, queue descriptors, firmware-specific config, and queue token storage. `ipu6_fw_com_open()` writes TUnit magic, syscom command/state boot parameters, config address, and starts the cell. `ipu6_fw_com_ready()`, `ipu6_fw_com_close()`, and `ipu6_fw_com_release()` manage lifecycle. `ipu6_send_get_token()/put_token()` and `ipu6_recv_get_token()/put_token()` implement lockless ring access using DMEM indices.

## Control flow and integration points
ISYS creates an `ipu6_fw_com_cfg` with queue sizes, specific firmware config, DMEM base, and callbacks. Prepare lays out memory and syncs it through `ipu6_dma_sync_single()`. Open writes boot parameters in buttress firmware parameter registers and calls the subsystem-specific start callback. Runtime command paths reserve a send token, fill it, and advance the write index; interrupt/response paths read a receive token and advance the read index.

## State, persistence, and dependencies
`struct ipu6_fw_com_context` owns the DMA buffer, IPU6 IOVA, queue descriptor arrays, DMEM base, config address, callbacks, and boot-parameter offset. The state persists while firmware communication is open. Dependencies include IPU6 DMA helpers, MMIO access, subsystem `cell_ready`/`cell_start` callbacks, and firmware syscom ABI state/command constants.

## Risks and test signals
Risks include queue layout mismatches with firmware, missing overflow checks in aggregate sizes, stale cache for config/specific data, invalid ring indices, release while firmware still running, and queue full/empty races. Test signals include ISYS firmware reaching READY, stream commands producing responses, queue wraparound, no WARN on DMEM indices, successful close/release, and firmware command timeouts only on deliberate fault injection.
