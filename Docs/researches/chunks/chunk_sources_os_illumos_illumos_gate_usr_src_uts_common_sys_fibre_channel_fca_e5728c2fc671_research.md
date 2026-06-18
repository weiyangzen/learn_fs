# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe12000.h lines 36515-39832

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe12000.h` lines 36515-39832 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration and byte offsets.

The chunk is 26,544 bytes from embedded `emlxs_lpe12000_image[]` firmware, covering image offsets `0x47448` through `0x4DBF7`. Adjacent context identifies the image as `LPe12000-S: v2.01a4 (ud201a4.all)`, guarded by `EMLXS_FW_IMAGE_DEF`, with total image size `0x75C0C`.

## APIs And Exported Data

This chunk contributes bytes to one private static object:

- `static uint8_t emlxs_lpe12000_image[]`: the LPe12000 firmware payload compiled into the Emulex `emlxs` Fibre Channel adapter driver when `EMLXS_FW_IMAGE_DEF` is set.

There are no C functions, macros, structs, typedefs, ioctl handlers, or illumos kernel entry points defined in this range. The visible C-facing names are outside this chunk: firmware metadata macros such as `emlxs_lpe12000_label`, `emlxs_lpe12000_kern`, `emlxs_lpe12000_stub`, `emlxs_lpe12000_sli2`, `emlxs_lpe12000_sli3`, and `emlxs_lpe12000_size`.

## Firmware Control Flow

The bytes decode structurally like big-endian ARM code/data. Within 6,636 apparent 32-bit words, I observed 68 apparent function prologues, 172 branch-with-link instructions, 919 non-link branches, 33 direct `MOV pc, lr` style returns, and 67 `LDM... pc` epilogues.

There are jump-table/dispatch-like regions around `0x47B00-0x47E34`, including compact unconditional branch tables to handlers inside and outside this chunk.

Control flow is heavily cross-range. Frequently referenced in-chunk targets include `0x47560`, `0x476AC`, `0x47A64`, `0x48C2C`, `0x49788`, `0x49EF0`, `0x4C0A8`, `0x4CE94`, `0x4D620`, and `0x4D824`. Frequent out-of-chunk targets include earlier offsets like `0x44D98`, `0x45DC8`, `0x45DD0`, `0x46468`, `0x46700`, and later offsets like `0x5F6CC`, `0x605F0`, `0x624A8`, `0x6F260`, `0x721F0`, `0x73388`, and `0x737E0`.

Because this is binary firmware without symbols, semantic handler names are not visible. The structure suggests multiple small state handlers, queue/message helpers, and event dispatch paths.

## State And Dependencies

No host-side C state is declared or mutated here. Runtime state is firmware-internal and only visible through encoded load/store offsets.

Recurring byte fields include `0x07`, `0x08`, `0x0A`, `0x0B`, `0x0F`, `0x24`, `0x26`, `0x27`, `0x3C`, `0x70`, `0x73`, and `0xA7`. Recurring word fields include `0x00`, `0x04`, `0x08`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x28`, `0x2C`, `0x30`, `0x38`, `0x40`, `0x44`, `0x50`, `0x64`, `0x74`, `0x78`, `0x7C`, `0x80`, and `0x260`. These look like firmware control block, mailbox/message descriptor, queue, or adapter-local memory layout accesses.

Host-side dependencies are `uint8_t`, `EMLXS_FW_IMAGE_DEF`, and `#pragma align 8(emlxs_lpe12000_image)`. Operationally, the `emlxs` driver must match this image to LPe12000-compatible adapters, and firmware metadata offsets outside the chunk must remain consistent with the binary payload.

## Risks And Cross-Chunk References

A single-byte edit can alter firmware instructions, branch targets, literal pools, or internal control-block offsets. Normal C type checking and unit testing will not detect semantic corruption in this opaque initializer.

The chunk begins immediately after prior code/literal content; the first word at `0x47448` appears to be a literal-pool value for preceding code. It ends mid-code at `0x4DBF7`, with the next chunk continuing the routine around `0x4DBF8`.

Branches reference earlier chunks extensively around `0x44xxx-0x46xxx` and later chunks around `0x5Fxxx-0x73xxx`. A final per-file report should merge this as a middle firmware-code segment, not an independent C module.