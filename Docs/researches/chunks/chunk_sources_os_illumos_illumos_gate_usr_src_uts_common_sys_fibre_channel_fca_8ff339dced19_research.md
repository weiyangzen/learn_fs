# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 36516-39833

## Scope

- Subset: `Docs/research_subset_a.md`, which includes `sources/os/illumos/illumos-gate`.
- File: `fw_lp11000.h`, Emulex LP11000 firmware image header for the illumos `emlxs` Fibre Channel adapter driver.
- Chunk: ordered chunk 12, lines 36516-39833, exactly 3,318 consecutive byte-array lines.
- Firmware image offsets covered: `0x47450` through `0x4DBF8`.
- Data covered: 26,544 bytes, or 6,636 32-bit words if interpreted as ARM instruction/data words.

## APIs And Exposed Surface

This chunk defines no host-callable C functions, structs, enums, or macros. It is an interior slice of `static uint8_t emlxs_lp11000_image[]`, which exists only when `EMLXS_FW_IMAGE_DEF` is defined. Without that define, the same header exposes `emlxs_lp11000_image` and `emlxs_lp11000_size` as zero.

Driver integration is through `emlxs_fw.h`, which maps `LP11000_FW` to `emlxs_lp11000_size`, `emlxs_lp11000_image`, label, and firmware check values. `emlxs_adapters.h` assigns `LP11000_FW` to LP11000, LP11000-S/Oracle, and spare 4Gb 1-port PCI-X2 FC HBA adapter entries.

## Firmware Control Flow Visible In The Blob

The C compiler sees only bytes, but the data is structured like ARM firmware:

- The chunk begins mid-routine at `0x47450`; the prologue and earlier condition setup are in the previous chunk.
- It contains many ARM branch, branch-link, and return-style words, including repeated `E9 2D ...` push-like prologues, `E8 BD ...` pop-like epilogues, and `E1 A0 F0 0E` returns.
- Several dispatch/jump-table regions are visible, especially around `0x486E0-0x48860`, `0x48F98-0x49060`, `0x4CFE8-0x4D0E8`, and `0x4CDD0-0x4CE80`.
- Embedded diagnostic/log strings visible in this range include fragments or full strings for `PRG_LOGIN %02x`, `INIT %08x`, `INIT_LINK %02x`, `ENDEC PCFG:`, `Our SID: %08x`, `DWNL %08x`, and `T/O x %x %x`.

## State And Data Dependencies

The firmware updates memory through register-relative offsets that appear to be private adapter/port/command control blocks rather than C structs. Recurrent fields include `0x04`, `0x06`, `0x07`, `0x08`, `0x0A`, `0x0B`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x28`, `0x2C`, `0x30`, `0x3C`, `0x40`, `0x44`, `0x4C`, `0x50`, `0x58`, `0x5C`, `0x60-0x6C`, `0x70-0x80`, `0x88`, `0xA0-0xA9`, `0xB0`, `0xB1`, `0xB8`, and larger control areas such as `0x0260`, `0x0264`, `0x0270`, `0x0278`, `0x0360-0x0374`, and `0x12C0-0x12C8`.

The blob repeatedly writes small state codes to offset `0x07` and nearby status bytes, including visible values such as `0x38`, `0x41`, `0x44`, `0x46`, `0x48`, `0x57`, `0x58`, `0x80`, `0x84`, `0x88`, `0xB0`, and `0xB1`.

## Dependencies

- Compile-time dependency: `EMLXS_FW_IMAGE_DEF` controls whether this byte payload is compiled into a consumer object.
- Driver dependency: `emlxs_fw.h` consumes the complete LP11000 image and metadata as the firmware table entry for `LP11000_FW`.
- Adapter dependency: `emlxs_adapters.h` maps `LP11000_FW` to the supported LP11000-family adapter records.
- Hardware dependency: the bytes are firmware for Emulex LP11000/LP11000-S 4Gb Fibre Channel HBA hardware.

## Risks And Cross-Chunk References

This is opaque executable firmware encoded as C source. Normal C review cannot validate memory safety, bounds, hardware sequencing, or Fibre Channel protocol correctness. Any byte edit can alter branch targets, dispatch tables, embedded literals, or state-machine transitions.

Previous chunk: this range starts mid-routine at `0x47450`. Next chunk: this range ends mid-routine at `0x4DBF8`; the following line continues at `0x4DC00` with stores into fields around `0x20-0x2C`. Per-file merge should treat this as one interior slice of the single `emlxs_lp11000_image[]` firmware object, not as an independent source module.