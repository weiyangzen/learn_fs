# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.h

## Purpose
Declares shared constants, address metadata, and client/server helper interfaces for the ZOID BMI method.

## Important APIs, Types, And Functions
Defines `ZOID_MAX_EXPECTED_MSG`, `ZOID_MAX_UNEXPECTED_MSG`, `ZOID_ADDR_SERVER_PID`, and `struct zoid_addr { int pid; }`. It declares the global `zoid_method_id`, server lifecycle and memory functions, unexpected-message testing/freeing, common server send/recv/test helpers, cancellation, and client address cleanup.

## Control Flow
`zoid.c` uses this header to route BMI callbacks to server helpers when initialized as a server. The address struct lets `method_addr_lookup` and client post paths assert that string address `zoid://` targets the single server endpoint.

## State And Persistence
The header defines no storage itself, but it fixes the in-memory address payload attached to `bmi_method_addr`. Message-size constants are behavioral limits for all users of the method.

## Dependencies And Integration Points
The prototypes depend on BMI types such as `bmi_op_id_t`, `bmi_method_addr_p`, `bmi_size_t`, `bmi_context_id`, `bmi_msg_tag_t`, and `PVFS_hint`. It is the ABI between `zoid.c` and the ZOID server implementation.

## Risks And Test Signals
Main risks are declaration drift with server implementation and incorrect assumptions around the only valid pid value. Build coverage of `bmi_zoid`, max-size query tests, and address lookup/free tests are the useful signals.
