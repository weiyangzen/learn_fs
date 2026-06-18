# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.h

## Purpose
`iris_hfi_common.h` defines the generation-neutral HFI command/response operation tables, packet payload/port/host-flag enums, color metadata enums, subscription data, and common HFI lifecycle APIs.

## Important APIs, Types, And Functions
Important types include `enum hfi_packet_port_type`, `enum hfi_packet_payload_info`, `enum hfi_packet_host_flags`, HFI color enums, `struct iris_hfi_prop_type_handle`, `struct iris_hfi_command_ops`, `struct iris_hfi_response_ops`, and `struct hfi_subscription_params`. Public functions cover HFI color conversion, core init, PM suspend/resume, and IRQ handlers.

## Control Flow
Each platform generation installs an `iris_hfi_command_ops` implementation. Generic core, common streaming, controls, and buffer code call these function pointers without knowing the wire format. The response op is called from the threaded IRQ handler.

## State And Persistence Behavior
The header describes state carried elsewhere: command op pointers in `struct iris_core`, response op pointers, and Gen2 subscription params used for source-change processing. No state is stored in the header itself.

## Dependencies And Integration Points
It includes V4L2 device types and `iris_buffer.h`. It is included by core, controls, HFI queue/command/response, and PM code. The command ops are the main abstraction separating Gen1 packet structs from Gen2 packet headers/sub-packets.

## Risks And Test Signals
Adding a command op requires both generations to implement or callers to handle NULL. Tests should verify that platform-selected HFI generation fills all ops used by common code, especially optional `session_pause` and `session_resume_drain`.
