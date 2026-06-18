# Chunk Research: `fw_lp11002.h` Lines 3336-6653

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h`

Scope: learn_fs subset A (`Docs/research_subset_a.md`), illumos `emlxs` Fibre Channel adapter firmware image.

## Chunk Identity

This report covers only chunk 2, lines `3336-6653`, and the requested line range was read completely. The range is wholly inside the generated `static uint8_t emlxs_lp11002_image[]` initializer for the Emulex LP11002 / LP11002-S adapter firmware. It is not ordinary illumos driver source.

The chunk spans firmware image offsets `0x06770` through `0x0CF1F`. It begins immediately after chunk 1's mid-routine formatting logic and ends mid-routine at the boundary with chunk 3.

## APIs And Host-Visible Surface

No C functions, structs, typedefs, macros, locks, syscalls, or callable kernel APIs are declared in this chunk. The host-visible surface affected by these lines is only the byte content of `emlxs_lp11002_image[]`.

The surrounding file-level interface, defined outside this range, provides the LP11002 firmware label/version constants, kernel/stub/SLI address macros, the optional image definition under `EMLXS_FW_IMAGE_DEF`, and the final `emlxs_lp11002_size`. `emlxs_fw.h` consumes those symbols as an opaque firmware descriptor for `LP11002_FW`.

## Firmware Control Flow

At the C layer, this chunk has no runtime control flow. At the firmware layer, the bytes are ARM-style executable code interleaved with literal pools and diagnostic data. Routine names and symbols are not present, so behavior is inferred from instruction patterns and embedded text.

The first region, around `0x06770-0x06A98`, continues a formatting/parser routine from chunk 1. It contains branches over uppercase/lowercase hexadecimal digit tables (`0123456789ABCDEF`, `0123456789abcdef`) and prefixes (`0X`, `0x`), plus repeated stores through a pointer advanced to word alignment.

Later regions include runtime helper loops, errno strings, self-test diagnostics, ERRCLR/reset-value checks, and dense fixed-offset control-block manipulation. The final bytes are not a complete routine; chunk 3 continues at `0x0CF20`.

## State, Dependencies, Risks

Host-visible state is immutable byte-array data only. Firmware-private state is opaque but visibly includes stack scratch buffers, formatted-output state, runtime error tables, diagnostic/self-test tables, and fixed-offset hardware/control records.

Build dependencies come from the enclosing header: `uint8_t`, `_FW_LP11002_H`, `EMLXS_FW_IMAGE_DEF`, and `#pragma align 8(emlxs_lp11002_image)`. Runtime dependencies are the LP11002 adapter processor, on-card memory map, Fibre Channel/SLI firmware ABI, descriptor layout, and the illumos `emlxs` firmware download path.

The main risk is binary integrity: any byte edit, comma loss, row reordering, endian conversion, or string change can alter executable firmware while leaving valid C. Source-level review cannot prove firmware memory safety or protocol correctness because this is vendor firmware without symbolic source.

## Cross-Chunk References

Chunk 1 defines the header prologue, firmware metadata, image declaration, initial vector/header data, and the first part of the formatter routine. This chunk starts at `0x06770`, immediately after chunk 1's active instruction stream at `0x06768`.

Chunk 3 starts at source line `6654`, firmware offset `0x0CF20`, and continues the active queue/control-block routine that begins before the end of this chunk.