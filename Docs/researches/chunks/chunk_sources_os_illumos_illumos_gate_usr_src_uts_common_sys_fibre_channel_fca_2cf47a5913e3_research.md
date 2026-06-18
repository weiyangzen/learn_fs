# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 53106-56423

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.
- File role: generated/embedded Emulex LP11000 firmware image header, not ordinary C driver logic.
- Enclosing artifact: `static uint8_t emlxs_lp11000_image[]`, compiled only when `EMLXS_FW_IMAGE_DEF` is defined.
- Firmware identity from file context: `LP11000-S: v2.82a4 (bd282a4.all)`.
- Chunk coverage: 3,318 contiguous 8-byte rows, firmware offsets `0x67AC0` through `0x6E26F`, about `0x67B0` bytes. The next source line continues at offset `0x6E270`.

## APIs And Host Surface

- No C functions, structs, enums, typedefs, or callable illumos kernel APIs are declared in this range.
- Host-visible surface is the enclosing firmware byte array; the `emlxs` driver treats it as opaque adapter firmware.
- Surrounding context controls image materialization: with `EMLXS_FW_IMAGE_DEF`, the byte array and `sizeof` size are emitted; otherwise image/size macros resolve to `0`.

## Control Flow

- Bytes decode as ARM-style firmware code/data, with prologues, epilogues, direct branches, branch-with-link calls, and dense dispatch tables.
- The chunk begins mid-control-path around `0x67AC0`; the previous chunk contains the setup.
- Early code checks fields around offsets `0x07`, `0x14`, `0x18`, `0x1C`, `0x30`, `0x33`, `0x34`, `0x60`, `0x64`, `0x6C`, `0x80`, `0x8C`, and `0xA7`, with constants including `0x99`, `0x9B`, `0x9D`, `0xAF`, `0xB8`, and `0x9F`.
- Dense jump/dispatch-table regions appear around `0x69678`, `0x6D858`-`0x6DB50`, `0x6D9E8`, `0x6DA78`, `0x6DAB8`, and `0x6E018`.
- Around `0x6D6B8`, code branches over embedded diagnostic text, then resumes at `0x6D6D8`.
- The chunk ends at `0x6E268` with a return/pop followed by a helper branch; line 56424 continues at `0x6E270`.

## State, Dependencies, Risks

- Dominant state is firmware-private fixed-offset structure memory, including small offsets from `0x04` through `0xAF` and larger offsets such as `0x260`, `0x264`, `0x27C`, `0x290`, `0x2F0`, `0x304`, and `0x35C`.
- Embedded diagnostic text at `0x6D6BC`: `ABTS XRI/RPI %08x (%x)`, identifying a nearby abort-sequence/exchange path.
- Dependencies: LP11000 hardware execution environment, ARM instruction encoding, Emulex mailbox/SLI behavior, and driver-side firmware selection/loading.
- Risks: opaque binary behavior, byte-integrity sensitivity, jump-table alignment sensitivity, and incomplete invariants at chunk boundaries.

## Cross-Chunk References

- Previous chunk supplies incoming control flow before `0x67AC0`.
- Next chunk begins at `0x6E270` and continues adjacent firmware routines.
- File-level merge should preserve the single image array, label/version, total image size `0x893DC`, and `EMLXS_FW_IMAGE_DEF` conditional behavior.