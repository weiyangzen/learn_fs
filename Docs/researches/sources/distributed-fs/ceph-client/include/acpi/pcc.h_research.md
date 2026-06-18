# sources/distributed-fs/ceph-client/include/acpi/pcc.h

Purpose: Defines the Linux Platform Communications Channel mailbox abstraction and shared-memory command/status bits used by ACPI PCC consumers.

Important APIs, types, and functions: Exports `struct pcc_mbox_chan`, `PCC_SIGNATURE`, command/status flag macros, `MAX_PCC_SUBSPACES`, and `pcc_mbox_request_channel()`/`pcc_mbox_free_channel()` with `-ENODEV` stubs when `CONFIG_PCC` is disabled.

Control flow: Clients request a PCC subspace by id through the mailbox framework, then use shared-memory base/size and timing metadata to issue commands and wait for completion or platform notification.

State and persistence: Runtime state is a mailbox channel, mapped shared memory, platform timing limits, and firmware-owned status/command words. ACPI PCCT table data describes the persistent channel layout.

Dependencies and integration points: Depends on mailbox controller/client APIs and ACPI PCCT definitions. Integrates with CPPC, RAS, platform firmware channels, and drivers using PCC doorbells.

Risks and test signals: Risks include subspace id overflow, missing PCC support, shared-memory mapping lifetime, status-bit races, and consumers ignoring latency/turnaround limits. Test request/free paths, disabled builds, concurrent PCC clients, command-complete/error handling, and PCCT malformed subspaces.
