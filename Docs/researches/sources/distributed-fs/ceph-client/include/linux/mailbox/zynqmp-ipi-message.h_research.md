<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/zynqmp-ipi-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/zynqmp-ipi-message.h

## Purpose
This header defines the variable-length message container used by Xilinx ZynqMP IPI mailbox clients.

## Important APIs, types, and functions
`struct zynqmp_ipi_message` contains a payload `len` and flexible `data[]`. The comment documents a fixed maximum payload size of 32 bytes, but the limit is enforced by callers or the controller rather than by the type itself.

## Control flow
Clients allocate or embed a buffer large enough for the header plus payload, fill `len` and `data`, and submit it with `mbox_send_message()`. The mailbox controller interprets the byte payload according to ZynqMP IPI protocol rules.

## State and persistence
The message is transient. No global state or persistence is defined.

## Dependencies and integration points
It relies on `size_t` and `u8` from common Linux headers already included by users. It integrates ZynqMP firmware/IPI clients with the generic mailbox framework.

## Risks and test signals
Main risks are payloads longer than the 32-byte hardware contract, allocation sizes that do not match `len`, and protocol consumers assuming NUL-terminated data. Test zero-length, exact 32-byte, and over-limit messages and verify the controller rejects or truncates safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/zynqmp-ipi-message.h -->
