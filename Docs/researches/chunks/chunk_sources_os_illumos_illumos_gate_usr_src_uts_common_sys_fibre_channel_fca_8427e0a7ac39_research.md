# Chunk Research: `fw_lp11002.h` Lines 13290-16607

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h`

Scope note: this report covers only lines 13290-16607 for learn_fs subset A. The range is entirely inside the generated `static uint8_t emlxs_lp11002_image[]` initializer, guarded by `EMLXS_FW_IMAGE_DEF`. It is LP11002-S adapter firmware data represented as C byte initializers, not host-executed illumos C logic.

## Chunk Extent

- Source lines read completely: 13290-16607.
- Firmware image offsets covered: row `0x19E80` through row `0x20628`, ending at byte `0x2062F`.
- Byte span represented: 3,318 eight-byte rows, 26,544 bytes.
- File-level metadata identifies the image as `LP11002-S: v2.82a4 (bf282a4.all)` with total image size `0x8DCB8`.

## APIs and Integration Surface

- This chunk declares no C functions, structs, enums, macros, or callable driver APIs.
- Its only host-visible contribution is another contiguous segment of `emlxs_lp11002_image[]`.
- `emlxs_fw.h` includes `fw_lp11002.h` while building `EMLXS_FW_TABLE`; the `LP11002_FW` descriptor binds `emlxs_lp11002_size`, `emlxs_lp11002_image`, label, kernel/stub addresses, and SLI constants.
- `emlxs_adapters.h` maps generic, Oracle-branded, and spare LP11002 adapter records to `LP11002_FW`.

## Firmware Control Flow and Data Visible

- The chunk starts mid-routine at firmware offset `0x19E80`, continuing ARM-style firmware instruction bytes from the previous chunk.
- Around `0x1A0D0-0x1A4A8`, compact firmware routines copy/compare repeated word patterns, followed by a small test table with markers such as `0xA55AA55A`, `0x5AA55AA5`, and `0x55555555`.
- A long zero-filled region begins at `0x1A510`; nonzero structured table data resumes at `0x1C080`.
- Around `0x1C880-0x1C998`, descriptor/header-style data includes firmware metadata-like values such as `0x07C12894`.
- Around `0x1DF80-0x1DFC0`, embedded diagnostic strings mention external/internal SerDes not detected.
- ARM-style executable firmware resumes around `0x1E038`.
- Around `0x1EE80-0x1EF20`, the chunk mixes offset tables, firmware identity/version fragments such as `BS2.82A4`, stub address-like value `0x02C82894`, and initialization code.
- Around `0x1FDA0-0x1FDF8`, descriptor/version data appears again, including `0x06C12893` and visible `B1F2.82A3`.
- From `0x1FE00` through `0x2062F`, the data is zero-filled padding/reserved image space.

## State, Dependencies, Risks

Host-side state is immutable firmware payload data; there is no mutable C state in this chunk. Firmware-visible state is only inferable from encoded bytes: register operations, table descriptors, branch targets, memory-copy loops, hardware/control words, SerDes diagnostics, and version/address records.

Runtime dependencies are the LP11002 adapter CPU, its memory map/register layout, Fibre Channel/SLI firmware ABI, and host firmware download/load paths that transfer `emlxs_lp11002_image[]` unchanged.

A single byte change can corrupt adapter firmware instructions, branch targets, literal pools, descriptor tables, version records, or reserved padding. The zero-filled sections may be intentional alignment, reserved memory, or sparse image space, so removing/compressing them would shift later firmware offsets.

## Cross-Chunk References

- Previous chunk lines 9972-13289 ends at offset `0x19E7F`; this chunk begins immediately at `0x19E80` and starts mid-control-flow.
- Next chunk lines 16608-19925 begins at offset `0x20630`, immediately after this chunk’s zero-filled tail.
- File-level merge should treat this as one segment of the opaque LP11002 firmware payload and combine it with the other chunks before drawing conclusions about full image layout, branch reachability, or firmware integrity.