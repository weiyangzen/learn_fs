# sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.h

## Purpose
`qlogicpti.h` defines the hardware register map, firmware mailbox protocol, queue entry formats, SCSI status constants, and software state for the QLogic/PTI SBUS ISP driver. It is the ABI-like contract between `qlogicpti.c`, the ISP firmware, and the SBUS register layout.

## Important APIs, Types, And Functions
Important structures include `Entry_header`, `dataseg`, `Command_Entry`, `Ext_Command_Entry`, `Continuation_Entry`, `Marker_Entry`, `Status_Entry`, `host_param`, `dev_param`, `pti_queue_entry`, and `struct qlogicpti`. Constants cover SBUS, DMA, mailbox, CPU/RISC, and host-control register offsets and bit definitions; request/response ring lengths; entry types; control flags; completion statuses; state/status flags; async events; and mailbox commands. Ring helpers `NEXT_REQ_PTR()`, `NEXT_RES_PTR()`, `PREV_REQ_PTR()`, and `PREV_RES_PTR()` implement wrapping over power-of-two-minus-one masks.

## Control Flow
The header has no direct execution, but its data formats drive all command flow. `Command_Entry` and `Continuation_Entry` describe outbound requests, `Status_Entry` describes inbound completions, and `Marker_Entry` synchronizes firmware after reset. Endianness-specific field ordering is encoded in several structures, allowing the same C field names to represent firmware byte layout on big- and little-endian builds.

## State And Persistence
`struct qlogicpti` defines all live adapter state: MMIO register pointers, coherent request/response queues, queue indices, marker flag, platform device, per-target command/tag state, command pointer slots, firmware revision, SCSI host, adapter identity, IRQ, device-tree settings, host and target parameters, PTI status register mapping/shadow, and bitflags. This state is allocated per SCSI host and is not persistent across driver unload or hardware reset.

## Dependencies And Integration Points
The header depends on Linux integer types, SCSI command declarations, platform-device concepts, DMA address types, and architecture endianness macros. It integrates tightly with ISP firmware expectations: queue entry size is fixed at 64 bytes, request and response queue lengths are 255 plus one actual slot, and mailbox status/event constants must match firmware.

## Risks And Edge Cases
Because this file encodes hardware and firmware layout, field-size or endian mistakes can corrupt DMA rings. `QLOGICPTI_MAX_SG(ql)` ties SG capacity to free request slots; callers must recompute queue capacity carefully. Several comments document hardware quirks, such as 64-byte burst unreliability and 32-bit firmware handles requiring an in-driver command-slot table. The header also redefines `MAX_TARGETS`/`MAX_LUNS` values also present in the C file, creating drift risk.

## Test Signals
Build tests should cover endian-sensitive structure layouts and all users of mailbox/entry constants. Runtime signals include correct firmware command parsing, request and response ring wraparound at slot 255, SG capacity calculation as free slots change, command handle lookup through `cmd_slots`, differential/terminator status interpretation, and register bit programming for SBUS burst, reset, interrupt, and RISC control paths.
