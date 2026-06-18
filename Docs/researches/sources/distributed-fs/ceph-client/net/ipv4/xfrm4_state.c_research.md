# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_state.c

## Purpose
This file registers IPv4 address-family callbacks for XFRM state handling. It connects IPv4 state objects to IPv4 output, transport-finish, and local-error functions.

## Important APIs, Types, and Functions
The central object is `xfrm4_state_afinfo`, with family `AF_INET`, tunnel protocol `IPPROTO_IPIP`, `output = xfrm4_output`, `transport_finish = xfrm4_transport_finish`, and `local_error = xfrm4_local_error`. `xfrm4_state_init()` registers it through `xfrm_state_register_afinfo()`.

## Control Flow
Initialization is called from `xfrm4_init()` before policy/protocol registration. After registration, XFRM core can call back into IPv4-specific output and input finishing paths for IPv4 states.

## State and Persistence Behavior
Persistent state is the registered AF info in XFRM core. This file owns no dynamic memory and has no teardown path in this source.

## Dependencies and Integration Points
It depends on XFRM core registration and sibling IPv4 XFRM functions in `xfrm4_output.c` and `xfrm4_input.c`.

## Risks
The file is small, but incorrect callback wiring would break all IPv4 XFRM state output/input completion or local PMTU error reporting. Protocol mismatch would affect IPIP tunnel-mode handling.

## Test Signals
Boot-time XFRM IPv4 initialization, IPv4 ESP/AH state output, transport-mode finish, local EMSGSIZE delivery, and IPIP tunnel-mode state setup indirectly validate this file.
