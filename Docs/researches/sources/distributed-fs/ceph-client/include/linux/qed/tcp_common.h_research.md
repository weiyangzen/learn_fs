# sources/distributed-fs/ceph-client/include/linux/qed/tcp_common.h

Purpose: provides firmware-facing TCP offload data contracts for QED storage/network offload flows, including connection setup, update, upload, timers, and out-of-order placement metadata.

Important APIs and types: `struct ooo_opaque` carries LL2 out-of-order placement metadata. `enum tcp_connect_mode`, `enum tcp_ip_version`, and `enum tcp_seg_placement_event` classify connection role, IPv4/IPv6, and segment placement actions. `struct tcp_init_params` sets global timers. `struct tcp_offload_params` and `struct tcp_offload_params_opt2` encode MAC/VLAN/IP/port tuple, offload flags, flow label, TTL/TOS, MSS, window scales, RTT/cwnd/sequence state, keepalive and retransmission timers, delayed-ACK/Nagle/ECN flags, and optional SYN payload DMA. `struct tcp_update_params` carries changed-field flags and replacement values. `struct tcp_upload_params` exports firmware TCP state back to the host.

Control flow: a connection starts with init/offload parameters programmed into firmware; later parameter changes are sent through `tcp_update_params`; teardown or fallback can upload TCP sequence/window/timer state to the host stack. OOO metadata guides segment placement and drop decisions.

State and persistence: state lives in firmware connection contexts and host command buffers: sequence numbers, windows, timers, congestion-control variables, keepalive counters, and placement counters. It is runtime state reconstructed or uploaded during offload transitions.

Dependencies and integration points: integrates QED firmware with TCP offload consumers such as iSCSI. It depends on endian-specific integer layout and QED bitfield conventions.

Risks and test signals: risks include invalid byte order, stale sequence/window state on upload, incorrect changed-field flags, IPv6 address array ordering, keepalive/retransmission timer drift, and mismatch between `opt2` and full offload formats. Test active/passive connections, IPv4/IPv6, ECN/Nagle/keepalive toggles, MTU/MSS changes, retransmission and keepalive timeouts, OOO placement, and offload-to-host upload correctness under packet loss.
