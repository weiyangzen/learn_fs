# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_control.c

Purpose: implements the QAIC management/control plane over the `QAIC_CONTROL` MHI channel. It converts UAPI `qaic_manage_msg` transaction arrays into the device wire protocol, sends them with sequence numbers and optional CRC, waits for paired responses, and applies local side effects for DBC activation, deactivation, DMA-continuation, and user teardown.

Important APIs and types: exported entry points are `qaic_manage_ioctl`, `get_cntl_version`, `qaic_mhi_ul_xfer_cb`, `qaic_mhi_dl_xfer_cb`, `qaic_control_open`, `qaic_control_close`, `qaic_release_usr`, and `wake_all_cntl`. Key internal types are `wire_msg`, `wire_trans_*`, `wrapper_msg`, `wrapper_list`, `xfer_queue_elem`, `dma_xfer`, and `ioctl_resources`.

Control flow: encode helpers validate user transaction lengths and translate passthrough, DMA, activate, deactivate, and status transactions. `qaic_manage_msg_xfer` builds wrappers, fills message header fields, queues one RX buffer and chained TX buffers through MHI, and blocks until `resp_worker` matches the response sequence. Large DMA payloads use `QAIC_TRANS_DMA_XFER_CONT` loops until the device acknowledges the transferred byte count. Decode helpers copy response transactions back to userspace and commit local state such as saving activated DBC queues or releasing deactivated DBCs.

State and persistence: persistent kernel state lives in `qaic_device` and `dma_bridge_chan`: control sequence numbers, queued control waits, CRC policy, lost RX buffer flag, DBC coherent queues, DBC ownership, and DBC sysfs state. The file does not persist state across module unload or device reset.

Dependencies and integration: depends on MHI, PCI DMA mapping, user page pinning, DRM file private data, SRCU locks from `qaic.h`, and QAIC UAPI transaction layouts. It is opened by the main MHI control probe in `qaic_drv.c` and drives datapath DBC ownership used by `qaic_data.c`.

Risks and test signals: high-risk areas are wrapper lifetime across async MHI callbacks, lost RX buffer handling after TX queue failure, DMA page pin cleanup, CRC negotiation, timeout cleanup, and late deactivate responses after a userspace waiter disappeared. Test with malformed transaction lengths/counts, CRC-on/off firmware, DMA-continuation larger than 64 KiB wire messages, user signal interruption, activate/deactivate races, module removal during waits, and MHI TX/RX fault injection.
