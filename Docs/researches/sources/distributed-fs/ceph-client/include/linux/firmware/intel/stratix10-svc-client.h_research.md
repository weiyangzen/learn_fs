# sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-svc-client.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-svc-client.h` declares the client-facing Stratix 10 service layer API for FPGA configuration, RSU, FCS, HWMON, mailbox commands, and asynchronous transactions. The source was read as a complete 392-line file for this report.

## Important APIs, Types, and Functions

Important definitions include service client names, service status codes, timeout constants, `enum stratix10_svc_command_code`, `struct stratix10_svc_client_msg`, `struct stratix10_svc_command_config_type`, `struct stratix10_svc_cb_data`, `struct stratix10_svc_client`, opaque `struct stratix10_svc_chan`, channel request/free APIs, memory allocate/free APIs, `stratix10_svc_send`, `stratix10_svc_done`, `async_callback_t`, and async add/remove/send/poll/done APIs.

## Control Flow

Clients request a named channel, allocate service-layer memory if needed, fill `stratix10_svc_client_msg`, send commands, receive completion callbacks with status and completed buffer addresses, then call `stratix10_svc_done()` or async done to release transaction resources. Async clients can register a unique client ID, send messages with a handler, poll completion, and remove transactions.

## State and Persistence Behavior

Channel and async transaction state are owned by the service layer. Client messages carry payload pointers, output pointers, lengths, command codes, and register-style arguments. Hardware/firmware state changes persist according to FPGA/RSU/FCS/HWMON operation semantics.

## Dependencies and Integration Points

It integrates with Stratix10 secure monitor calls, FPGA manager, RSU, FCS, HWMON, device model, mailbox buffers, and service-layer worker/callback infrastructure.

## Risks and Edge Cases

Timeout constants differ by client class. Clients must free service memory and channels, call done after completion/error, and handle busy/no-support/invalid-param statuses. Async handler lifetime and callback arguments must be protected from use-after-free.

## Test Signals

Service-layer client mock tests, FPGA reconfiguration buffer flow tests, RSU/FCS/HWMON command tests, timeout tests, async send/poll/done lifecycle tests, and channel allocation failure tests.
