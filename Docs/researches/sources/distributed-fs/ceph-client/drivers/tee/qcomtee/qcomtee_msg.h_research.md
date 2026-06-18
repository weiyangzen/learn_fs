<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_msg.h -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_msg.h

## Purpose

`qcomtee_msg.h` defines the Qualcomm TEE transport message ABI used in shared inbound and outbound buffers. It documents object IDs, argument layouts, count packing, callback message formats, service operation constants, QTEE version decoding, and conversion from Linux errors to QTEE message results.

## Important APIs, Types, and Functions

`QCOMTEE_MSG_OBJECT_NS_BIT` marks kernel-hosted object IDs. Static QTEE IDs are `QCOMTEE_MSG_OBJECT_NULL` and `QCOMTEE_MSG_OBJECT_ROOT`. `union qcomtee_msg_arg` encodes either a buffer `(offset, size)` pair or object ID. `struct qcomtee_msg_object_invoke` encodes direct calls, while `struct qcomtee_msg_callback` encodes secure-world callback requests and responses.

Count masks (`QCOMTEE_MASK_IB`, `OB`, `IO`, `OO`) and inline helpers compute per-kind counts, starting indexes, total args, and iteration ranges. `qcomtee_msg_init()` packs cumulative argument counters into four 4-bit fields. `qcomtee_msg_buffer_args()` and `qcomtee_msg_offset_to_ptr()` locate buffer payloads after the variable argument array. The header also defines reserved object operations RELEASE/RETAIN, root/client-env/feature service operation IDs, transport result constants, and `qcomtee_msg_set_result()`.

## Control Flow

`core.c` uses this ABI when preparing direct invocation messages in inbound shared memory, parsing final direct-call responses, parsing callback requests in outbound shared memory, and writing callback responses back into the outbound buffer. Arguments are ordered by kind: input buffers, output buffers, input objects, and output objects. Buffer payloads are stored after the message header/argument table and aligned to 64-bit boundaries.

## State and Persistence Behavior

The header is declarative and owns no persistent state. Message structures are transient contents of per-invocation TEE shared-memory buffers. The constants define the stable ABI that both Linux and QTEE must interpret identically across each invocation.

## Dependencies and Integration Points

The header depends on Linux bitfield helpers and is included by `qcomtee_object.h` and `qcomtee.h`. Its root and feature-service constants are used by `call.c` and `core.c`, while error mappings are used during callback response submission. The ABI is also coupled to Qualcomm SCM calls that receive physical addresses and sizes for inbound/outbound buffers.

## Risks and Edge Cases

Each argument-kind count is 4 bits, so callers must enforce the 16-per-kind maximum before calling `qcomtee_msg_init()`. The initializer expects cumulative indexes rather than independent counts, which is compact but easy to misuse. Message parsing assumes QTEE-provided offsets and sizes are within the allocated buffers; allocation code bounds Linux-originated messages, but response/callback offsets from QTEE deserve careful validation. Error mapping collapses many Linux errors into generic QTEE result codes, which can hide actionable failure causes.

## Test Signals

ABI tests should verify count packing/unpacking, argument index calculations for mixed argument lists, 64-bit buffer alignment, struct header sizes, maximum per-kind limits, reserved operation values, root/feature service constants, version decoding macros, and `qcomtee_msg_set_result()` mappings for common kernel errors and user-defined positive errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_msg.h -->
