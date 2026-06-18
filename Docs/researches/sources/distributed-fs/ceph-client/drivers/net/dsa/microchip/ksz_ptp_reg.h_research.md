# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp_reg.h

## Purpose
`ksz_ptp_reg.h` defines PTP, trigger output, timestamp, interrupt, and LAN937x GPIO/LED register offsets and bit fields used by `ksz_ptp.c`.

## Important APIs, Types, and Functions
The file is macro-only. It defines global LED override/source registers, PTP clock control bits (`PTP_READ_TIME`, `PTP_LOAD_TIME`, `PTP_CLK_ADJ_ENABLE`, `PTP_CLK_ENABLE`, and related fields), subnanosecond rate masks, PTP message configuration bits, unit index fields, trigger status/interrupt/control fields, trigger timing registers, and per-port timestamp/interrupt registers. Message index constants map PDelay_Resp, PDelay_Req, and Sync to the three timestamp IRQ slots.

## Control Flow
There is no executable control flow. `ksz_ptp.c` composes these masks with common regmap helpers to select GPIOs, reset trigger units, configure periodic outputs, read/write PHC time, enable PTP packet parsing, and decode/clear timestamp interrupts.

## State and Persistence
These macros name volatile hardware state. Persistence and caching are handled by the PTP implementation and the switch hardware, not by this header.

## Dependencies and Integration Points
The header assumes Linux bit macros such as `BIT()` and `GENMASK()` are already available through including translation units. It is tightly coupled to `ksz_ptp.c` and the abstract PTP register slots in `ksz_common.h`/chip data.

## Risks and Edge Cases
Incorrect bit definitions can misroute LAN937x LED pins, enable the wrong trigger unit, clear the wrong W1C interrupt bit, or break timestamp message selection. Some field names represent bit masks while message constants represent logical array indexes, so mixing them would be hazardous.

## Test Signals
PTP clock control, periodic output, GPIO routing, and TX timestamp IRQ tests provide the runtime validation for these definitions. Register traces should show writes to the documented offsets and W1C clearing of `REG_PTP_PORT_TX_INT_STATUS__2`.
