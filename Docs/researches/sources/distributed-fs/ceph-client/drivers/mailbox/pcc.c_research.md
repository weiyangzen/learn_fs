# sources/distributed-fs/ceph-client/drivers/mailbox/pcc.c

Purpose: implements ACPI Platform Communication Channel as a mailbox controller, allowing clients such as CPPC/RAS/MPST to coordinate with firmware/platform controllers through ACPI-described shared memory and doorbell registers.

Important APIs/types/functions: `struct pcc_chan_info` wraps `struct pcc_mbox_chan`, doorbell/ACK/complete/error registers, IRQ metadata, subspace type, and in-use state. Exported APIs `pcc_mbox_request_channel` and `pcc_mbox_free_channel` map shared memory and bind/free mailbox clients. Internal helpers parse PCCT subspaces, initialize GAS registers, ring doorbells, poll completion, handle IRQs, and acknowledge slave subspace notifications.

Control flow: `pcc_init` checks ACPI PCCT and creates a platform bundle early. Probe walks PCCT entries, allocates channels, configures txdone by global doorbell flag, parses optional platform IRQs, doorbell/complete/update/error registers, and shared-memory metadata, then registers the controller. A client requests a subspace by id, the driver maps the shared memory region, and binds the channel. Send updates command-complete state then rings the doorbell; IRQ acknowledges platform IRQ, validates complete/error state, clears `chan_in_use`, reports RX and txdone, and performs slave-subspace acknowledgement.

State and persistence: global `chan_info` and `pcc_chan_count` describe ACPI subspaces. Shared memory is mapped per requested channel and unmapped on free. Register virtual addresses are cached for performance.

Dependencies and integration: depends on ACPI PCCT, ACPI GAS read/write, GSI mapping, mailbox framework, and `include/acpi/pcc.h` client contracts.

Risks: malformed PCCT register widths, missing ACK registers on level IRQs, or wrong subspace type handling can cause stuck firmware communication. Polling completion without IRQ depends entirely on command-complete semantics.

Test signals: ACPI table parsing for every PCCT type, request/free shared-memory mapping, IRQ and polling completion paths, error-status clear handling, and CPPC/RAS client boot coverage.
