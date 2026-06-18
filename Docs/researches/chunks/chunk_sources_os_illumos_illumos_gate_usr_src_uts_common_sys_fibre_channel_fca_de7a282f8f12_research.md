# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 3336-6653

This chunk is a contiguous slice of the Emulex LP11000 firmware byte array `emlxs_lp11000_image[]`. It covers image offsets `0x06770` through `0x0CF1F` inclusive: 3,318 initializer rows and 26,544 bytes. The chunk is not ordinary illumos C logic; it is adapter-resident firmware encoded as bytes, with ARM-style instruction words, literal pools, jump/data tables, and embedded diagnostic strings.

## APIs And Host Surface

No C functions, structs, typedefs, enums, driver callbacks, or callable kernel APIs are declared in this line range. The host-visible contract is inherited from the file wrapper:

- `emlxs_lp11000_image[]` is emitted only under `EMLXS_FW_IMAGE_DEF`.
- File-level metadata outside this chunk identifies the image as `LP11000-S: v2.82a4 (bd282a4.all)` and provides kernel/stub/SLI address macros.
- When the image definition is not requested, the surrounding header later substitutes `emlxs_lp11000_image` and `emlxs_lp11000_size` with `0`; that logic is outside this chunk.

## Encoded Control Flow

The first line starts in the middle of firmware execution at `0x06770`, immediately after code from the previous chunk. The early region contains branch-heavy formatting/runtime-like code. Visible literal text includes uppercase and lowercase hexadecimal digit tables near `0x06790` and `0x067E8`, plus `0X`/`0x`, sign, space, and padding literals, suggesting number-formatting helper code embedded in the firmware runtime.

Around `0x07067`-`0x07107`, the byte stream contains standard runtime error strings: `No error (errno = 0)`, `EDOM - function argument out of range`, `ERANGE - function result not representable`, and `ESIGNUM - illegal signal number to signal() or raise()`. Nearby code branches to and from helper routines, so this appears to be part of an embedded C library/runtime support area rather than host-driver error handling.

The middle of the chunk mixes dense instruction sequences with diagnostic/self-test text. Readable strings include:

- `Error bits in ERRCLR cannot be cleared`
- `Address`, `Expected`, `Actual`, `Error bits`
- `Required Test`
- `Expected:`, `Read:`, `Bits in error:`
- `Unknown ALU code`
- `Invalid table code`
- `Unknown pattern generation code`
- `Error for`, `Expected reset value:`, `Wrote:`, `Read:`, `Error bits:`

These strings point to firmware-side memory/register/ALU/pattern-generation self-test or debug-monitor routines. They do not create host-side APIs, but they reveal that this slice participates in low-level adapter diagnostics.

The final region, roughly `0x0C000` through the boundary at `0x0CF1F`, contains routines with repeated loads, stores, comparisons, and branches over fixed structure offsets such as `+0x08`, `+0x0C`, `+0x10`, `+0x14`, `+0x18`, `+0x1C`, `+0x20`, `+0x24`, and larger descriptor-like offsets. The exact data structures are proprietary firmware internals, but the pattern is consistent with queue/list accounting, descriptor allocation or recycling, status polling, and hardware-control bookkeeping.

Static branch decoding from the emitted ARM-style words shows many intra-image references: most branch/call targets land inside this chunk, but many target helper code before `0x06770`, and a smaller number target code after `0x0CF1F`. Therefore this range is not independently executable or analyzable as a closed module.

## State And Data

At C level, the only state contributed by this chunk is immutable byte data inside the firmware image initializer. At adapter runtime, the bytes encode executable state machines and their constants.

Visible firmware state patterns include:

- Position-sensitive literal pools and string tables interleaved with code.
- PC-relative references to nearby digit tables, prefixes, diagnostic strings, and branch targets.
- Fixed-offset record manipulation that likely acts on firmware descriptors, queues, control blocks, or hardware status records.
- Poll/test/update loops around status words and bitfields, especially in the diagnostic sections.

Because code and data are interleaved, the row comments are only a partial aid. Printable text can sit adjacent to executable words, and not every printable-looking byte sequence is necessarily a standalone string.

## Dependencies

Compile-time dependencies are the enclosing header guard, `EMLXS_FW_IMAGE_DEF`, `uint8_t`, and the compiler/linker handling of `#pragma align 8(emlxs_lp11000_image)`, all declared outside this line range.

Runtime dependencies are firmware-loader and adapter invariants:

- The driver must deliver this byte range to the LP11000 adapter exactly as emitted.
- Byte order, 8-byte row ordering, offsets, and total image size must stay aligned with the file-level metadata.
- Branch offsets and literal references depend on the exact placement of this chunk relative to earlier and later firmware chunks.
- The encoded routines depend on the LP11000/Thor adapter execution environment, register map, on-card memory layout, and Fibre Channel/SLI firmware conventions.

## Risks

Any edit in this chunk is high risk. A single-byte change can corrupt an instruction, branch displacement, literal pool entry, diagnostic string, packed constant, self-test table, or firmware-internal structure layout. Normal C compilation can check only the syntax of the initializer, not the semantic validity of the firmware.

The diagnostic strings indicate self-test and debug paths. Corruption here could mask adapter hardware failures, misreport register-test results, or break firmware recovery/debug output. The dense polling and fixed-offset update loops also imply potential initialization hangs or command-processing failures if altered.

Version coupling is strict: this byte range must remain consistent with the LP11000 label/version macros, the firmware entry/stub/SLI address constants, and the final image size reported later in the header.

## Cross-Chunk References

- Chunk 1 supplies the start of the routine whose execution reaches `0x06770`; this chunk begins mid-control-flow.
- Calls and branches in this chunk target helpers before `0x06770`, including common runtime/debug routines from earlier chunks.
- Several branches and calls target code after `0x0CF1F`, so subsequent chunks continue routines referenced here.
- This chunk ends mid-routine at `0x0CF18`/`0x0CF1F`; the next chunk must describe the continuation.
- Header-level declarations, size macros, include guards, and final fallback macros are outside this line range and belong in other chunk reports or the merged per-file report.