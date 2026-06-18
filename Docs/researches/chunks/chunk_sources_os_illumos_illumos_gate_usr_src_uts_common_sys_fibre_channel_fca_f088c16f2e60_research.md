# Chunk Research: `fw_lp11000.h` Lines 46470-49787

## Scope And Identity

- Source file: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h`
- Subset scope: `Docs/research_subset_a.md`, illumos `emlxs` Fibre Channel adapter firmware header.
- Exact line range read: 46470-49787.
- Enclosing artifact: `static uint8_t emlxs_lp11000_image[]`, compiled only when `EMLXS_FW_IMAGE_DEF` is defined.
- Firmware identity from file context: `LP11000-S: v2.82a4 (bd282a4.all)`.
- Firmware byte span covered: rows `0x5AB60` through `0x61308`, ending at byte `0x6130F`; 26,544 image bytes.

This chunk is embedded LP11000 adapter firmware, not normal illumos host driver source. The bytes are position-sensitive ARM firmware code, literal data, strings, tables, and trailing zero-fill inside one larger image.

## APIs And Host Surface

No C functions, structs, typedefs, enums, callbacks, ioctls, or illumos kernel APIs are declared in this range. The only host-visible effect is extending the initializer for `emlxs_lp11000_image[]`.

The host-side firmware contract is defined outside this chunk by `emlxs_lp11000_label`, `emlxs_lp11000_kern`, `emlxs_lp11000_stub`, SLI version constants, `emlxs_lp11000_image[]`, and `emlxs_lp11000_size`. `emlxs_fw.h` includes this header and registers these values in the LP11000 firmware table entry. The illumos driver treats this range as opaque bytes to load into the adapter, not as callable C.

## Firmware Control Flow

The range begins immediately after the prior chunk's link-up and position-map logic at row `0x5AB58`. It starts with a literal/address word at `0x5AB60`, then ARM prologue-like code at `0x5AB64`, so the chunk starts at a boundary between firmware literal data and helper code.

Visible control-flow themes:

- Receive-frame and interrupt checks around `0x5ABB0`-`0x5AD30`, with embedded diagnostics `Rcvd Frame called` and `no interrupt`.
- Transmit-idle timeout handling around `0x5AE00`-`0x5AE78`, anchored by `Timeout TX Never IDLE`.
- Sync and FTXQ failure paths around `0x5B0E0`-`0x5B330`, with `Never Sync`, `Never Acquired Sync`, `Sending EOFa`, `FTXQ int never set`, and `SAISR_FTXQ never set`.
- Loop initialization and LIP handling around `0x5B760`-`0x5B990`, with `Issue LipF8s`, `Issue LipF7 Reset to AL_PA=%x`, `LIPF8s > 2 secs`, `LIPF8 from myself`, `LIPF7 not from myself`, `Xmit 30ms of LIPF7s`, and `LPTOV Timeout`.
- Link-initialization primitive names around `0x5BF8C`-`0x5C05C`: `XMT_LIHA`, `XMT_LIFA`, `XMT_LIPA`, `XMT_LISA`, `XMT_LIRP`, `XMT_LILP`, `XMT_LISM`, and `=IGNORED`.
- A low-level table/configuration region begins around `0x5F5F0`, with hardware/register group tags: `LINK`, `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `RDM2`, `TDMA`, `LMAU`, `PCIR`, and `DEND`.

Branches, BL-style calls, literal pools, and PC-relative strings target code outside the chunk, so exact routine boundaries are inferential.

## State And Data

Host-side state is immutable firmware data only. Firmware-side state is adapter-private and appears as fixed offsets from base registers and literal addresses.

Visible state categories include link synchronization, FC-AL loop phase, LIPF7/LIPF8 flags, AL_PA reset handling, LPRQ initialization, LPTOV timeout state, receive-frame status, interrupt status, transmit queue/FTXQ fields, exchange/control-block references, and hardware register-group metadata.

The last dense nonzero region is `0x5AB60-0x60087`, followed by sparse nonzero islands through `0x60127`. From `0x60128` through `0x6130F`, the image is zero-filled padding or reserved image space.

## Dependencies

- Build dependency: meaningful only inside `fw_lp11000.h` and only compiled as a real object when `EMLXS_FW_IMAGE_DEF` is defined.
- Cross-file dependency: `emlxs_fw.h` consumes `emlxs_lp11000_image`, `emlxs_lp11000_size`, label, kernel/stub addresses, and SLI revision constants.
- Runtime dependency: LP11000 hardware, ARM firmware environment, SLI firmware ABI, firmware SRAM/control-block layout, adapter registers, FC-AL loop initialization semantics, receive/transmit queues, interrupts, and timeout behavior.

## Risks

- This is executable firmware encoded as C initializer bytes; one byte edit can corrupt adapter behavior while still compiling.
- Static C review cannot prove reachability, memory safety, or register semantics.
- Visible failure strings point to risks in link bring-up and recovery: never syncing, missing FTXQ interrupt state, TX never idle, LPTOV timeout, unexpected LIPF7/LIPF8 source, and ignored loop primitives.
- The register-table region is alignment and endian sensitive; repeated records and zero-filled regions must not be treated as redundant formatting.

## Cross-Chunk References

- Previous LP11000 chunk, lines 43152-46469, ends at row `0x5AB58` after FC-AL arbitration, ALPA/position-map, `No Position Map`, and `LINK IS UP!` logic.
- Next LP11000 chunk, lines 49788-53105, starts at row `0x61310`, continuing the zero-filled region before later code/data resumes around `0x62148` and `0x62990`.
- The final per-file report should merge this as an opaque middle slice of `emlxs_lp11000_image[]`, preserving firmware table linkage, `EMLXS_FW_IMAGE_DEF` behavior, LP11000 firmware identity, and total image-size contract.