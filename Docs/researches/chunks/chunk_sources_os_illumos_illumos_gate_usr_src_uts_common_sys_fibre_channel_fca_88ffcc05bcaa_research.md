# Chunk Research: fw_lp11000.h lines 63060-66377

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h`
Scope: `Docs/research_subset_a.md`
Chunk: 20, lines 63060-66377, firmware byte offsets `0x7B1D0` through `0x81978`.

## Summary

This chunk is an embedded LP11000 Emulex firmware image fragment, not host-executed C logic. The C API surface remains the surrounding header's `emlxs_lp11000_image[]` byte array and metadata macros; this line range contributes only bytes, ARM instructions, literal pools, and inline diagnostic strings consumed by the adapter firmware after the illumos `emlxs` driver downloads the image.

The visible firmware code covers Fibre Channel link/login initialization and loop/fabric state handling. Inline strings identify major paths: `REG_LOGIN`, `UNREG_LOGIN`, `INIT`, `INIT_LINK`, `ENDEC PCFG:`, `Our SID: %08x`, `DWNL %08x`, `RCVD_LIP_F8`, `tx_close_timeout`, `LPB and LPE Rcvd=>ignored`, `Unknown port_state=%x`, `Loop Phase=%x`, `Monitor State:Loop_Phase=%x`, `ARBF0 in ill phase=%x`, `To OPEN_INIT Due To: lipf7_rcvd`, `IAM_MASTER`, `XMT_ARBF0`, `LIFA`, `LIPA`, `LIHA`, `LISA`, `LIRP`, `LILP`, `XMT_CLS`, and bitmap/ALPA dump text near the end.

## APIs And Entry Points

No C functions, structs, or callable illumos APIs are declared in this chunk. The host-visible contract is inherited from the file-level firmware wrapper: when `EMLXS_FW_IMAGE_DEF` is defined, these bytes are part of `static uint8_t emlxs_lp11000_image[]`; otherwise the image macro resolves to `0`.

Firmware-internal entry points are visible only as ARM branch targets and literal addresses. The chunk starts mid-routine at `0x7B1D0` and ends mid-routine/data sequence at `0x81978`, so local function boundaries are inferred from ARM prologue/epilogue patterns such as `E9 2D ...` / `E8 BD ...` rather than symbol names.

## Control Flow

- `0x7B1D0-0x7B550`: continuation of a preceding routine, then a new routine beginning at `0x7B230`. It repeatedly tests mode/status bits at structure offsets like `0x04`, `0x08`, `0x24`, `0x28`, `0x2C`, `0x30`, `0x34`, and `0x3C`, sets hardware/firmware flags through byte writes around `0xA7`, and fans out through several internal branches.
- `0x7B550-0x7C140`: initialization and table-building path. It reads global fields around `0x0D80-0x0D98`, writes markers at `0x113D/0x113E`, initializes multiple fixed offsets, copies table entries, sets bits in `0xA7`, and uses global addresses in the `0x000967xx` and `0x0008Dxxx` ranges.
- `0x7C140-0x7D348`: request validation and login payload manipulation. Diagnostic literals `REG_LOGIN` and `UNREG_LOGIN` appear here, alongside checks for command-like fields, range validation, compact state mapping, and updates to offsets `0x0C`, `0x18`, `0x1C`, `0x50-0x60`, and `0xA3/0xA6/0xA7/0xA8`.
- `0x7D348-0x7E370`: broader initialization path. Strings `INIT`, `INIT_LINK`, `ENDEC PCFG:`, and `Our SID: %08x` correspond to setup code that builds configuration blocks, copies global-table words, writes adapter identity/SID-style fields, and toggles control bits around `0xA6`, `0xA8`, `0xB0-B2`, `0x290`, `0x374`, and `0x37C`.
- `0x7E370-0x7F5A8`: link parameter synthesis and download/transition path. The `DWNL %08x` literal appears in a block that clears/sets control bits, loops over encoded fields, invokes helper routines, mirrors fields between per-port structures and global slots, and handles state byte `0x39`.
- `0x7F5A8-0x801E8`: command decoder/state update path. It compares encoded command values, updates small state bytes (`0x24`, `0x25`, `0x85`, `0x90`, `0xAA`, `0xB0`, `0xB1`, `0xD9`), manipulates shared control words, and returns firmware status constants.
- `0x801E8-0x807A8`: helper routines for queue/window accounting. These routines compare counters, update offsets `0x10`, `0x14`, `0x18`, `0x1C`, collect hardware/global counters into a local record, and track bitmask status in byte `0xB8` plus counters at `0x80/0x84`.
- `0x807A8-0x81978`: loop initialization/state machine. This region clears/sets link bits, copies context records, emits diagnostics, and dispatches on loop phase. Named strings identify received LIP handling, timeout handling, ignored LPB/LPE, unknown port state, monitor loop phase, ARBF0, LIFA/LIPA/LIHA/LISA/LIRP/LILP, transmit close, and master ALPA/position-map dumps.

## State

- A global/adapter context pointer is loaded repeatedly through offset `0x660`; routines dereference it before reading offsets such as `0x04`, `0x08`, `0x20`, `0x28`, `0x2C`, `0x30`, `0x34`, `0x38`, `0x40`, `0x44`, `0x48`, `0x50`, `0x54`, `0x58`, and `0x5C`.
- Byte flags around `0xA3`, `0xA6`, `0xA7`, `0xA8`, `0xAA`, `0xAC`, `0xAD`, `0xB0`, `0xB1`, `0xB2`, `0xB3`, `0xB8`, `0xD3`, `0xD5`, `0xD9`, and `0xDB` appear to represent firmware control/status latches and link-state markers.
- Word offsets around `0x128`, `0x134`, `0x13C`, `0x144`, `0x170`, `0x180`, `0x184`, `0x290`, `0x298`, `0x29C`, `0x300`, `0x304`, `0x374`, and `0x37C` are used as counters, table bases, or hardware-derived values.
- Fixed global/literal addresses include `0x000964C0`, `0x00096580-0x00096944`, `0x00096AA0`, `0x00096BAC`, `0x000977B0`, and several `0x0008Dxxx/0x0008DFxx` slots.

## Dependencies And Risks

Depends on the binary layout and execution environment of the LP11000 adapter firmware. The illumos driver treats these bytes opaquely. The chunk also depends on ARM instruction encoding, firmware-defined memory maps, external branch targets in adjacent chunks, and the file-level `EMLXS_FW_IMAGE_DEF` / `emlxs_lp11000_size` wrapper.

Any byte-level edit can corrupt firmware control flow, literal pools, alignment, expected checksums, or device state-machine behavior. Inline ASCII strings are interleaved with executable bytes and literal pools, so text-oriented rewriting is unsafe. Bugs here would likely surface as adapter initialization failure, link bring-up failure, fabric/loop login failure, or firmware hang.

## Cross-Chunk References

- Previous chunk dependency: this chunk begins at `0x7B1D0` in the middle of an active routine.
- Next chunk dependency: this chunk ends at `0x81978` after ALPA/position-map diagnostic literals, before the surrounding routine completes.
- Earlier file context defines the image label and firmware entry/version macros: `emlxs_lp11000_label`, `emlxs_lp11000_kern`, `emlxs_lp11000_stub`, `emlxs_lp11000_sli1`, `emlxs_lp11000_sli2`, `emlxs_lp11000_sli3`, and `emlxs_lp11000_sli4`.
- Later file context closes `emlxs_lp11000_image[]` and defines `emlxs_lp11000_size`; this chunk must remain byte-for-byte position-stable relative to those definitions.