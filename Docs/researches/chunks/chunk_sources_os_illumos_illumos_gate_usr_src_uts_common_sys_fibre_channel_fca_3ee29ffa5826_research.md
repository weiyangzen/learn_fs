# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 33197-36514

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`; this chunk is within that exact subset.
- File role: generated/embedded Emulex LPe11002 firmware header for the illumos `emlxs` Fibre Channel driver, not host-executed C implementation.
- This range is entirely inside `static uint8_t emlxs_lpe11002_image[]`, visible only when `EMLXS_FW_IMAGE_DEF` is used by the including translation unit.
- Firmware identity from file context and neighboring chunk reports: `LPe11002-S: v2.82a4 (zf282a4.all)`, total image size `0x8F3A8`.
- Chunk coverage: source lines 33197-36514, firmware byte offsets `0x40C98` through the row beginning at `0x47440`, ending at byte `0x47447`.
- Byte span represented: `0x67B0` bytes, 26,544 bytes total.

## APIs And Host Surface

- No C functions, typedefs, structs, macros, or illumos kernel APIs are declared in this range.
- The only C-visible surface is the enclosing firmware byte array `emlxs_lpe11002_image[]`.
- Host driver integration is indirect: surrounding file metadata and `emlxs_fw.h` register this image as the LPe11002 firmware entry with pointer, size, label, and SLI version constants.
- The bytes are opaque to host C. The illumos driver downloads them to the adapter; it does not call any firmware-internal routines as C symbols.

## Firmware Control Flow Visible

- The bytes decode consistently as big-endian ARM-style firmware code/data: register-save prologues, `bx lr`-style returns, branch-with-link calls, load/store-multiple copies, PC-relative literal loads, and table-driven branches.
- The chunk begins mid-control-flow at `0x40C98`. Early code around `0x40CC8`-`0x40DC8` copies or updates fields near offsets `0x18`, `0x1c`, `0x30`, and `0x4c`, clears a control bit at offset `0x0c`, and branches to common helpers.
- Around `0x40DD8`-`0x40F60`, a routine classifies status bytes and command values, with visible comparisons against values including `0x01`, `0x02`, `0x09`, `0x0b`, `0x15`, `0x17`, `0x18`, `0x1a`, `0x1c`, `0x2a`, `0x80`, `0x82`, `0x83`, and `0x8b`.
- Around `0x40F68`-`0x41080`, a small switch/branch-table path compares table entries, validates fields at offsets such as `0x1c`, `0x24`, and `0x3c`, and calls a helper with length-like constant `0x60`.
- Around `0x41080`-`0x411C8`, code walks indexed structures, checks bytes at offsets `0x07`, `0x50`, and `0x5a`, populates entries at offsets `0x00`, `0x04`, `0x08`, `0x09`, `0x10`, and `0x14`, and updates min/max-like words.
- Around `0x411C8`-`0x412A8`, a reset/scan routine clears several global or per-context records, counts linked lists through fields such as `0x270`, `0x260`, and `0x2f0`, and stores resulting counts through helper calls.
- Around `0x412B0`-`0x413F8`, initialization logic writes global state near `0x658`/`0x660`, emits several low-level register/configuration helper calls, loops over a table rooted by literal address `0x00081904`, and stores a result from `0x0008159c`.
- Around `0x41410`-`0x41890`, a large initialization routine programs many constants through repeated helper calls, zeroes bytes near `0x360`-`0x363`, updates control words, initializes repeated queue/region descriptors, and loops over ranges with limits around `0x170`, `0x6a`, and `0xf83`.
- The middle of the chunk transitions from executable code into firmware data: long zero-filled regions, sentinel values, address tables, and metadata-like records dominate roughly `0x43AF0` onward.
- Near `0x47120`-`0x47380`, executable code resumes with copy loops, cache/control coprocessor-style instructions (`0xEE...` encodings), bootstrap/relocation-like setup, dispatch through several helper calls, and reads/writes of status around offset `0x78`.
- The final rows at `0x47390`-`0x47440` are table data: firmware addresses such as `0x0006403c`, `0x0007a484`, `0x00063fe4`, `0x000751fc`, `0x0007731c`, and descriptor records beginning with byte tags such as `0x55`, `0x58`, `0x56`, `0x50`, `0x6b`, `0x51`, `0x6a`, `0x4d`, `0x65`, `0x67`, `0x45`, and `0x42`.

## State And Data

- Frequently touched structure offsets include `0x00`, `0x04`, `0x07`, `0x08`, `0x09`, `0x0c`, `0x10`, `0x14`, `0x18`, `0x1c`, `0x20`, `0x24`, `0x28`, `0x2c`, `0x30`, `0x34`, `0x38`, `0x40`, `0x44`, `0x48`, `0x4c`, `0x50`, `0x56`, `0x57`, `0x58`, `0x5a`, `0x72`, `0x78`, `0x79`, `0xa0`, `0x260`, `0x264`, `0x270`, `0x2f0`, `0x2f4`, `0x360`-`0x364`, `0x374`, and `0x710`.
- Literal pointer/address data visible in this chunk includes `0x00067eac`, `0x00069094`, `0x00068fc4`, `0x00082e64`, `0x00082e6c`, `0x00082e74`, `0x00083158`, `0x00083170`, `0x00083180`, `0x00083190`, `0x000810d8`, `0x00081904`, and `0x0008159c`.
- Data sections include repeated zero blocks, `0xffffffff` sentinels, small numeric tables, test-pattern words `0x12345678`, and repeated pointer/flag records around `0x43F28`-`0x43FA8`.
- An embedded firmware metadata record appears around `0x441D8`-`0x44238`, including words `0x8eb82123`, `0xaaaa26d5`, version-like `0x07e12894`, and printable string `Z2F2D.82A4`.
- Extracted printable byte sequences in this chunk include short firmware labels/table fragments such as `BLINK`, `BIUCB`, `CRAMB`, `FRXQB`, `ARMRB`, `FIFOB`, `BRDMA`, `RDM2B`, `BTDMA`, `BLMAU`, `DENDB`, and `Z2F2D.82A4`. These are inside the opaque firmware image, not C identifiers exported to illumos.

## Dependencies

- Build dependency: byte order, row order, row width, and 8-byte alignment must remain exact so `emlxs_lpe11002_image[]` matches the expected firmware binary.
- Host dependency: the enclosing header is consumed by `emlxs_fw.h`/firmware table machinery and adapter selection logic outside this range.
- Runtime dependency: the bytecode assumes the LPe11002/Zephyr adapter CPU, memory map, hardware registers, SLI2/SLI3 behavior, and firmware ABI.
- Analysis dependency: there are no symbols in this range; behavior is inferred from offsets, ARM instruction shapes, literal addresses, and embedded ASCII fragments.

## Risks

- Opaque binary risk: memory safety, concurrency, register sequencing, and Fibre Channel protocol correctness cannot be audited at normal C source level from this chunk alone.
- Integrity risk: any byte edit, endian conversion, row deletion, inserted comma, or changed diagnostic/table byte can corrupt branch targets, firmware tables, image size expectations, or device initialization.
- Boundary risk: this chunk begins mid-routine and ends in table data, so branch reachability and table ownership require adjacent chunks and the full image.
- Hardware risk: visible initialization and control/cache style instructions may affect adapter reset, firmware relocation, queue setup, and SLI/link readiness.
- Provenance/licensing risk: the firmware payload is vendor-supplied binary data embedded as source; file-level Emulex/Oracle licensing and redistribution constraints apply.

## Cross-Chunk References

- Previous chunk: line 33196 ends immediately before this range at the row starting `0x40C90`; this chunk begins at `0x40C98` inside continuing firmware control flow.
- Next chunk: line 36515 continues at `0x47448`, likely in the same descriptor/table region that starts in the final rows here.
- Earlier completed chunk reports establish the file-level host surface: label/version macros and `emlxs_lpe11002_image[]` are defined outside this chunk, while the body here is only payload bytes.
- Later completed chunks show the same image continues far beyond this chunk and eventually covers Fibre Channel exchange/session diagnostics, so file-level conclusions must merge all 23 chunks before asserting firmware layout, branch reachability, or integrity properties.