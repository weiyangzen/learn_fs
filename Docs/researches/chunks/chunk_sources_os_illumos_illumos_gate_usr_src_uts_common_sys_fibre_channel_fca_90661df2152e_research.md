# Chunk Research: `fw_lp11000.h` Lines 16608-19925

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h`

Scope: `Docs/research_subset_a.md`, which includes `sources/os/illumos/illumos-gate`.

## Chunk Identity

This chunk is not host-executed C logic. It is an interior slice of `static uint8_t emlxs_lp11000_image[]`, the embedded firmware image for Emulex LP11000/LP11000-S Helios Fibre Channel adapters in the illumos `emlxs` driver.

The requested line range was read completely. Every line in the range is a firmware byte-array row, with no C declarations or preprocessor directives inside the chunk.

- Source lines: 16608-19925.
- Firmware offsets covered: `0x20630` through `0x26DDF`.
- Row count: 3,318 eight-byte rows.
- Byte span: 26,544 bytes.
- CRC32 over the eight data byte literals per row: `ddb75624`.
- Containing full image metadata visible outside the chunk: label `LP11000-S: v2.82a4 (bd282a4.all)`, full image size `0x893DC` bytes, and firmware entry symbols `emlxs_lp11000_image` / `emlxs_lp11000_size`.

## APIs And Host-Visible Surface

This chunk declares no C functions, structs, macros, or callable APIs.

The host-visible surface is the surrounding firmware artifact:

- `fw_lp11000.h` defines `emlxs_lp11000_label`, `emlxs_lp11000_kern`, `emlxs_lp11000_stub`, `emlxs_lp11000_sli1`, `emlxs_lp11000_sli2`, `emlxs_lp11000_sli3`, `emlxs_lp11000_sli4`, and conditionally `emlxs_lp11000_image[]`.
- `emlxs_fw.h` includes `fw_lp11000.h` and registers `LP11000_FW` in `EMLXS_FW_TABLE` using `emlxs_lp11000_size`, `emlxs_lp11000_image`, and the LP11000 metadata fields.
- `emlxs_adapters.h` maps LP11000-class Helios adapters, including the Oracle-branded `LP11000-S` and spare variants, to `LP11000_FW` with SLI2/SLI3 support masks.

## Firmware Control Flow Visible In The Blob

The bytes are structured like big-endian ARM firmware code mixed with literal data. Source-level C tooling only sees byte literals, but instruction-like patterns are clear:

- The chunk contains about 1,092 branch-class 32-bit words, 64 `E1 A0 F0 0E` return-style words, 74 push-like `E9 2D ...` words, and 64 pop-like `E8 BD ...` words.
- The first rows continue from the previous chunk and include return stubs, branch-with-link calls, and literal-pool-looking values such as `0x00085F2C` and `0x0008FFC0`.
- Visible code repeatedly reads, masks, and stores pointer-relative fields. Common offsets include small control/status bytes around `0x04`, `0x07`, `0x08`, `0x0A`, `0x0B`, `0x0F`, `0x1C`, `0x24`, `0x25`, `0x26`, `0x2C`, `0x30`, `0x40`, `0x44`, `0x48`, `0x4C`, `0x54`, `0x5C`, `0x60`, `0x64`, `0x68`, `0x6D`, `0x6E`, `0x70`, `0x73`, `0x7A`, `0x80`, `0x84`, `0x88`, `0x90`, `0x91`, `0x94`, `0x98`, `0x99`, `0x9A`, `0x9B`, `0xB2`, and larger firmware-private offsets such as `0x140`, `0x144`, `0x260`, `0x264`, `0x270`, `0x2A4`, `0x340`, `0x348`, `0x350`, `0x358`, `0x370`, `0x374`, `0x380`, and `0x3C0`.
- Several paths look like queue/control-block manipulation: copying linked descriptor fields, updating counters, clearing or setting flag words, and storing command/state bytes such as `0x41`, `0x57`, and `0x84`.
- The late section around `0x26730` starts a substantial routine that initializes or transforms a descriptor/control object: it clears fields, copies nested pointer data, updates flags at offsets `0x0C`, `0x14`, `0x18`, and `0x1C`, tracks counts at `0x24` and `0x64`, and branches into routines outside the chunk.
- No printable embedded diagnostics of length six or more were found in this exact slice; unlike neighboring firmware regions, this one is primarily instruction/data words.

## State And Dependencies

The state visible here is firmware-private adapter state, not illumos C structs. The repeated fixed offsets indicate on-card control blocks, hardware register mirrors, queues, counters, and descriptor fields. The host driver depends on the complete image being passed to the adapter unchanged.

Dependencies:

- Compile-time: `emlxs_lp11000_image[]` is emitted only when `EMLXS_FW_IMAGE_DEF` is defined; otherwise the header exposes zero-valued image/size macros.
- Driver table: `emlxs_fw.h` binds the image to the `LP11000_FW` firmware id.
- Adapter table: `emlxs_adapters.h` assigns `LP11000_FW` to Helios LP11000-family 4Gb Fibre Channel HBAs with SLI2/SLI3 support.
- Runtime: the LP11000 adapter CPU, firmware memory map, SLI firmware ABI, DMA/queue layout, and Fibre Channel link/exchange state machines.

## Risks And Maintenance Notes

- Any byte-level change can alter firmware branches, literal pools, state-field offsets, or hardware sequencing.
- The blob includes many PC-relative branches/calls; moving bytes, deleting rows, or merging chunks incorrectly would corrupt execution.
- Normal C review cannot validate bounds, concurrency, link recovery, mailbox behavior, or DMA safety inside the firmware.
- The chunk has no local checksum or semantic guard. Integrity must be preserved by source control, build reproducibility, and the surrounding firmware loading path.
- Failures in this region would likely appear as adapter initialization problems, link state instability, mailbox/IO timeouts, queue corruption, or SLI2/SLI3 protocol failures.

## Cross-Chunk References

- Previous chunk: line 16608 starts at image offset `0x20630`, immediately after code around `0x20620-0x20628`; the first instruction-like row is a PC-relative operation followed by a backward branch, so execution context comes from the prior chunk.
- Next chunk: line 19925 ends at the row beginning `0x26DD8`. The next row at `0x26DE0` continues the same routine, including additional conditional branches and calls.
- Header declarations and image-size definitions are outside this chunk at the file boundaries. The per-file merge should treat this report as one contiguous payload segment of `emlxs_lp11000_image[]`, not as an independent C module.