# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_types.h

## Purpose
Defines PTP-specific IAVF state containers that are shared between PTP implementation, virtchnl command dispatch, and Rx timestamp processing.

## Important APIs, Types, and Functions
`struct iavf_ptp_aq_cmd` is a flexible-array command wrapper containing a list node, virtchnl opcode, message length, and message payload. `struct iavf_ptp` stores the PTP waitqueue, PF-advertised `virtchnl_ptp_caps`, `ptp_clock_info`, registered `ptp_clock`, queued PTP AQ commands, cached PHC time, cache update timestamp, AQ command mutex, current hardware timestamp configuration, and `phc_time_ready` flag.

## Control Flow
The header has no executable control flow. `iavf_ptp.c` allocates and queues `iavf_ptp_aq_cmd` objects, while `iavf_virtchnl.c` dequeues and sends them, then updates `struct iavf_ptp` when PF responses arrive.

## State and Persistence
All state is in-memory adapter state. `aq_cmds` persists queued virtchnl PTP work until sent or released. `cached_phc_time` and `cached_phc_updated` persist the latest PF-reported PHC reading for Rx timestamp extension. `hwtstamp_config` persists the last accepted userspace timestamp mode.

## Dependencies and Integration Points
Includes the base `iavf_types.h` header, virtchnl definitions, and `<linux/ptp_clock_kernel.h>`. This unusual self-include is protected by the include guard, allowing the file to layer PTP-specific definitions while sharing the historical header name. Integrated by `iavf_ptp.h`, PTP code, virtchnl code, and adapter initialization in `iavf_main.c`.

## Risks
The command flexible array depends on correct `msglen` allocation and lifetime management. `cached_phc_time` is read in the Rx path while updated in virtchnl completion, so correctness depends on simple atomic-width access and freshness rather than complex locking. Initialization of list head, waitqueue, and mutex must happen before any PTP command can be queued.

## Test Signals
Compile with PTP enabled, run probe/remove with PTP capability, validate queued command cleanup during `iavf_ptp_release`, check PHC read wait/wakeup behavior, and test reset paths that reinitialize or clear PTP capabilities.
