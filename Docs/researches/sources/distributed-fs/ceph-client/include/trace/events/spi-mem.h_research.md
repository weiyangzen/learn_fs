
# sources/distributed-fs/ceph-client/include/trace/events/spi-mem.h

## Purpose
Defines tracepoints for SPI memory operations, showing operation start/stop, command/address/dummy/data phases, bus widths, DTR flags, data direction, and return status.

## Important APIs, Types, and Functions
Events are `spi_mem_start_op` and `spi_mem_stop_op`. `TRACE_SYSTEM` is `spi-mem` and `TRACE_SYSTEM_VAR` is `spi_mem` for C identifier compatibility. `decode_dtr()` prints DTR phase markers. Fields are extracted from `struct spi_mem_op`, including opcode, address bytes/value, dummy bytes, bus widths, data bytes, direction, and data buffer pointer, plus return code on stop.

## Control Flow
SPI memory core code emits start before executing a memory operation and stop after completion. The tracepoint snapshots the operation descriptor rather than copying the payload buffer.

## State and Persistence
The header owns no SPI memory state. Trace records persist operation descriptors and buffer pointers. Payload contents are not copied, so the buffer pointer is only useful as a correlation hint while the operation is live.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and SPI memory operation types. Integrates with SPI NOR/NAND, controller drivers implementing `spi_mem_ops`, and flash transaction debugging.

## Risks
Pointer-only data buffer recording avoids payload overhead but limits postmortem value. DTR, bus-width, and phase semantics must track `struct spi_mem_op` evolution. Trace format uses `spi-mem` naming, so include/trace generation depends on the `TRACE_SYSTEM_VAR` override.

## Test Signals
Signals include SPI NOR reads/writes/erase op traces, DTR-capable flash operations, dummy/address phase validation, controller error injection, and tracefs event format checks for the hyphenated system name.
