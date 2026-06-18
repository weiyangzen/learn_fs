# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ptp.h

## Purpose
Declares the IAVF PTP interface used by the main driver, virtchnl control plane, and Tx/Rx data path. It also provides no-op or error stubs when PTP clock support is not compiled into the kernel.

## Important APIs, Types, and Functions
The header declares `iavf_ptp_init`, `iavf_ptp_release`, `iavf_ptp_process_caps`, `iavf_ptp_cap_supported`, `iavf_virtchnl_send_ptp_cmd`, `iavf_ptp_set_ts_config`, and `iavf_ptp_extend_32b_timestamp`. `IAVF_PTP_40B_TSTAMP_VALID` defines the valid bit used when extracting flexible Rx descriptor timestamp data.

## Control Flow
There is no runtime control flow beyond conditional compilation. With `CONFIG_PTP_1588_CLOCK`, callers bind to real implementations in `iavf_ptp.c` and `iavf_virtchnl.c`. Without it, initialization/release/capability processing are no-ops, capability checks return false, timestamp configuration returns failure, and timestamp extension returns zero.

## State and Persistence
The header owns no mutable state. It defines the compile-time contract that controls whether `adapter->ptp` state is active and whether virtchnl PTP commands can be sent.

## Dependencies and Integration Points
Includes `iavf_types.h` for `struct iavf_adapter` and PTP-related adapter state. It is included by PTP implementation, virtchnl code, main netdev setup, and Tx/Rx code that needs Rx timestamp extension.

## Risks
The stub `iavf_ptp_set_ts_config` returns `-1` instead of a symbolic errno, so callers should not depend on a specific disabled-PTP errno. Build coverage must ensure all call sites compile in both PTP-enabled and PTP-disabled configurations. The timestamp valid bit must match the hardware descriptor ABI used by `iavf_txrx.c`.

## Test Signals
Compile with and without `CONFIG_PTP_1588_CLOCK`, verify `ethtool -T` and hwtstamp operations report unavailable behavior without PTP, and check that Rx timestamp code is either inactive or correctly linked depending on the config.
