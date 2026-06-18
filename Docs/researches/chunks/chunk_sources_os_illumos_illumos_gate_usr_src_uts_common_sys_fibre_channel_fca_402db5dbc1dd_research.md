# Chunk Research: `fw_lp10000.h` Lines 26562-29879

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h`

This chunk is a contiguous slice of the `emlxs_lp10000_image[]` firmware byte initializer, not ordinary host-side C logic. The enclosing header exports LP10000 firmware metadata macros and, when `EMLXS_FW_IMAGE_DEF` is defined, the aligned `static uint8_t emlxs_lp10000_image[]`; this chunk contributes only opaque firmware bytes inside that array. The chunk covers firmware offsets `0x33D40` through `0x3A4EF`, 3,318 source lines and 26,544 initializer bytes.

## API Surface

- No C functions, structs, enums, or callable driver APIs are defined in this range.
- Host-visible contract is inherited from the file-level image definition: byte order, array position, size, and alignment must remain exact.
- Firmware-resident diagnostics suggest FC-AL/link routines, but they are not directly callable from illumos C code.

## Control Flow

- Starts mid-firmware routine from chunk 8, comparing port/loop state values such as `0xB0`, `0x80`, `0x90`, `0xC0`, and `0xE0`.
- Handles unknown/monitor loop phases and OPEN_INIT transitions. Visible strings include `Unknown port_state=%x`, `Loop Phase=%x`, `Monitor State:Loop_Phase=%x`, `ARBF0 in ill phase=%x`, and `To OPEN_INIT Due To: lipf7_rcvd`.
- Middle section handles FC-AL primitives and arbitration/link state: `ARBF0`, `IAM_MASTER`, `XMT_ARBF0`, `LIFA`, `LIPA`, `LIHA`, `LISA`, `LIRP`, `LILP`, `XMT_CLS`, `Master BitMap`, `#of ALPA=%x`, `PosMap=>%02x`, and `LINK IS UP!`.
- Send/receive paths are visible for `XMT_LIHA`, `XMT_LIFA`, `XMT_LIPA`, `XMT_LISA`, `XMT_LIRP`, `XMT_LILP`, `XMT_LISM`, `XMY_LISM`, `LIPF7`, and `RCV_MyLIPF8 : DID=%08x`.
- Error/retry paths include `Timeout TX Never IDLE`, `Never Sync`, `Never Acquired Sync`, `Sending EOFa`, `FTXQ int never set`, and `SAISR_FTXQ never set`.
- Around `0x38958`, executable-looking words give way to a large zero-filled/literal-table region with sparse constants such as `0x2710`, `0x0800`, `0x0100`, `0x1000`, `0x0200`, `0x2000`, and `0x0400`.

## State, Dependencies, Risks

Visible state is firmware-private and pointer-relative, with dense accesses to per-port/loop/exchange/hardware fields including `+0x0C`, `+0x10`, `+0x14`, `+0x28`, `+0x50`, `+0x78`, `+0xA0`, `+0xC8`, `+0xDC`, `+0x170`, `+0x17C`, `+0x2F0`, `+0x660`, and `+0x808`-range offsets. The chunk depends on the LP10000 adapter CPU, firmware memory map, SLI/FC-AL conventions, and helper routines/data tables outside this range.

Primary risks are byte-level corruption of branch targets, literal pools, timing-sensitive link recovery, and table boundaries near the zero-filled region. Normal C tooling can only validate that the array compiles, not that firmware semantics remain valid.

## Cross-Chunk References

- Previous chunk: entry conditions and setup precede line 26562, including an earlier `LPB and LPE Rcvd=>ignored` path.
- Next chunk: the zero-filled/literal-table region continues past line 29879.
- Whole file: this must be merged as one segment of the LP10000 firmware image, not as an independent C module.

## Verification Notes

- Read line range `26562-29879` completely.
- Counted 3,318 source lines.
- Parsed 26,544 initializer bytes.
- Source slice SHA-256: `baa6ba9358cc5575abe0f9f3680ebe2403580a06081ec502f9396d7e89efa204`.