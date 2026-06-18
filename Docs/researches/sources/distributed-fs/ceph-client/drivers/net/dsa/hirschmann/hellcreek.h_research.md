# sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek.h

Purpose: this header defines the Hellcreek switch register map, port constants, TSN/Qbv register bits, devlink structures, and private state shared by the main driver, PTP clock code, and hardware timestamping code.

Important APIs, types, and functions: constants define CPU and tunnel ports, VLAN membership encodings, egress queue count, default max SDU, switch-core registers (`HR_*`) and TSN gate registers (`TR_*`). Core types include `struct hellcreek_counter`, `struct hellcreek_port_hwtstamp`, `struct hellcreek_port`, `struct hellcreek_fdb_entry`, `struct hellcreek`, and `struct hellcreek_devlink_vlan_entry`. Macros such as `dw_to_hellcreek_port()` support delayed schedule work ownership.

Control flow: C files use the register definitions to select ports, VLANs, counters, FDB entries, and time-gate domains, and use the shared structs to coordinate DSA operations, PTP overflow work, LED state, per-port timestamp queues, and TAPRIO delayed work.

State and persistence: the header defines the complete driver state layout: platform data, DSA switch, PTP clock and clock info, per-port array, overflow work, LEDs, three mutexes, devlink regions, TSN and PTP MMIO bases, software shadows for switch config, VLAN membership, PTP seconds/last timestamp, status outputs, and FDB size. Per-port state includes VLAN-device bitmap, port config shadow, counters, hwtstamp state, current schedule, and delayed work.

Dependencies and integration points: it includes bitmap/bitops/device/LED/mutex/PTP/timecounter/workqueue types, Hellcreek platform data, DSA, and packet scheduler TAPRIO definitions. It is the common local ABI for `hellcreek.c`, `hellcreek_ptp.c`, and `hellcreek_hwtstamp.c`.

Risks: register bit definitions are hardware ABI and many fields are selected indirectly through current port/priority/VLAN/TGD selectors, so callers must serialize and program selectors correctly. The PTP and TSN schedule code share time state through `ptp_lock`. A typo in `TR_EETCMD_EETSEC_MASK` uses `GEMASK`, which would be compile-sensitive if that macro path is used.

Test signals: build coverage of all Hellcreek files, correct struct sharing across object boundaries, register programming validation for FDB/VLAN/Qbv/PTP, lockdep coverage for `reg_lock`, `vlan_lock`, and `ptp_lock`, and devlink snapshot structure size compatibility.
