# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.c

## Purpose

`nal-rbsp.c` provides the shared bit-level RBSP reader/writer used by both H.264 and HEVC NAL helpers. It manages bit positions, emulation-prevention byte insertion/removal, unsigned and signed Exp-Golomb coding, and RBSP trailing bits.

## Important APIs, Types, And Functions

- `rbsp_init()` initializes a cursor over a byte buffer with either `read` or `write` operations.
- Public wrappers `rbsp_bit()`, `rbsp_bits()`, `rbsp_uev()`, and `rbsp_sev()` dispatch to the current ops table and stop once `rbsp->error` is set.
- `rbsp_trailing_bits()` writes or reads the stop bit and alignment zero bits through the same wrapper API.
- Internal functions implement bit reads/writes, multi-bit reads/writes, unsigned Exp-Golomb, signed Exp-Golomb, and emulation-prevention handling.
- Global ops tables `write` and `read` provide the operation strategy used by syntax walkers.

## Control Flow

Writers call syntax walkers that repeatedly call the public wrappers. `rbsp_write_bit()` inserts an emulation-prevention pattern when the zero counter reaches the trigger threshold, writes one bit at the current byte/bit offset, advances `pos`, and updates the zero counter. Readers mirror this by discarding the emulation-prevention pattern when needed, reading a bit, advancing, and updating counters. Exp-Golomb helpers are built on top of those bit primitives. If any operation fails, `rbsp->error` is set and later wrapper calls become no-ops.

## State And Persistence

All active state is in `struct rbsp`: target data pointer, byte size, bit position, consecutive-zero count, ops pointer, and error code. There is no external persistence. The `read` and `write` ops tables are global shared constants in practice, though not declared `const`.

## Dependencies And Integration Points

The file depends on kernel math/log2 helpers and `nal-rbsp.h`. It is consumed by `nal-h264.c` and `nal-hevc.c`, which provide the actual codec syntax. Its behavior directly affects every generated SPS/PPS/VPS/filler NAL emitted by the Allegro driver.

## Risks

The emulation-prevention implementation is subtle: it tracks consecutive zero bits rather than simply scanning bytes, so off-by-one errors could corrupt generated streams. `rbsp_write_uev()` uses `ilog2(*value + 1)`, so callers must avoid overflow at `UINT_MAX`. Signed Exp-Golomb conversion must handle negative values safely. The global ops objects are writable, so accidental mutation would affect all users.

## Test Signals

Unit tests should cover bit-level reads/writes across byte boundaries, unsigned and signed Exp-Golomb round trips, buffer-too-small errors, trailing-bit alignment, and known byte sequences requiring emulation-prevention insertion/removal. Codec-level SPS/PPS/VPS round trips exercise this layer indirectly.
