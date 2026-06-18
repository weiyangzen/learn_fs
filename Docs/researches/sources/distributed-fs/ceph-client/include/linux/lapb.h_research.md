# sources/distributed-fs/ceph-client/include/linux/lapb.h

Purpose: declares the kernel-facing LAPB module interface for network devices using Link Access Procedure Balanced framing.

Important APIs and types: status codes (`LAPB_OK`, `LAPB_BADTOKEN`, etc.), mode bits (`LAPB_STANDARD`, `LAPB_EXTENDED`, `LAPB_SLP`, `LAPB_MLP`, `LAPB_DTE`, `LAPB_DCE`), `struct lapb_register_struct` callback table, and `struct lapb_parms_struct` timer/window/state parameters are exported. Public functions register/unregister a `net_device`, get/set parameters, request connect/disconnect, send data, and feed received skb data.

Control flow: a lower network driver registers callbacks, asks LAPB to establish or tear down a link, passes received frames through `lapb_data_received()`, and receives data/control indications through callbacks.

State and persistence: protocol state is held by the LAPB module per registered net_device: timers, retry counts, window, and connection state. The header only defines the ABI.

Dependencies and integration points: depends on `sk_buff`, timers, and `net_device`; integrates with WAN/X.25-style networking drivers.

Risks and test signals: risks include callback lifetime after unregister, invalid timer/window parameters, skb ownership mistakes, and state-machine regressions. Test connect/disconnect paths, timeout/retry behavior, extended vs standard mode, DTE/DCE modes, and unregister with queued timers.
