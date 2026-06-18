# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 63059-66376

## Scope And Shape

This chunk is a contiguous 3,318-line slice of `emlxs_lpe11000_image[]`, covering firmware byte offsets `0x7B1C8` through `0x81977` inclusive. Every line in the range is an initializer row with eight bytes and a byte-offset comment; the chunk contributes 26,544 bytes of the full `0x8A5CC`-byte LPe11000 firmware image. It is not C source logic in the normal sense: the bytes encode ARM-style firmware code and embedded literal/data tables loaded by the Emulex `emlxs` Fibre Channel adapter driver.

Host-side integration is through `emlxs_fw.h`, where `LPe11000_FW` table entries reference `emlxs_lpe11000_size`, `emlxs_lpe11000_image`, label, and component version fields. This chunk has no callable illumos APIs of its own, but it is part of the binary payload consumed by firmware download/update paths.

## Visible Firmware Control Flow

The chunk is dense executable firmware. Common ARM instruction prefixes are visible throughout: branch-with-link (`0xEB...`), unconditional branches (`0xEA...`), conditional branches, load/store operations (`0xE5...`), and function prologue/epilogue patterns (`0xE9 0x2D...` / `0xE8 0xBD...`).

Major visible regions:

- `0x7B1C8` starts mid-routine, repeatedly calling helpers, checking return values, and returning status-like values.
- `0x7B2F0`-`0x7B4B8` writes byte constants such as `0xA0`-`0xA3` and command/status values `0x7B`-`0x7F`, with repeated helper calls.
- `0x7B718`-`0x7B790` initializes global state through literal-pool addresses including `0x00096980`, `0x00096990`, `0x000969A0`, and `0x000969A4`.
- `0x7E178` embeds ASCII `bp init\n`, followed by initialization code that manipulates low-level control registers and state bytes.
- `0x7E1E0`-`0x7E318` appears to run a boot/bring-up state machine keyed by state byte `0x39`, hardware mode bits near `0x30`, and status bytes near `0x80`-`0x84` and `0xA8`.
- `0x7FC90`-`0x7FE68` walks descriptor-like structures, copies word pairs, updates pointer/counter fields, and returns boolean-style success/failure.
- `0x81218`-`0x816F0` contains a large dispatcher classifying operation/status fields such as `0x0101`, `0x0202`, `0x0501`, and several `0x04xx` cases.
- `0x81970` ends inside active dispatch/control flow, continuing into the next chunk.

## State And Dependencies

Visible structure-relative state includes byte offsets `0x06`, `0x07`, `0x0D`, `0x0E`, `0x10`, `0x11`, `0x24`, `0x30`, `0x39`, `0x4E`, `0x4F`, `0x52`, `0x53`, `0x68`, `0x69`, `0x80`-`0x86`, `0x98`, and `0xA8`.

Visible word/pointer/counter offsets include `0x20`, `0x24`, `0x28`, `0x2C`, `0x30`, `0x34`, `0x38`, `0x50`, `0x58`, `0x5C`, `0x60`, `0x64`, `0x80`, `0x90`-`0xA0`, `0x1B0`-`0x1BC`, `0x220`-`0x230`, `0x260`-`0x264`, and `0x2C0`-`0x2DC`.

This chunk depends on earlier and later firmware bytes for complete meaning. It starts mid-routine, many branches target code outside the range, and the final visible dispatch sequence continues after line 66376.

## Risks

The main risk is opacity: this is binary firmware encoded as a C initializer, so normal source review and compiler analysis cannot validate behavior. Any byte-level edit can corrupt executable instructions, branch targets, literal addresses, or image integrity. Alignment, byte order, and version coupling with the exported label/version macros are critical.

## Cross-Chunk References

- Previous chunk: required for the routine already in progress at `0x7B1C8`.
- Next chunk: required for dispatch/control flow continuing after `0x81970`.
- Whole file: required for firmware metadata, array declaration, array size, and `EMLXS_FW_IMAGE_DEF` fallback behavior.