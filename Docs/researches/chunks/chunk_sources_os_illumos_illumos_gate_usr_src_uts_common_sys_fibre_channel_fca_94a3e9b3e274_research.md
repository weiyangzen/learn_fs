# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 39833-43150

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`; this chunk is within that exact subset.
- File role: generated/embedded Emulex LPe11002 firmware header for the illumos `emlxs` Fibre Channel driver, not host-executed C implementation.
- This range is entirely inside `static uint8_t emlxs_lpe11002_image[]`, visible only in the translation unit that defines `EMLXS_FW_IMAGE_DEF`.
- Firmware identity from file context: `LPe11002-S: v2.82a4 (zf282a4.all)`, with full image size `0x8F3A8`.
- Chunk coverage: source lines 39833-43150, firmware byte offsets `0x4DBF8` through the row beginning at `0x543A0`, ending at byte `0x543A7`.
- Byte span represented: `0x67B0` bytes, 26,544 bytes total.

## APIs And Host Surface

- No C functions, typedefs, structs, macros, or illumos kernel APIs are declared in this range.
- The only C-visible entity is the enclosing firmware byte array `emlxs_lpe11002_image[]`.
- Host integration is indirect: the surrounding header exposes label/version constants, SLI entry constants, image pointer, and size outside this chunk; `emlxs` firmware-selection code consumes those values elsewhere.
- The bytes are opaque to host C. The driver downloads the image to the adapter; it does not call firmware-internal routines as C symbols.

## Firmware Control Flow Visible

- The byte stream continues to decode consistently as big-endian ARM-style adapter firmware, with register-save prologues, returns, branch-with-link calls, unconditional branches, PC-relative literal loads, and embedded literal/string pools.
- The range begins mid-control-flow at `0x4DBF8`, setting a state byte to `0x58`, updating a control word at offset `0x0C`, clearing offset `0x1C`, and branching back to earlier firmware code.
- Several routine entries are visible near `0x4DC38`, `0x4DCE0`, `0x4DD60`, `0x4DE98`, `0x4E3D8`, `0x51500`, `0x53D00`, `0x53EB8`, and `0x54058`, indicating this chunk spans multiple firmware subroutines rather than one isolated table.
- Early code paths manipulate small command/status bytes such as `0x23`, `0x31`, `0x3E`, `0x57`, `0x58`, `0x84`, `0x88`, and `0xB0`, often writing them to object offset `0x07`; these appear to be firmware-internal state or command opcodes.
- Around `0x4DE98`-`0x4E210`, the firmware tests flags at offsets `0x0A`, `0x0B`, `0x24`, `0x26`, `0x27`, `0x30`, `0x38`, `0x44`, and `0x6A`, builds or updates per-exchange records, and loops while a condition byte remains nonzero.
- Around `0x4E218`-`0x4E338`, there is a small indexed-byte transfer path using offset `0x26` as a pending byte/state, copying through an indexed area derived from a `0x200`-class base and then clearing that pending byte.
- Around `0x4E338`-`0x4E3D0`, status bits in offset `0x0C` are masked/updated and dispatch branches select status bytes `0x84` or `0x88` depending on other object fields.
- Around `0x50290` and `0x50330`, embedded diagnostic strings identify routines for `DREG_LOGIN` and `UNREG_LOGIN`, with nearby code calling common helpers and updating counters/table entries.
- Around `0x51000`-`0x510D8`, a compact jump-table-like sequence selects among several branches, updates global counters/limits, and falls into an `INIT %08x` diagnostic string.
- Around `0x512D0`-`0x51460`, diagnostics reference `INIT_LINK`, `ENDEC PCFG:`, and `Our SID: %08x`, tying this chunk to Fibre Channel link initialization and port identity state.
- Around `0x51500`-`0x51630`, a larger initialization routine copies or derives many words into a control/state block, including fields near `0x90`-`0xC8` and values sourced from a shared block around `0x660`.
- Around `0x53D00`-`0x53F58`, code probes several addresses or conditions, accumulates bit flags (`0x01`, `0x02`, `0x04`, `0x08`, `0x10`, `0x20`), increments byte counters near `0x7C` and `0x80`, and writes a summarized byte at offset `0xB8`.
- The final scoped line at `0x543A0` ends mid-routine: it has just tested byte offset `0x26` and begins a conditional path whose return/branch logic continues in the next chunk.

## State And Data

- Frequently touched low offsets include `0x00`, `0x04`, `0x06`, `0x07`, `0x08`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0E`, `0x0F`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x26`, `0x27`, `0x28`, `0x2C`, `0x30`, `0x38`, `0x3C`, `0x40`, `0x44`, `0x4C`, `0x4D`, `0x64`, `0x6A`, `0x6C`, `0x70`, `0x74`, `0x78`, `0x7C`, `0x80`, `0x84`, `0x88`, `0x90`, `0x94`, `0x98`, `0x9C`, `0xA0`, `0xA3`, `0xAA`, `0xB0`, `0xB1`, `0xB8`, `0xBC`, `0xC0`, `0xC4`, `0xC8`, and `0xCC`.
- Larger firmware-private fields visible include offsets around `0x104`, `0x158`, `0x15C`, `0x160`, `0x164`, `0x2F0`, `0x358`, `0x360`, `0x362`, `0x380`, `0x3C0`, `0x400`, `0x660`, and `0x66E`.
- Extracted printable strings in this chunk include `DREG_LOGIN %02x %06x`, `UNREG_LOGIN %02x`, `INIT %08x`, `INIT_LINK %02x`, `ENDEC PCFG:`, `Our SID: %08x`, and `DWNL %08x`.
- Those strings indicate firmware paths for Fibre Channel login deregistration/unregistration, initialization, link initialization, ENDEC/physical configuration, source ID tracking, and download state.
- Literal addresses such as `0x000840E8`, `0x00084180`, `0x00084338`, `0x00084340`, `0x000846F0`, and `0x0006FA00` appear in nearby literal pools and are firmware-private references, not host virtual addresses.

## Dependencies

- Build dependency: byte order, row order, row width, commas, and 8-byte alignment must remain exact so `emlxs_lpe11002_image[]` matches the expected vendor firmware binary.
- Host dependency: the enclosing header is consumed by `emlxs` firmware table and adapter-selection machinery outside this range.
- Runtime dependency: the bytecode assumes the LPe11002/Zephyr adapter CPU, memory map, Fibre Channel login/link state machine, ENDEC/register layout, SLI2/SLI3 behavior, and firmware ABI.
- Analysis dependency: there are no symbols in this range; behavior is inferred from offsets, ARM instruction shapes, branch/literal patterns, and embedded ASCII fragments.

## Risks

- Opaque binary risk: memory safety, concurrency, register sequencing, Fibre Channel protocol correctness, and timeout behavior cannot be audited at normal C source level from this chunk alone.
- Integrity risk: any byte edit, endian conversion, row deletion, inserted comma, or changed diagnostic/literal byte can corrupt branch targets, literal pools, firmware state machines, image size expectations, device initialization, or adapter recovery behavior.
- Boundary risk: this chunk begins and ends mid-firmware control flow; branch reachability and invariants require adjacent chunks and the full image.
- Hardware risk: visible login, unregister, init, link-init, ENDEC, SID, and download-state paths can affect adapter login/logout behavior, link bring-up, and HBA readiness.
- Provenance/licensing risk: the firmware payload is vendor-supplied binary data embedded as source; file-level Emulex licensing applies.

## Cross-Chunk References

- Previous chunk: line 39832 ends immediately before this range at the row starting `0x4DBF0`; this chunk begins at `0x4DBF8` in continuing firmware logic that had already prepared an indexed object pointer.
- Next chunk: line 43151 continues after the row starting `0x543A0`; the visible conditional path involving offset `0x26` continues into that following range.
- Earlier and later chunk reports are needed to recover full branch targets for many `EA`/`EB` instructions that jump outside `0x4DBF8`-`0x543A7`.
- File-level merge should retain the host-facing facts from the wrapper: label/version macros, kernel/stub/SLI constants, conditional `EMLXS_FW_IMAGE_DEF` behavior, array declaration, and total image size.
- Final per-file conclusions should merge all chunks before asserting exact firmware layout, call graph, branch reachability, or mapping from diagnostics to adapter-visible behavior.