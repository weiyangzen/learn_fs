# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.h

## Purpose
`qedr_roce_cm.h` declares the QEDR RoCE GSI connection-management and special-QP helper interface used by the verbs implementation and QEDR main logic.

## Important APIs, Types, And Functions
It defines GSI limits (`QEDR_GSI_MAX_RECV_WR`, `QEDR_GSI_MAX_SEND_WR`, `QEDR_GSI_MAX_RECV_SGE`), RoCEv2 UDP source port constant `QEDR_ROCE_V2_UDP_SPORT`, helper `qedr_get_ipv4_from_gid`, and prototypes for GSI poll/post/create/destroy/store functions.

## Control Flow
Only `qedr_get_ipv4_from_gid` has executable behavior: it reads the IPv4 address bytes from the last four bytes of an IPv4-mapped GID. The rest of the header provides declarations consumed by `qedr_roce_cm.c` and verbs code.

## State And Persistence Behavior
The header has no state. Constants define resource limits enforced during GSI QP creation and receive posting.

## Dependencies And Integration Points
The prototypes reference RDMA core CQ/QP/WR types and QEDR private device/QP/CQ types from including files. The header has an include guard and is the contract between GSI-special handling and the generic QEDR verbs implementation.

## Risks And Test Signals
Risks include unaligned or aliasing-sensitive access in `qedr_get_ipv4_from_gid`, stale GSI limits versus LL2 firmware capability, and prototype drift. Test signals include builds with strict warnings, RoCEv2 IPv4 GID send tests, and GSI QP creation tests at boundary WR/SGE values.
