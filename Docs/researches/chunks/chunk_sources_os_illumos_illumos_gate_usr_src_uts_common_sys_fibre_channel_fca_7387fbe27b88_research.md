# Chunk Research: `fw_lpe11000.h` Lines 46469-49786

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h`

Scope note: this chunk is entirely inside `static uint8_t emlxs_lpe11000_image[]`, the embedded firmware image for the Emulex LPe11000-S Fibre Channel adapter. It is not host-executed C logic. The C compiler only stores these bytes in the driver image when `EMLXS_FW_IMAGE_DEF` is enabled.

## Chunk Extent

- Source lines read completely: 46469-49786.
- Firmware image offsets covered: `0x5AB58` through the eight-byte row beginning at `0x61300`, ending at byte `0x61307`.
- Byte span represented: `0x67B0` bytes, 26,544 bytes total.
- Adjacent metadata identifies the full image as `emlxs_lpe11000_image[]` with size `0x8A5CC` bytes and label `LPe11000-S: v2.82a4 (zd282a4.all)`.

## APIs and Integration Surface

- This chunk exports no C functions, macros, structs, or callable APIs of its own.
- Its only C-visible surface is the containing `emlxs_lpe11000_image[]` byte array.
- The public header-level interface is outside this chunk: firmware label/address macros, `emlxs_lpe11000_image`, and `emlxs_lpe11000_size`.
- Host-side code must treat this region as opaque firmware data; its meaningful ABI is the byte-exact adapter firmware image consumed by the Emulex firmware loader.

## Firmware Control Flow Visible

- The first bytes continue a routine from the previous chunk. The visible code updates byte-sized and word-sized state around offsets such as `0x06`, `0x07`, `0x0C`, `0x10`, `0x12`, `0x13`, `0x18`, `0x28`, `0x2C`, `0x30`, `0x3C`, `0x4F`, `0x50`, `0x70`, `0x79`, `0x90`, `0x98`, `0x9C`, `0xA8`, `0xB0`, `0xB4`, `0xBC`, `0xC0`, `0xC4`, `0xC8`, `0xCC`, `0x170`, `0x17C`, `0x180`, `0x184`, `0x260`, `0x264`, `0x2F0`, `0x374`, and `0x700`.
- Multiple jump-table-like sequences are visible. One near `0x5AD30` dispatches link/loop phases, and another larger case dispatch appears around `0x5DFC0`-`0x5E030`.
- The chunk contains many `BL`/`B`-style branch encodings to helper routines both before and after this line range, so most routines are not independently analyzable from this chunk alone.
- Visible diagnostic strings show loop initialization and link-state state-machine paths: `Ill phase`, `RCVD_LIP_F8`, `lipf8_rcvd`, `tx_close_timeout`, `LPB and LPE Rcvd=>ignored`, `Unknown port_state=%x`, `Loop Phase=%x`, `Monitor State:Loop_Phase=%x`, `ARBF0 in ill phase=%x`, `To OPEN_INIT Due To:`, `To OPEN_INIT Due To: lipf7_rcvd`, `ARBF0`, `Ignored(Not a LISM`, `MASTER`, `XMT_ARBF0`, `FL_PORT`, `LIFA`, `LIPA`, `LIHA`, `LISA`, `LIRP`, `LILP`, `XMT_CLS`, `CLS`, `LINK IS UP!`, `Rcvd Frame called`, `no interrupt`, `Timeout TX Never IDLE`, `Never Sync`, `Never Acquired Sync`, `Sending EOFa`, `FTXQ int never set`, and `SAISR_FTXQ never set`.
- Additional visible strings show LIP handling and exchange/logging paths: `1:Issue LipF8s`, `2:Issue LipF8s`, `Issue LipF7 Reset to AL_PA=%x`, `Issue LipF7s`, `lipf8 Active Rcvd:`, `LIPF8s > 2 secs`, `LIPF8 from myself`, `LIPF7 not from myself`, `Xmit 30ms of LIPF7s`, `loopi 2 LPRQ_INIT. State = %08x`, `LPTOV Timeout`, `ILV=>REINIT=%x`, `Rcvd:`, `Xmit:`, `Buf=%02x`, `wwn1=%08x:wwn2=%08x:`, `XMT_LIHA`, `XMT_LIFA`, `XMT_LIPA`, `XMT_LISA`, `XMT_LIRP`, `XMT_LILP`, `XMT_LISM`, `RCV_`, `RCV_MyLIPF8 : DID=%08x`, and `Sending %s->xcb %x`.
- Late in the chunk, code transitions from active routines into tables and firmware descriptors. Visible ASCII/table labels include `LINK`, `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `RDM2`, `TDMA`, `LMAU`, `PCIR`, and `DEND`.

## State and Dependencies

- The firmware-visible state is pointer-relative adapter state, not C structs visible in this header. It includes link/loop phase bytes, port state, AL_PA/position-map-like fields, counters, queue pointers, exchange-control fields, and hardware register mirrors.
- State transitions visible in the byte stream include LIP F7/F8 receive/transmit paths, OPEN_INIT transitions, ARBF0 handling, LISM/LIFA/LIPA/LIHA/LISA/LIRP/LILP transmit/receive paths, CLS transmit handling, link-up completion, timeout/retry paths, and frame/exchange logging.
- There are table-driven sections for hardware blocks or dump/register groups (`BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `TDMA`, `LMAU`, `PCIR`), followed by address/count records and zero-filled reserved data.
- Runtime dependencies are the LPe11000 adapter CPU, its ARM instruction set, firmware memory map, hardware registers, Fibre Channel loop/SLI conventions, and exact in-card data-structure layout.
- Build-time dependency is simply inclusion under `EMLXS_FW_IMAGE_DEF`; outside that define the header exposes zero-valued `emlxs_lpe11000_image` and size macros rather than the byte array.

## Risks

- A single-byte change can corrupt firmware instructions, branch targets, literal pools, state tables, register descriptors, or reserved layout.
- The firmware appears endian-sensitive and instruction-set-sensitive; normal C tooling cannot validate the semantics of this byte stream.
- The visible control flow includes polling/timeouts for transmit idle, sync acquisition, FTXQ interrupt bits, LIP handling, and link-up, so wrong surrounding state can plausibly hang initialization or link recovery.
- State-machine strings indicate many rare/error paths: illegal phases, unknown port states, ignored loop primitives, sync failures, LPTOV timeout, and unexpected frame/interrupt conditions.
- The late descriptor/table region increases integrity risk because offsets and counts likely need to match firmware loader or dump logic expectations exactly.

## Cross-Chunk References

- This chunk begins mid-routine; the preceding chunk contains the start of the state update logic that reaches line 46469.
- Many branch/call targets go backward to earlier helper code and forward past line 49786, so this chunk should not be treated as self-contained.
- The final lines are in a zero-filled/reserved table area beginning after visible descriptor records; the next chunk continues that reserved/data-table region.
- Final per-file analysis should merge all chunks before drawing conclusions about complete firmware layout, branch reachability, or adapter initialization behavior.