<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_ids_map_extended.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_ids_map_extended.h

## Purpose
Auto-generated Gaudi2 async event classification data. It maps firmware-controller event IDs to CPU event IDs and attaches driver policy metadata: whether an event is valid, whether it is a message event, what reset class it implies, and a stable printable event name.

## Important APIs, Types, And Functions
- `enum event_reset_type` defines `EVENT_RESET_TYPE_NONE`, `EVENT_RESET_TYPE_COMPUTE`, and `EVENT_RESET_TYPE_HARD`, which are consumed as driver reset policy.
- `struct gaudi2_async_events_ids_map` is the table row ABI: `fc_id`, `cpu_id`, `valid`, `msg`, `reset`, and `name[64]`.
- `gaudi2_irq_map_table[]` is a static table with entries for PCIe, TPC, MME, EDMA, KDMA, PDMA, CPU, PSOC, SRAM, HBM, HMMU, HIF, NIC, SM, XBAR, ARC, decoder, rotator, queue-manager, power, thermal, and heartbeat events.

## Control Flow
The header has no functions, but it drives Gaudi2 interrupt/event control flow. `gaudi2.c` iterates `gaudi2_irq_map_table` to collect valid non-message hardware events, maps CPU events when programming interrupt routing, prints event names in error paths, and decides whether async handling should trigger no reset, compute reset, or hard reset. Entries with `msg = 1` represent firmware or queue-manager messages that are handled differently from raw hardware events.

## State And Persistence Behavior
The table is compile-time static driver state and is not persisted. Runtime state lives in Gaudi2 device structures, event queues, and reset flows that reference this table. The table includes many intentionally invalid/reserved rows so `fc_id` can be used as a dense index without reshaping the firmware numbering.

## Dependencies And Integration Points
It is included by Gaudi2 driver code and depends on firmware event numbering staying aligned with generated IDs such as `GAUDI2_EVENT_CPU_PI_UPDATE`, `GAUDI2_EVENT_CPU_HALT_MACHINE`, and other async IDs. Integration points include MSI-X event queue programming, event logging, reset escalation, RAZWI/error reporting, queue-manager event handling, and health/error debug paths.

## Risks And Edge Cases
The main risk is firmware/driver drift: a wrong `cpu_id`, `valid`, `msg`, or `reset` value can route an interrupt to the wrong handler, suppress a real fault, or escalate a recoverable event into a hard reset. Reserved rows are valid index placeholders and must not be compacted. Multiple functional events share CPU IDs, so consumers must distinguish firmware-controller IDs from CPU IDs. The table is `static` in a header, so including it in more than one translation unit would duplicate storage.

## Test Signals
Useful signals are Gaudi2 boot with interrupts enabled, async event injection or firmware event simulation, recovery tests for ECC/AXI/page-fault/queue-manager events, and logs showing correct event names and reset levels. Build coverage should catch missing enum names; runtime validation should confirm valid event counts and event queue MSI-X routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_ids_map_extended.h -->
