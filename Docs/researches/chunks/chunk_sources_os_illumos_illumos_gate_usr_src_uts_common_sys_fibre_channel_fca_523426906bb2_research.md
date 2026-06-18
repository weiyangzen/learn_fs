# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 69695-73012

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`; this chunk is within that exact subset.
- File role: generated/embedded Emulex LPe11002 firmware header for the illumos `emlxs` Fibre Channel driver, not host-executed C implementation.
- This range is entirely inside `static uint8_t emlxs_lpe11002_image[]`, visible only when `EMLXS_FW_IMAGE_DEF` is used by the including translation unit.
- Firmware identity from file context: `LPe11002-S: v2.82a4 (zf282a4.all)`, with full image size `0x8F3A8`.
- Chunk coverage: source lines 69695-73012, firmware byte offsets `0x88128` through the row beginning at `0x8E8D0`, ending at byte `0x8E8D7`.
- Byte span represented: `0x67B0` bytes, 26,544 bytes total.

## APIs And Host Surface

- No C functions, typedefs, structs, macros, or illumos kernel APIs are declared in this range.
- The only C-visible surface is the enclosing firmware byte array `emlxs_lpe11002_image[]`.
- Host integration is indirect: surrounding file metadata and `emlxs_fw.h` register this image in the LPe11002 firmware table entry using the image pointer, size, label, and SLI version constants.
- The bytes are opaque to host C. The illumos driver downloads them to the adapter; it does not call firmware-internal routines as C symbols.

## Firmware Control Flow Visible

- The byte stream continues to decode consistently as big-endian ARM-style adapter firmware, with register-save prologues, returns, branch-with-link calls, unconditional branches, PC-relative literal loads, and table-driven dispatch.
- The range begins mid-firmware logic at `0x88128`, immediately after prior-chunk diagnostic strings for transmit-queue interrupt assertions. The first visible routines test per-context flags and write small state bytes at offsets such as `0x09`, `0x0A`, `0x0B`, `0x0D`, `0x70`, `0x98`, and `0xB0`.
- Around `0x88518`-`0x88760`, the firmware contains loop initialization/reset paths for Fibre Channel loop primitives, including LIPF8/LIPF7 handling, `AL_PA` reset, `LPRQ_INIT`, and `LPTOV Timeout`.
- Around `0x88768`-`0x88910`, code copies or derives many link/session option bits from one control word into a larger state block.
- Around `0x88D04`-`0x890A0`, diagnostic strings describe receive/transmit payload comparisons and link primitive states such as `XMT_LIHA`, `XMT_LIFA`, `XMT_LIPA`, `XMT_LISA`, `XMT_LIRP`, `XMT_LILP`, and `XMT_LISM`.
- Around `0x89C30`-`0x8A310`, the chunk shows a dense Fibre Channel receive/transmit state machine that compares and updates status bytes, counters, command values, and context fields.
- Around `0x8BD50`-`0x8C570`, firmware initializes and moves queue-like records, clears a 0x20-entry loop, formats descriptors, copies list/table records, and programs shared blocks around `0x2A4`, `0x2A8`, `0x2AC`, `0x660`, and `0x664`.
- The last third transitions into firmware metadata/register tables with signatures for `LINK`, `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `RDM2`, `TDMA`, `LMAU`, `PCIR`, and `DEND`.
- After the table area, code resumes around `0x8E6E0`-`0x8E8D7` with bootstrap/control sequences, supervisor/software interrupt style opcodes, coprocessor/control-register style opcodes, delay loops, and stack/register setup.

## State And Data

- Frequently touched low offsets include `0x00`, `0x04`, `0x07`, `0x08`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, `0x0F`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x27`, `0x28`, `0x2C`, `0x30`, `0x34`, `0x3C`, `0x4C`, `0x70`, `0x78`, `0x80`, `0x98`, `0xA1`, `0xA7`, `0xA9`, and `0xB0`.
- Larger firmware-private fields visible include `0x100`-`0x164`, `0x17C`, `0x184`, `0x260`, `0x264`, `0x290`, `0x294`, `0x2A4`, `0x2A8`, `0x2AC`, `0x2F0`, `0x300`, `0x304`, `0x370`, `0x380`, `0x3C0`, `0x630`, `0x660`, `0x664`, and `0x764`.
- Extracted printable strings include `Issue LipF8s`, `Issue LipF7 Reset to AL_PA=%x`, `LIPF8s > 2 secs`, `LIPF8 from myself`, `LIPF7 not from myself`, `Xmit 30ms of LIPF7s`, `loopi 2 LPRQ_INIT. State = %08x`, `LPTOV Timeout`, `RCV_MyLIPF8 : DID=%08x`, and `Sending %s->xcb %x`.
- The register/table section near `0x8E1C0`-`0x8E6C0` contains named blocks and counts/offsets rather than normal executable C.

## Dependencies

- Build dependency: byte order, row order, row width, commas, and 8-byte alignment must remain exact so `emlxs_lpe11002_image[]` matches the expected firmware binary.
- Host dependency: the enclosing header is consumed by `emlxs_fw.h`/firmware table machinery and adapter selection logic outside this range.
- Runtime dependency: the bytecode assumes the LPe11002/Zephyr adapter CPU, memory map, Fibre Channel loop/link primitive state machine, register layout, SLI2/SLI3 behavior, and firmware ABI.
- Analysis dependency: there are no symbols in this range; behavior is inferred from offsets, ARM instruction shapes, literal addresses, and embedded ASCII fragments.

## Risks

- Opaque binary risk: memory safety, concurrency, register sequencing, Fibre Channel protocol correctness, and timeout behavior cannot be audited at normal C source level from this chunk alone.
- Integrity risk: any byte edit, endian conversion, row deletion, inserted comma, or changed diagnostic/table byte can corrupt branch targets, firmware tables, image size expectations, device initialization, loop bring-up, or adapter recovery behavior.
- Boundary risk: this chunk begins mid-routine and ends mid-bootstrap/control sequence, so branch reachability and table ownership require adjacent chunks and the full image.
- Hardware risk: visible link primitive, queue, descriptor, register-table, and coprocessor/control operations may affect adapter reset, LIP/LILP/LIRP/LISM handling, receive/transmit state transitions, firmware relocation, queue setup, and SLI/link readiness.
- Provenance/licensing risk: the firmware payload is vendor-supplied binary data embedded as source; file-level Emulex/Oracle licensing and redistribution constraints apply.

## Cross-Chunk References

- Previous chunk: line 69694 ends immediately before this range at the row starting `0x88120`; this chunk begins at `0x88128` in continuing firmware control flow after transmit-queue diagnostic strings.
- Next chunk: line 73013 continues after the row starting `0x8E8D0`; the visible bootstrap/control-register setup at the end continues into that following range.
- Earlier chunk reports establish the file-level host surface: label/version macros and `emlxs_lpe11002_image[]` are defined outside this chunk, while the body here is only payload bytes.
- Later or adjacent chunks are needed to determine whether the `LINK`/`BIUC`/`CRAM`/`FRXQ`/`ARMR`/`FIFO`/`RDMA`/`RDM2`/`TDMA`/`LMAU`/`PCIR` table block is consumed by nearby firmware diagnostics, initialization code, or a broader firmware self-description mechanism.
- Final per-file conclusions should merge all chunks before asserting firmware layout, branch reachability, integrity properties, or exact mapping from diagnostic strings to adapter-visible behavior.