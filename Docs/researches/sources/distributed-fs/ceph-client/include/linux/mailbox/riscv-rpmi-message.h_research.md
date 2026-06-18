<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/riscv-rpmi-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/riscv-rpmi-message.h

## Purpose
This header defines the Linux mailbox message ABI for RISC-V RPMI service groups. It includes wire headers, service/message identifiers, error translation, helper initializers, and a send helper that bridges RPMI messages to the generic mailbox framework.

## Important APIs, types, and functions
Wire-level structures are `struct rpmi_message_header`, `struct rpmi_message`, and `struct rpmi_notification_event`. `enum rpmi_error_codes` maps RPMI negative status values, while `rpmi_to_linux_error()` converts them to Linux errno values. Service identifiers cover system MSI and clock service groups. The Linux mailbox wrapper is `struct rpmi_mbox_message`, whose union represents attribute operations, request/response service data, or notification events. Initializers include `rpmi_mbox_init_get_attribute`, `rpmi_mbox_init_set_attribute`, `rpmi_mbox_init_send_with_response`, and `rpmi_mbox_init_send_without_response`; `rpmi_mbox_send_message()` sends through `mbox_send_message()` and reports completion with `mbox_client_txdone()`.

## Control flow
Callers initialize a `rpmi_mbox_message` for one of the supported message types, pass it to `rpmi_mbox_send_message()`, and then inspect `msg->error` plus response fields. The send helper treats a negative mailbox submission as transport failure; otherwise it uses the controller/client-populated `msg->error` as the transaction result and explicitly completes the mailbox TX state machine.

## State and persistence
State is transient and message-local. Request and response pointers remain caller-owned; `out_response_len` and `error` are expected to be filled during mailbox handling. No persistent state is stored in this header.

## Dependencies and integration points
The header depends on errno constants, mailbox client APIs, endian-sized Linux types, and `upper_16_bits`/`lower_16_bits`. It integrates RPMI clock and system-MSI service clients with generic mailbox channels.

## Risks and test signals
Risks include endian mistakes in wire headers, stale request/response buffers, service IDs exceeding firmware support, response truncation when `max_response_len` is too small, and callers forgetting that completion is signaled explicitly. Test attribute get/set, no-response sends, response-length reporting, notification decoding, all RPMI-to-Linux errno mappings, and transport failures from `mbox_send_message()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/riscv-rpmi-message.h -->
