# Chunk Research: `fw_lp11002.h` Lines 53106-56423

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h`

Scope note: this chunk is fully inside `static uint8_t emlxs_lp11002_image[]`, the embedded Emulex LP11002-S firmware image for the illumos `emlxs` Fibre Channel driver. It is not host-side C logic; it is precompiled adapter firmware represented as byte initializers.

## Chunk Extent

- Source lines read completely: 53106-56423.
- Firmware image offsets covered: row `0x67AC0` through row `0x6E268`, ending at byte `0x6E26F`.
- Size represented by this chunk: 3,318 initializer rows, 26,544 firmware bytes.
- The file-level firmware metadata outside this chunk identifies the image as `LP11002-S: v2.82a4 (bf282a4.all)`, guarded by `EMLXS_FW_IMAGE_DEF`, aligned with `#pragma align 8`, and consumed through `emlxs_lp11002_image` / `emlxs_lp11002_size`.
- The chunk starts and ends mid-firmware-control-flow. There are no C declaration or preprocessor boundaries in the requested range.

## APIs and Integration Surface

- No C functions, structs, typedefs, enums, or callable illumos kernel APIs are declared in this chunk.
- The only host-visible artifact is positional data inside `emlxs_lp11002_image[]`.
- External host integration is inherited from adjacent file context: `emlxs_fw.h` includes `fw_lp11002.h` and places `LP11002_FW`, `emlxs_lp11002_size`, `emlxs_lp11002_image`, the label, and SLI metadata into the firmware table.
- Adapter binding is outside this chunk; this byte range must be treated as opaque payload loaded to LP11002-compatible hardware.

## Firmware Control Flow Visible

- The bytes decode as dense ARM-style firmware with many function-like regions: visible patterns include 98 stack prologues (`E9 2D ...`), 135 stack epilogues (`E8 BD ...`), many `mov pc, lr` returns, branch-with-link calls (`EB`), conditional branches, and jump-table-like branch runs.
- The opening region continues the prior chunk's routine at `0x67AB0`/`0x67AB8`, testing fields around `+0x2C`, `+0x30`, `+0x3C`, and `+0x3F`, then calling shared helpers and updating status bytes.
- Around `0x67B68`-`0x68D58`, routines manipulate queue/list records, table scans, counters, frame/request descriptors, and status bytes across offsets such as `+0x80`, `+0x260`, `+0x264`, `+0x270`, `+0x2C0`-`+0x2DC`, and `+0x2F0`-`+0x2FC`.
- Around `0x69190`-`0x691C8`, repeated coprocessor/control-register style opcodes (`EE 07 ...`) appear with `+0x20` stride loops, likely firmware cache/TLB/barrier or hardware-control operations.
- Around `0x69718`-`0x69768`, a visible jump table dispatches a compact state/opcode field into many local handlers. Nearby logic uses status bytes `0x80`, `0x82`, and `0x8B`.
- Around `0x6B188`-`0x6BD00`, code initializes exchange/request objects, zeroing and filling many descriptor fields and setting command/status bytes including `0x37`, `0x3A`, `0x3C`, `0x42`, `0x56`, `0x80`, `0x82`, `0x83`, `0x84`, and `0x8B`.
- Around `0x6C9D0`-`0x6D410`, the chunk includes frame/exchange completion paths, duplicate or abort-like filtering by status values such as `0x9D`, `0xAD`, `0xAF`, `0xBB`, and descriptor copy-out routines.
- The tail `0x6DE10`-`0x6E268` includes compact helper routines: range/length clamps, table copy helpers over `+0x80`-based slots, a small jump table at `0x6DF78`, and cleanup that writes status byte `0x84` to `+0x07`. The last row prepares arguments and continues into the next chunk at `0x6E270`.

## State and Dependencies

- Host-side state is immutable firmware payload; no illumos locks, queues, DMA handles, condition variables, or callbacks are created here.
- Firmware-side state is opaque but visibly organized as per-object descriptors with small byte status fields, ring/list pointers, table entries, counters, and hardware/control words.
- Frequently referenced offsets include `+0x00`, `+0x04`, `+0x08`, `+0x0C`, `+0x1C`, `+0x20`, `+0x24`, `+0x26`, `+0x27`, `+0x28`, `+0x2C`, `+0x30`, `+0x3C`, `+0x40`, `+0x44`, `+0x64`, `+0x80`, `+0x84`, `+0x88`, `+0x8C`, and larger table offsets such as `+0x260`, `+0x264`, `+0x270`, `+0x2A4`, `+0x2C0`-`+0x2DC`, `+0x2F0`-`+0x2FC`, `+0x320`, `+0x340`, `+0x350`, `+0x358`, and `+0x3C0`.
- Runtime dependencies are the LP11002 adapter CPU, exact firmware load address/endianness, on-card SRAM/register layout, SLI/Fibre Channel firmware ABI, and helper routines/literal pools in earlier and later chunks.
- Several branch targets are outside this chunk in both directions, so routine boundaries and full error paths cannot be resolved from this slice alone.

## Risks

- Any byte edit can corrupt executable firmware instructions, branch displacements, literal-pool references, jump-table targets, descriptor layouts, or hardware register programming.
- The C compiler only validates the initializer syntax; it cannot validate firmware semantics, control-flow integrity, table sizes, or state-machine correctness.
- The visible logic touches exchange/request descriptors, queue/list fields, login or frame-state bytes, and hardware/cache-control operations. Corruption here could cause link recovery failures, dropped frames, stale or duplicated exchanges, firmware hangs, or adapter initialization failure.
- The chunk is offset-sensitive. Inserting or deleting even one byte would shift all later firmware offsets and invalidate branches/literal references in the rest of `emlxs_lp11002_image[]`.

## Cross-Chunk References

- Previous chunk 16 ends at image offset `0x67AB8`; this chunk starts immediately at `0x67AC0` and continues that routine's state checks and helper calls.
- Next chunk 18 starts at `0x6E270`, directly continuing the tail routine after this chunk has loaded/moved arguments at `0x6E260`-`0x6E268`.
- Calls and branches target helpers in earlier and later parts of the firmware image, including shared diagnostic/completion/hardware routines; the final per-file report should summarize this as one opaque LP11002 firmware payload rather than independent host C modules.