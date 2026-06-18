<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsvc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmsvc.h

## Purpose
Defines the ATM signaling daemon control socket ABI used between kernel SVC code and `atmsigd`.

## Important APIs, Types, And Functions
`ATMSIGD_CTRL` registers the signaling daemon control socket. `enum atmsvc_msg_type` defines bind/connect/accept/reject/listen/okay/error/indicate/close/modify/identify/terminate/addparty/dropparty messages. `struct atmsvc_msg` carries VCC tokens, reply code, PVC/SVC addresses, QoS, SAP, and session id. `SELECT_TOP_PCR` chooses a PCR value from traffic parameters.

## Control Flow
Kernel SVC code sends requests/indications to atmsigd; the daemon resolves signaling, returns okay/error/close or call-control messages, and includes QoS/SAP/address state. Point-to-multipoint operations use add/drop party messages.

## State And Persistence
State includes active/listening VCC tokens, signaling sessions, call addresses, QoS/SAP negotiations, and pending replies. It is runtime call-control state.

## Dependencies And Integration Points
Depends on ATM API/core/ioctl headers. Integrates with atmsigd, ATM UNI signaling, SVC sockets, and QoS policy.

## Risks And Edge Cases
Opaque VCC token lifetime, positive vs negative reply semantics, daemon crash/termination, p2mp session handling, and PCR selection policy must match kernel and daemon.

## Test Signals
Daemon registration, bind/connect/listen/accept/reject/close flows, add/drop party, modify QoS, daemon termination recovery, and malformed message handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsvc.h -->
