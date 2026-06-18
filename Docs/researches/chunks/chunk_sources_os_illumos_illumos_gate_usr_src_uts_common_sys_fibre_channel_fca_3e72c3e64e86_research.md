# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe12000.h lines 16607-19924

## Scope

- Subset: `Docs/research_subset_a.md`, which includes `sources/os/illumos/illumos-gate`.
- File: `fw_lpe12000.h`, Emulex LPe12000 firmware image header for the illumos `emlxs` Fibre Channel adapter driver.
- Chunk: lines 16607-19924, exactly 3,318 consecutive byte-array lines.
- Firmware image offsets covered by this chunk: `0x20628` through `0x26DD0`.
- Data covered: 26,544 bytes, 6,636 big-endian 32-bit words if interpreted as ARM instruction/data words.
- Chunk CRC32 over only the byte literals in this line range: `c828bb52`.

## APIs And Exposed Surface

This chunk defines no C functions, types, macros, or callable driver APIs by itself. It is an interior slice of:

- `static uint8_t emlxs_lpe12000_image[]`, emitted only when `EMLXS_FW_IMAGE_DEF` is defined.
- The larger header-level firmware metadata: `emlxs_lpe12000_label`, `emlxs_lpe12000_kern`, `emlxs_lpe12000_stub`, `emlxs_lpe12000_sli1`, `emlxs_lpe12000_sli2`, `emlxs_lpe12000_sli3`, `emlxs_lpe12000_sli4`, and `emlxs_lpe12000_size`.

The driver-facing registration is outside this chunk: `emlxs_fw.h` maps `LPe12000_FW` to `emlxs_lpe12000_size`, `emlxs_lpe12000_image`, and the firmware labels/check values. `emlxs_adapters.h` assigns `LPe12000_FW` to Saturn/LPe12000-family adapter entries, including single-channel, dual-channel, Oracle-branded, express-module, and spare variants.

## Firmware Control Flow Visible In The Blob

Although the C compiler only sees byte literals, the bytes are structured like ARM firmware code:

- The chunk begins mid-routine at image offset `0x20628`, continuing control flow started in the previous chunk.
- The chunk contains many ARM branch/call/return patterns: approximately 924 branch-class words and many `E1 A0 F0 0E` return-style words.
- It contains multiple routine prologues/epilogues encoded as block transfers, e.g. `E9 2D ...` push-like sequences and `E8 BD ...` pop/return-like sequences.
- It contains jump-table or dispatch-table regions, notably around offsets `0x23428-0x23460` and `0x24250-0x242B8`.
- It classifies command/status bytes such as `0x80`, `0x81`, `0x82`, `0x83`, `0x84`, `0x85`, `0x8B`, `0xE0`, `0xF0`, and `0xFF`.
- It includes coprocessor/cache-maintenance-looking instructions (`0xEE...`, `0xF5...`) around offsets such as `0x21520`, `0x21AF8`, `0x22E48-0x22E80`, and `0x23288-0x23298`.

## State And Data Dependencies

The visible firmware code heavily manipulates memory through fixed offsets from register-held base pointers. Recurrent offsets likely represent firmware-private control blocks rather than C-visible structs.

Literal pointer/table values appear inside the range, including `0x009D2BBC`, `0x009D28CC`, `0x009D28BC`, `0x009D28DC`, and several `0x009D2754` references. These are firmware-address constants, not host kernel addresses.

A small data-table-looking area appears around `0x232B0-0x232BC`: `0x0C000400`, `0x0C000600`, `0x00105000`, `0x0C000000`.

Command/status descriptor constants appear around `0x24CF8-0x24F6C`, including `0x00101211`, `0x00201211`, `0x00404212`, `0x10104212`, and `0x02000FFF`.

## Dependencies

- Compile-time dependency: this byte array exists only for compilation units defining `EMLXS_FW_IMAGE_DEF`; otherwise `emlxs_lpe12000_image` and `emlxs_lpe12000_size` are defined as zero.
- Driver dependency: `emlxs_fw.h` consumes the whole image and metadata as a firmware table entry for `LPe12000_FW`.
- Adapter dependency: `emlxs_adapters.h` maps `LPe12000_FW` to LPe12000/LPe12002 Saturn-family adapters with SLI2/SLI3 support masks.
- Hardware dependency: the blob is firmware for Emulex Saturn/LPe12000 8Gb Fibre Channel HBAs.

## Risks And Maintenance Notes

- The chunk is opaque binary firmware encoded as C source. Normal C review cannot validate safety, bounds, protocol correctness, or hardware-side behavior.
- Any byte change in this range can silently alter firmware control flow, tables, or hardware register handling.
- The C file has no local checksum enforcement for this chunk. Integrity appears to rely on surrounding firmware metadata and the driver/firmware loading path.
- The blob includes absolute-looking firmware addresses and PC-relative branch/call offsets. Moving bytes within the image or chunking/merging incorrectly would corrupt execution.
- Bugs here could surface as adapter initialization failures, mailbox/IO timeouts, incorrect link state, or data path instability.

## Cross-Chunk References

- Previous chunk: this chunk starts mid-routine. Lines immediately before 16607 perform bit masking and looped updates around offsets `0x1A0`, `0x1A4`, and `0x1A8`.
- Next chunk: this chunk ends mid-routine at `0x26DD0`; line 19925 continues the same instruction sequence at `0x26DD8`.
- Header start and end are outside this chunk. The declarations and firmware size are at the file boundaries, while this chunk is pure interior payload.
- Per-file merge should describe this as one slice of the single `emlxs_lpe12000_image[]` object, not as an independent module.