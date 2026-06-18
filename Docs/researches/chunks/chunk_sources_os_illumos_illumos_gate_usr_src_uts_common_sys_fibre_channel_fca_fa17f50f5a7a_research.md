# Chunk Research: fw_lpe11000.h Chunk 6 Lines 16607-19924

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h`

Scope: lines 16607-19924 of the `emlxs_lpe11000_image[]` firmware byte array. This chunk starts at embedded image offset `0x20628` and ends at `0x26DD7`, covering about 26,544 bytes.

## Chunk Role

This range is not normal C logic. It contributes bytes to the `static uint8_t emlxs_lpe11000_image[]` firmware payload consumed by the illumos `emlxs` Fibre Channel driver. Control flow is embedded ARM-like firmware logic inferred from opcodes and literal pools, not host-side C execution.

## APIs And Exports

- No new C functions, structs, macros, or host-callable APIs are introduced.
- The chunk contributes a contiguous segment to `emlxs_lpe11000_image[]`.
- Host-side users depend on the whole byte array and metadata from other chunks.
- Embedded interfaces appear as routines, dispatch tables, literal pools, and diagnostic strings, but are not symbolized.

## Control Flow

- The chunk begins mid-routine, continuing state checks and updates over offsets such as `0x1f`, `0x20`, `0x28`, `0x158`, `0x15c`, and `0x160`.
- Multiple packed firmware routines use standard prologue/epilogue patterns and repeated helper calls.
- Offsets around `0x20FE0-0x21538` include literal data and visible strings: `Z1D2.82A3`, `TIME: %08x  %s`, `%08x:`, `%08x %08x`, and `Rcverr Frm %x. Idx %x.`.
- Dense pointer/descriptor tables appear around `0x212B8-0x214E8` and `0x23C40-0x23D20`, referencing embedded addresses in `0x0007xxxx`, `0x0008xxxx`, and `0x0009xxxx` regions.
- A visible command dispatcher around `0x23B70-0x23C38` compares command bytes including `0x40-0x48`, `0xc0-0xc4`, then branches to far handlers.
- Later handlers classify command/status values in ranges including `0x80-0x8b`, `0xb4`, `0xd0`, `0xe0`, and `0xf0`.
- The chunk ends mid-handler while updating descriptor/status fields; the next chunk must continue the routine.

## State And Dependencies

The firmware manipulates opaque adapter structures with frequent fields at offsets `0x04`, `0x07`, `0x08`, `0x0a`, `0x0b`, `0x0c`, `0x10`, `0x14`, `0x18`, `0x1c`, `0x20`, `0x24`, `0x26`, `0x27`, `0x28`, `0x2c`, `0x30`, `0x3c`, `0x40`, `0x44`, `0x50`, `0x54`, `0x58`, `0x60`, `0x64`, `0x6a`, `0x6c`, and `0x70`.

Dependencies are byte-level: branch targets, helper routines, and literal addresses span prior and later chunks. The host driver must preserve byte order, alignment, and array continuity.

## Risks

- Any byte change can alter firmware behavior while still compiling.
- The source lacks symbolic names for embedded routines and states.
- The range begins and ends inside embedded routines, so complete correctness depends on adjacent chunks.
- Command dispatch and adapter state handling are hardware-facing and high risk.

## Cross-Chunk References

- Prior chunk: required for the routine entry and initial state before `0x20628`.
- Next chunk: required because this chunk ends mid-routine after offset `0x26DD0`.
- Whole file: top-level firmware metadata and final array size/terminator are outside this chunk.
- Many branch/literal references target firmware regions outside this line range.

## Research Notes

- Complete line range read: 16607-19924.
- Adjacent context checked only to confirm the enclosing byte array and continuity.
- No final per-file report was created.