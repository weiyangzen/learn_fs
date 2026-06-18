# sources/distributed-fs/ceph-client/include/uapi/linux/mptcp.h

## Purpose
Defines Multipath TCP socket option ABI for connection info, subflow flags/addrs, full info buffers, reset reason codes, path-manager names, endpoint flags, and socket option IDs.

## Important APIs, Types, And Functions
Exports `mptcp_info`, subflow flag macros, PM event/address flags, reset reason constants, `mptcp_subflow_data`, `mptcp_subflow_addrs`, `mptcp_subflow_info`, `mptcp_full_info`, and socket options `MPTCP_INFO`, `MPTCP_TCPINFO`, `MPTCP_SUBFLOW_ADDRS`, `MPTCP_FULL_INFO`.

## Control Flow
Userspace calls `getsockopt` on MPTCP sockets. Simple info returns `mptcp_info`; full info uses size fields and user pointers for arrays of subflow and TCP info. Kernel writes actual counts and structure sizes for compatibility.

## State, Persistence, And Dependencies
State is live MPTCP connection and subflow state inside the kernel. Depends on socket, IPv4/IPv6 address, const, types, and `linux/mptcp_pm.h`.

## Integration Points
Used by MPTCP-aware diagnostics, network managers, tests, and path-management tooling.

## Risks
Several fields preserve old names via macros and include holes that must not be repurposed casually. Full-info pointers and size fields need careful 32/64-bit compatibility and bounds checking.

## Test Signals
Validate `getsockopt` size negotiation, fallback and key-received flags, subflow count/address reporting, full-info truncation behavior, reset reason exposure, and endpoint flag masks.
