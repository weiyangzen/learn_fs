# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h lines 66378-69695

## Scope

This chunk is a contiguous middle slice of the generated LP11002 firmware image header. It remains inside `static uint8_t emlxs_lp11002_image[]`, guarded by `EMLXS_FW_IMAGE_DEF`, and contributes 26,544 firmware bytes from image offset `0x81980` through `0x8812F`.

The source file identifies the image as `LP11002-S: v2.82a4 (bf282a4.all)`. There is no host-side C function body in this line range; the bytes are precompiled adapter firmware represented as a C initializer.

## APIs and Exports

- `emlxs_lp11002_image[]`: this chunk appends raw bytes to the embedded LP11002 firmware image.
- `emlxs_lp11002_size`: defined later in the file as `sizeof (emlxs_lp11002_image)` when the image is compiled in.
- `emlxs_lp11002_label`, `emlxs_lp11002_kern`, `emlxs_lp11002_stub`, and `emlxs_lp11002_sli*`: defined at the file top outside this chunk; this chunk supplies image contents matching that metadata.

No structs, enums, driver callbacks, or callable C APIs are declared here. The only C-level behavior is inclusion/omission of firmware storage through the surrounding preprocessor conditional.

## Firmware Control Flow

The byte patterns decode as ARM-style firmware code mixed with literal pools and diagnostic strings. The chunk starts in the middle of a routine after the previous chunk and ends mid-routine; line 69696 continues the instruction stream at image offset `0x88130`.

Visible firmware behavior centers on Fibre Channel loop/link initialization and LIP processing, with strings for `INIT`, `INIT_LINK`, ENDEC configuration, source-ID setup, `RCVD_LIP_F8`, loop phase, port state, ARBF0, LIPF7/LIPF8, AL_PA maps, link-up, timeout, and XCB handoff.

Instruction-level patterns show repeated firmware subroutine prologues/epilogues, branch-with-link calls, conditional branches, literal-pool references, and compact copy/loop sequences. These are firmware-internal entry points and branches only; the host compiler treats them as immutable byte constants.

## State and Data

The firmware appears to manipulate memory-mapped or structure-relative state through repeated byte/word loads and stores. Visible offsets include low fields such as `0x04`, `0x07`, `0x08`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x26`, `0x27`, `0x28`, `0x30`, `0x38`, `0x39`, `0x3C`, `0x40`, `0x44`, `0x48`, `0x4C`, `0x50`, `0x54`, `0x58`, `0x5A`, `0x64`, `0x6A`, `0x70`, `0x72`, `0x78`, and `0x7C`, plus larger offsets such as `0x80`, `0x8C`, `0x90`, `0x98`, `0x9C`, `0xA3` through `0xA9`, `0xAC`, `0xB0`, `0xC0`, `0xC8`, `0xCC`, `0xD0`, `0x13D`, `0x17C`, `0x180`, `0x184`, `0x260`, `0x264`, `0x270`, `0x278` through `0x27A`, `0x290`, `0x300`, `0x304`, `0x370`, and `0x704`.

Repeated state themes include loop phase transitions, AL_PA election/map construction, LIPF7/LIPF8 receive/transmit state, FTXQ/SAISR_FTXQ transmit status, EOFa emission, and XCB-like dispatch.

## Dependencies

Host-side dependencies:

- `EMLXS_FW_IMAGE_DEF` controls whether `emlxs_lp11002_image[]` storage is emitted.
- `uint8_t` must be available from the including driver environment.
- `emlxs_fw.h` includes `fw_lp11002.h` when building the Emulex firmware table and binds this image under `LP11002_FW`.

Firmware-side dependencies:

- Branches and calls target routines before and after this chunk.
- Literal pointers and diagnostic-string references assume fixed byte offsets.
- Runtime semantics depend on LP11002 Emulex adapter hardware and firmware ABI, not illumos host C execution.

## Risks and Maintenance Notes

- Treat this chunk as opaque vendor firmware.
- Any byte edit can corrupt branch targets, literal pools, state offsets, checksums/signatures elsewhere in the image, or hardware-visible behavior while still compiling.
- Diagnostic strings are useful anchors, but not a complete interface contract.
- Apparent padding, repeated instructions, and small tables must be preserved byte-for-byte.
- The line range ends mid-routine; the following chunk is required for final return/error paths.

## Cross-Chunk References

- Previous chunk: supplies the routine prologue and setup for the code that continues at `0x81980`.
- Following chunk: continues the mid-routine path starting at `0x88130`.
- Earlier image regions contain common helpers reached by backward `EB`/`EA` branches.
- Later image regions contain handlers/data referenced by literal addresses in the `0x0008xxxx`, `0x0007xxxx`, and `0x000Bxxxx` ranges.