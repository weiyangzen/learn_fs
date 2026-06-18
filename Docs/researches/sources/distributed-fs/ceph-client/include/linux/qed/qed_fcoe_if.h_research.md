# sources/distributed-fs/ceph-client/include/linux/qed/qed_fcoe_if.h

Purpose: declares the public QED FCoE client interface used by FCoE upper layers to start firmware resources, acquire/offload/destroy FCoE connections, access LL2, and collect FCoE stats.

Important APIs/types/functions: `qed_fcoe_stats` mirrors RX/TX FCoE counters and silent-drop reasons. `qed_dev_fcoe_info` returns common device info, primary/secondary BDQ request queue addresses, WWPN/WWNN, and CQ count. `qed_fcoe_params_offload` carries SQ page addresses, MACs, FC payload/timer values, VLAN tag, FC source/destination IDs, flags, and default queue. `qed_fcoe_tid` describes firmware task blocks. `qed_fcoe_cb_ops` extends common callbacks with `get_login_failures`. `qed_fcoe_ops` exposes `fill_dev_info`, `register_ops`, `ll2`, `start`, `stop`, `acquire_conn`, `release_conn`, `offload_conn`, `destroy_conn`, and `get_stats`; `qed_get_fcoe_ops()`/`qed_put_fcoe_ops()` manage ops access.

Control flow: a client obtains FCoE ops, registers callbacks, reads device info, starts FCoE with a task-block descriptor, optionally uses LL2 for FIP/control traffic, acquires a firmware connection handle/doorbell, offloads connection parameters, posts protocol work through its rings, destroys the connection with termination parameters, releases the handle, and stops FCoE.

State and persistence: connection handles, firmware CIDs, doorbell addresses, task blocks, and BDQ/CQ resources persist while FCoE is started and each connection is active. Stats persist until reset or restart. FC login/session durability is handled by upper layers, not by this header.

Dependencies and integration points: includes `qed_if.h` and uses `fc_addr_nw` from FCoE common definitions through transitive include expectations. Integrates QED core with FCoE storage drivers, LL2 packet path, firmware task memory, Fibre Channel identifiers, and management firmware TLV reporting.

Risks: caller-owned task blocks and PBL addresses must remain DMA-valid. Incorrect WWN/FC ID/MAC/VLAN/timer values prevent fabric login or data exchange. The ops table assumes `ll2` is available and configured for control traffic. `destroy_conn` termination DMA address lifetime is a common failure point.

Test signals: FCoE start/stop, task block sizing, FIP login, connection acquire/offload/release, FC read/write, ABTS/termination, LL2 control packet send/receive, login failure reporting, stats counters for RX/TX and silent-drop reasons, and module get/put lifecycle.
