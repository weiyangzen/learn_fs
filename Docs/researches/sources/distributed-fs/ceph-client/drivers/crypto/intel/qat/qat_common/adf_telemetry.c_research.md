# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.c

Purpose: implements common telemetry lifecycle and data collection. It allocates firmware DMA telemetry memory, starts/stops telemetry admin commands, snapshots changing counters into history buffers, and provides state used by debugfs readers.

Important APIs: `adf_tl_init`, `adf_tl_start`, `adf_tl_run`, `adf_tl_halt`, `adf_tl_stop`, and `adf_tl_shutdown`. Helpers validate hardware data, allocate/free memory, snapshot registers, and compute command-queue counts from slice counts and hardware multipliers.

Control flow and state: init validates `adf_tl_hw_data`, allocates `struct adf_telemetry`, RP index array, history buffers, and coherent DMA layout. Run sends admin TL start with DMA address and RP indexes, validates returned slice counts, computes cmdq counts, sets `state` and history depth, then queues delayed work. Work handler checks message count, snapshots DMA data under lock when changed, handles race by resnapshotting if count changes mid-copy, advances ring buffer, and requeues. Halt cancels work, clears state, and sends admin stop.

Dependencies and integration: uses admin telemetry commands, misc workqueue, Gen-specific `adf_tl_hw_data`, and debugfs control/data files.

Risks and test signals: cancellation inside worker and external halt must avoid deadlock; state controls history sample count. Test unsupported FW capability, invalid slice counts, TL start/stop/restart, RP selection, history aggregation, and shutdown after active telemetry.
