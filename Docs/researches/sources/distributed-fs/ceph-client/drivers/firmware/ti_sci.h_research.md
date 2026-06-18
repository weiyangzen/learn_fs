# sources/distributed-fs/ceph-client/drivers/firmware/ti_sci.h

## Purpose
`ti_sci.h` is the private TI SCI wire-protocol schema used by `ti_sci.c`. It defines message IDs, generic header flags, request/response layouts, state constants, resource masks, and packed firmware ABI structures for generic, device, clock, low-power, resource-management, IRQ, NAVSS, UDMAP, and processor-control operations.

## Important APIs, types, and constants
The core type is `struct ti_sci_msg_hdr`, a packed header with message type, host id, sequence id, and request/response flags. All other protocol structures embed it first. Generic messages include firmware version, system reset, and capability query. Device messages model state transitions, reset bits, context-loss counts, programmed state, and current hardware state. Clock messages cover state, parent selection, parent count, frequency query, set, and get; they include the 8-bit `clk_id` plus `clk_id_32` escape path for IDs >= 255.

Low-power structs define prepare-sleep modes for Partial-IO and DM-managed suspend, IO isolation enable/disable, wake reason reporting, device constraints, and latency constraints. Resource-management structs define resource ranges, IRQ route management with validity bitmasks, ring configuration, PSI-L pair/unpair, UDMAP TX channel, RX channel, and RX flow configuration. Processor-control structs define request/release/handover, boot vector config, control flags, and status response.

## Control flow and integration
The header has no executable control flow, but its layout directly controls `ti_sci.c` message construction and response parsing. The driver allocates a transfer buffer, casts it to one of these request structs, fills fields, sends it through the mailbox, then casts the same buffer to a matching response struct. The common ACK/NACK semantics come from `TI_SCI_FLAG_RESP_GENERIC_ACK` in `struct ti_sci_msg_hdr`.

## State and persistence behavior
The file defines state values but stores none itself. Firmware-visible state represented here includes device software/hardware state, clock software/hardware state, firmware capability bits, resource ranges, low-power constraints, and processor boot/control/status flags. The `__packed` annotations are part of the persistence and compatibility contract because they keep C layout aligned with the firmware wire format.

## Dependencies and integration points
The header assumes kernel bit helpers such as `GENMASK()`/`GENMASK_ULL()` are available through including contexts. It is included by the TI SCI driver and complements public client-facing definitions in `linux/soc/ti/ti_sci_protocol.h`. Integration is ABI-sensitive: clients do not normally include this private header, but their public operation calls depend on these internal structs matching the firmware specification.

## Risks and test signals
The main risk is ABI drift: any field ordering, size, packing, message ID, flag, or mask error can silently break firmware communication. The 255 escape convention for clock parent/clock IDs is especially easy to mishandle. Test signals are build coverage for all structs referenced by `ti_sci.c`, successful firmware version/capability queries, ACK/NACK handling across message families, and hardware/firmware integration tests that exercise clock IDs and resource ranges near boundary values.
