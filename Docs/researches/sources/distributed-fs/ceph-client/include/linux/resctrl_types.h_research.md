# sources/distributed-fs/ceph-client/include/linux/resctrl_types.h

Purpose: this header holds small shared resctrl constants and event IDs that are needed outside the larger internal/core resctrl header.

Important APIs/types/functions: constants include `MAX_MBA_BW`, `MBM_OVERFLOW_INTERVAL`, configurable MBM transaction bits (`READS_TO_LOCAL_MEM`, `READS_TO_REMOTE_MEM`, non-temporal writes, slow-memory reads, dirty victims), `MAX_EVT_CONFIG_BITS`, and `NUM_MBM_TRANSACTIONS`. `enum resctrl_event_id` defines QoS events for L3 occupancy, total/local MBM bandwidth, and Intel telemetry events. Macros include `QOS_NUM_L3_MBM_EVENTS` and `MBM_STATE_IDX(evt)`.

Control flow: resctrl monitor and architecture code uses event IDs to enable, configure, read, and index monitoring counters. MBM bitmasks constrain user-visible event configuration and architecture programming.

State and persistence: no state is owned here. The constants define indexes into persistent state arrays such as MBM state tables and architecture counter assignment records.

Dependencies and integration points: used by `resctrl.h`, x86 RDT, Arm MPAM-style support, resctrl FS monitor code, and telemetry support.

Risks: enum values for `QOS_L3_*` must match hardware programming values on RDT systems. Adding events changes `QOS_NUM_EVENTS` and may affect array sizing. Test signals include build coverage across architectures, MBM event configuration tests, event-to-index tests for `MBM_STATE_IDX()`, and counter reads for all enabled events.
