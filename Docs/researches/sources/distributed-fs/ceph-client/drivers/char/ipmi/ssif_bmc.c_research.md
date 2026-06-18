<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ssif_bmc.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ssif_bmc.c

## Purpose
Implements the BMC-side SSIF I2C slave driver. It exposes a misc character device for userspace IPMI service code, receives host SSIF write transactions into request messages, accepts userspace response messages, and serves them back through single- or multipart SMBus reads with optional PEC.

## Important APIs, Types, and Functions
- `struct ssif_part_buffer` stores one SMBus transaction part, including address, command, length, payload, PEC, and index.
- `enum ssif_state` models SSIF slave transaction phases from ready through receiving, sending, and aborting.
- `struct ssif_bmc_ctx` stores I2C client, miscdev, locks, waitqueue, timer, request/response buffers, multipart counters, and flags.
- File operations `ssif_bmc_read()`, `ssif_bmc_write()`, `ssif_bmc_open()`, `ssif_bmc_poll()`, and `ssif_bmc_release()` form the userspace ABI.
- I2C slave callback `ssif_bmc_cb()` dispatches to event handlers for read requested/processed, write requested/received, and stop.
- KUnit tests under `CONFIG_SSIF_IPMI_BMC_KUNIT_TEST` exercise state-machine edge cases.

## Control Flow
Host write events move through start, command, receive, and stop. A valid singlepart or multipart end calls `handle_request()`, marks a request available, wakes userspace, sets busy, and arms a response timeout. Userspace reads the request and writes a response before timeout; the response is then served to host read transactions by `set_singlepart_response_buffer()` or `set_multipart_response_buffer()`. Stop after final response part calls `complete_response()`. Invalid PEC, unexpected event order, timeout, or protocol interruption moves to aborting until a new valid start.

## State and Persistence
Per-device state is in `ssif_bmc_ctx` protected by a spinlock. Userspace waiters use `wait_queue`. A response timer recovers from userspace not providing a response. `running` enforces single opener. Request/response buffers persist until consumed or invalidated.

## Dependencies and Integration Points
Depends on I2C slave support, miscdevice, `linux/ipmi_ssif_bmc.h`, OF compatible `ssif-bmc`, and optional KUnit. It presents device name `ipmi-ssif-host`.

## Risks
The state machine handles many interrupted-transaction cases and must return `-EBUSY` to the I2C core while waiting for userspace. PEC validation and multipart length accounting are security-sensitive because the host controls transaction bytes. Userspace response timeout changes state asynchronously and can race with write attempts.

## Test Signals
Built-in KUnit cases cover singlepart request, restart without stop, restart after invalid command, singlepart response completion with PEC, stop during start, read/write interruptions, and timeout retry. Additional integration tests should cover multipart request/response and real I2C slave controller behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ssif_bmc.c -->
