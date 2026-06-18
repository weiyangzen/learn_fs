<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole.h

Purpose: defines the UML management-console wire protocol and shared request/reply structures used by kernel and host-side mconsole code.

Important APIs/types/functions: protocol constants are `MCONSOLE_MAGIC`, `MCONSOLE_MAX_DATA`, and `MCONSOLE_VERSION`. Wire structs are `mconsole_request`, `mconsole_reply`, and `mconsole_notify`. Internal structs are `mconsole_command` and `mc_request`; `enum mc_context` distinguishes interrupt-context and process-context handlers. It declares command handlers and request/reply/notify functions.

Control flow: `mconsole_user.c` parses datagrams into `mc_request` and dispatch metadata; `mconsole_kern.c` executes handlers and uses reply helpers.

State and persistence: no state is defined here except the external `mconsole_socket_name`. The protocol is runtime IPC over Unix datagram sockets.

Dependencies and integration points: includes host `stdint.h` when building user-side code and UML ptrace register definitions for captured IRQ register state.

Risks: this header defines a compatibility protocol. Changing sizes, magic, version, or enum values can break `uml_mconsole` clients and boot notifications.

Test signals: send valid/invalid versioned datagrams, oversized requests, notifications, and command replies split across multiple packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole.h -->
