# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.h

## Purpose
`qat_algs_send.h` defines the shared request and backlog structures used by QAT algorithm implementations to submit firmware messages to ETR rings with Crypto API backlog support.

## Important APIs, Types, And Functions
`struct qat_instance_backlog` contains a list head and spinlock. `struct qat_alg_req` contains the firmware request pointer, TX ring pointer, base Crypto API async request, list node, and backlog pointer. It declares `qat_alg_send_message()` and `qat_alg_send_backlog()`.

## Control Flow
The header has no executable flow. Algorithm code fills `qat_alg_req` immediately before submission, then the implementation either sends directly or links it onto the instance backlog. Completion callbacks drain the same backlog.

## State And Persistence Behavior
The backlog persists per QAT crypto/compression instance. `qat_alg_req` persists inside a single in-flight or queued operation. The list node is valid only while the original Crypto API request remains alive.

## Dependencies And Integration Points
It includes list support and transport internals for `adf_etr_ring_data`. It integrates common submission behavior across symmetric LA, PKE, and data-compression rings.

## Risks
The header exposes raw `u32 *fw_req` and ring pointers; callers must ensure the request buffer matches the ring's message size and remains stable while queued. All users sharing one backlog can affect each other's latency.

## Test Signals
Compile coverage validates structure availability. Runtime backlog tests across symmetric, PKE, and compression services validate shared behavior.
