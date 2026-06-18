# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.c

## Purpose
Implements Precision Time Protocol support for the Intel IAVF virtual function driver when `CONFIG_PTP_1588_CLOCK` is enabled. Because the VF does not directly own the physical hardware clock, the file exposes a PTP clock to userspace by sending virtchnl requests to the PF, caches PHC time for timestamp extension, and controls Rx hardware timestamp reporting on Rx rings.

## Important APIs, Types, and Functions
The exported entry points are `iavf_ptp_init`, `iavf_ptp_release`, `iavf_ptp_process_caps`, `iavf_ptp_cap_supported`, `iavf_ptp_set_ts_config`, and `iavf_ptp_extend_32b_timestamp`. Internal helpers include `iavf_ptp_set_timestamp_mode`, `iavf_send_phc_read`, `iavf_read_phc_indirect`, `iavf_ptp_gettimex64`, `iavf_ptp_register_clock`, `iavf_ptp_cache_phc_time`, and `iavf_ptp_do_aux_work`. `iavf_clock_to_adapter` maps `ptp_clock_info` back to `struct iavf_adapter`.

## Control Flow
Capability-gated initialization checks `VIRTCHNL_1588_PTP_CAP_READ_PHC`, registers a `ptp_clock_info`, points every active Rx ring at `adapter->ptp`, and schedules auxiliary PTP work. Userspace PHC reads call `gettimex64`, which queues `VIRTCHNL_OP_1588_PTP_GET_TIME`, waits up to one second on `phc_time_waitqueue`, and returns `cached_phc_time` after the virtchnl completion path fills it. Timestamp configuration accepts Rx timestamp filters, normalizes any supported Rx filter to `HWTSTAMP_FILTER_ALL`, rejects Tx timestamping, and flips `IAVF_TXRX_FLAGS_HW_TSTAMP` on all active Rx rings. Auxiliary work refreshes PHC time roughly twice per second, while `iavf_ptp_extend_32b_timestamp` combines cached 64-bit PHC time with 32-bit descriptor timestamps.

## State and Persistence
Persistent driver state lives in `adapter->ptp`: registered PTP clock pointer, `ptp_clock_info`, PF-reported capabilities, cached PHC nanoseconds, cache update jiffies, current `kernel_hwtstamp_config`, command queue, waitqueue, and `phc_time_ready`. Per-ring timestamp state is represented by `rx_ring->ptp` and `IAVF_TXRX_FLAGS_HW_TSTAMP`. No state is written to disk; hardware-visible changes are mediated by virtchnl messages and queue configuration.

## Dependencies and Integration Points
Depends on `iavf_ptp.h`, `iavf_types.h`, the kernel PTP clock API, virtchnl 1588 opcodes, watchdog/AQ scheduling through `adapter->aq_required`, and the completion logic in `iavf_virtchnl.c`. Rx timestamp delivery integrates with `iavf_txrx.c` flexible descriptor parsing, which calls `iavf_ptp_extend_32b_timestamp`. Netdev hardware timestamp ioctls enter through `iavf_main.c` and call `iavf_ptp_set_ts_config`.

## Risks
The indirect PHC read path can return `-EBUSY` if the PF response does not arrive within one second, so PHC reads are latency-sensitive to AdminQ health. Timestamp extension is only correct when cached PHC time is close to the descriptor event; stale auxiliary work or PF communication stalls can produce wrong 64-bit timestamps. Capability changes during reset must release or recreate the PTP clock without leaving queued commands, and Rx timestamp enabling touches ring flags without per-ring locking, relying on driver serialization around configuration. Tx hardware timestamping is explicitly unsupported.

## Test Signals
Useful signals include `ptp4l` or `phc2sys` PHC reads against a VF with PTP capability, `ethtool -T`, `hwtstamp_config` set/get for Rx filters, reset while PTP is enabled, PF capability loss and regain, AdminQ timeout injection for `GET_TIME`, Rx timestamp validation on flexible descriptors, and checking that timestamping is disabled after `iavf_ptp_release`.
