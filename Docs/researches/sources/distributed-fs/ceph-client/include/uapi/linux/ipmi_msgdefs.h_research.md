# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_msgdefs.h

## Purpose
`ipmi_msgdefs.h` provides common IPMI net function, command, completion-code, protocol, and channel-medium constants shared by IPMI UAPI users.

## Important APIs, Types, and Functions
Constants cover sensor/event, application, storage, and firmware netfns; common commands such as get device ID, reset, get/clear message flags, send/get/read event messages, channel info, SEL insertion, and BMC global enables; BMC enable bits; default slave address; maximum message length; standard and bus-level completion/error codes; channel protocol identifiers; and channel medium identifiers.

## Control Flow
No executable flow exists here. IPMI userspace and kernel drivers use these constants to construct raw `ipmi_msg` packets, decode completion codes, and interpret channel metadata.

## State and Persistence
The header has no state. It names values that appear in BMC messages, completion responses, and channel capability reports.

## Dependencies and Integration Points
It is included by `ipmi.h` and consumed by IPMI tools, BMC drivers, and management agents that need symbolic values for the IPMI specification.

## Risks and Test Signals
Tests should validate command encodings against IPMI specifications, max message length handling, and consistency between kernel responses and userspace decoders. Risk is low in code volume but high for interoperability if constants drift.
