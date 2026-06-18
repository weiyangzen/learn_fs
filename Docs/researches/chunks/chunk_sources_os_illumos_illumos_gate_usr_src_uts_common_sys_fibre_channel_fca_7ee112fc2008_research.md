# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h lines 36516-39833

## Scope

- Subset: `Docs/research_subset_a.md`
- Source tree: `sources/os/illumos/illumos-gate`
- File: `usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h`
- Chunk: 12
- Lines: 36516-39833
- Firmware image offsets covered: `0x47450` through `0x4DBFF` inclusive, `0x67B0` bytes.

## What This Chunk Contains

This chunk is not host-side C logic. It is a contiguous middle section of the static `uint8_t emlxs_lp10000_image[]` firmware payload for Emulex LP10000/Thor Fibre Channel HBAs. The bytes decode as big-endian ARM instructions mixed with inline literal pools. The enclosing header identifies the image as `LP10000-S: v1.92a1 (td192a1.all)`.

Within this span I found 98 ARM-style routine prologues and many branches/calls to routines outside the chunk. The chunk therefore carries executable adapter firmware behavior, not C-callable APIs exposed directly to illumos.

## Host-Side API Surface

No new C declarations, structs, macros, or illumos driver entry points are introduced in this line range. The host-visible surface is inherited from surrounding file/header context: `emlxs_lp10000_image[]`, `emlxs_lp10000_size`, `emlxs_firmware_t` table integration, LP10000 adapter table entries, and firmware loader/download APIs such as `emlxs_fw_load()` and `emlxs_fw_download()`.

## Firmware Control Flow Visible In This Chunk

- `0x47450-0x476AC`: status/error collection, bitmask maintenance at offset `0x294`, counter snapshots from offsets like `0x78`, `0x7C`, `0x24`, `0x28`, `0x2C`, and a local boolean helper at `0x4765C`.
- `0x476B0-0x47787`: register/log update, including global offset `0x660`, byte register `0xD0`, ring/log writes near `0x4D000-0x4E000`, and writes through the `0x09000000` region.
- `0x47830-0x47A00`: event opcode dispatch for values including `0x03`, `0x13`, `0x1F`, `0x23`, `0x29`, `0x83`, `0x95`, `0x99`, `0x9B`, `0x9D`, `0xA1`, and `0xC3`.
- `0x47C7C`, `0x48068`, `0x488C0`, `0x48E80`: message/descriptor routing, descriptor flag updates including `0x1000` and `0x10000000`, and calls to local and outside helpers.
- `0x49700`, `0x49F88`, `0x4A19C`: descriptor/pool maintenance using global offsets `0x260`, `0x264`, `0x2E4` and descriptor fields `0x18-0x38`.
- `0x4C6D8`: interrupt/completion processing using pending-mask state at `0x118-0x120` and hardware-like register `0x0A000708`.
- `0x4D524-0x4D793`: initialization/teardown style routines guarded by global flags at `0xF8`/`0xFC`, manipulating registers including `0x0A00038C`, `0x0A000390`, and `0x0A000708`.
- `0x4D794-0x4DA87`: multi-lane bit/status aggregation from `0x0A000394`, `0x398`, `0x39C`, `0x3A0`, with lane flag `0x20000000`.
- `0x4DA88-0x4DBFF`: low-level serial/bit-bang sequencing via `0x0A000030`; the transaction helper begins at `0x4DB60` and continues into the next chunk.

## State And Data Dependencies

The firmware uses fixed adapter memory/register regions:

- `0x0A000000` register block: offsets `0x030`, `0x38C`, `0x390`, `0x394`, `0x398`, `0x39C`, `0x3A0`, `0x708`, `0x70C`.
- `0x09800000` register/control block: offsets around `0x100` and `0x44`.
- `0x09000000` buffer/table block: offsets around `0x004`, `0x300`, `0x380`, `0x500`, `0x690`.
- Low/global state offsets: `0x48`, `0x59`, `0x5A`, `0x5C`, `0x5D`, `0x70`, `0x80`, `0xD0`, `0xF8`, `0xFC`, `0x118-0x120`, `0x144`, `0x164`, `0x260-0x264`, `0x2E4`, `0x660`.

Inline literal pools point to firmware-global addresses such as `0x00037278`, `0x00037294`, `0x000372A8-0x000372E4`, `0x000392FC`, `0x0003969C`, `0x000396F8`, `0x00039CDC`, and `0x0002A7CC-0x0002A7EC`.

## Cross-Chunk References

- The chunk starts mid-routine; the first instruction calls `0x47338`, and register state is inherited from the previous chunk.
- Earlier firmware targets include `0x233F0`, `0x234A4`, `0x3C31C`, `0x3E2BC`, `0x3E320`, `0x40CBC`, `0x40CEC`, `0x46DC0`, `0x46E98`, `0x46ED8`, `0x472AC`, and `0x47338`.
- Later firmware targets include `0x52E24`, `0x53510`, `0x53F2C`, and `0x56B50`.
- The final routine at `0x4DB60` crosses the chunk boundary and continues at `0x4DC00`.

## Risks And Maintenance Notes

This is opaque proprietary firmware embedded in a kernel driver header. Normal C review cannot prove safety or correctness; meaningful changes require byte-for-byte provenance, vendor release notes, or firmware disassembly expertise. A one-byte edit can change branch targets, descriptor layout assumptions, or hardware sequencing.

Security and reliability risk is concentrated in firmware authenticity and update path handling, not in this chunk’s C syntax. The host driver embeds and downloads this payload to supported LP10000/Thor adapters through `emlxs_fw_table` and related firmware loader/download code.