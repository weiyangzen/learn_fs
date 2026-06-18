# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_ssif_bmc.h

## Purpose
`ipmi_ssif_bmc.h` defines the message payload structure for SSIF BMC IPMI communication.

## Important APIs, Types, and Functions
`IPMI_SSIF_PAYLOAD_MAX` is 254 bytes. `struct ipmi_ssif_msg` contains `len`, `netfn_lun`, `cmd`, and a payload array sized to the maximum SSIF payload.

## Control Flow
Userspace or kernel-side BMC emulation passes a bounded SSIF message containing netfn/LUN, command, and payload. The receiving side validates `len` and interprets the payload according to IPMI command semantics.

## State and Persistence
The structure is transient message state only. Persistent behavior is in the SSIF/BMC backend and SMBus/I2C transport.

## Dependencies and Integration Points
It includes `<linux/types.h>` and integrates with IPMI SSIF BMC drivers and host-to-BMC management transports.

## Risks and Test Signals
Tests should cover payload length limits, zero-length payloads, command/netfn decoding, and rejection of overlong `len` values. ABI risk is straightforward fixed-size message layout.
