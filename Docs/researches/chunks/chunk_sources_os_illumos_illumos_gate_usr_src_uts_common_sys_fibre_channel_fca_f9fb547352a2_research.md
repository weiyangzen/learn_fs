# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 29879-33196

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.
- File role: generated Emulex LPe11000 Fibre Channel adapter firmware image header, not normal host-side illumos driver logic.
- Enclosing artifact: `static uint8_t emlxs_lpe11000_image[]`, emitted only when `EMLXS_FW_IMAGE_DEF` is defined.
- Firmware identity from file context: `LPe11000-S: v2.82a4 (zd282a4.all)`.
- Chunk coverage: ordered chunk 10, source lines 29879-33196, image byte rows `0x3A4E8` through `0x40C90`; the covered bytes end at `0x40C97`.
- Size represented in this chunk: 3,318 initializer rows, 26,544 image bytes.

## APIs And Host Surface

- This range declares no C functions, structs, typedefs, enums, ioctls, callbacks, locks, or illumos kernel APIs.
- The only host-visible content in the range is a contiguous slice of `emlxs_lpe11000_image[]`.
- `emlxs_fw.h` includes `fw_lpe11000.h` under `EMLXS_FW_TABLE_DEF` and maps this image into the `LPe11000_FW` descriptor with image size, label, and SLI/kern/stub constants.
- Host C code treats this chunk as opaque firmware payload. Any apparent routines, strings, or tables in the byte stream are adapter-side artifacts, not host-callable APIs.

## Firmware Control Flow

- The chunk begins mid-stream at `0x3A4E8`, continuing ARM-like instruction bytes from the previous chunk.
- Around `0x3A640-0x3A8B8`, embedded diagnostics indicate link/sync or transmit-queue state: `Never Sync`, `Never Acquired Sync`, `Sending EOFa`, `FTXQ int never set`, and `SAISR_FTXQ never set`.
- Around `0x3AC48-0x3B7C8`, the payload contains loop initialization and link primitive handling paths, including LIPF8/LIPF7 issuance, reset-to-AL_PA, LPTOV timeout, receive/transmit buffers, WWN fields, payload words, and `LPRQ_INIT`.
- Around `0x3B4C0-0x3B7C8`, strings identify primitive handlers such as `XMT_LIHA`, `XMT_LIFA`, `XMT_LIPA`, `XMT_LISA`, `XMT_LIRP`, `XMT_LILP`, `XMT_LISM`, `RCV_`, and `RCV_MyLIPF8 : DID=%08x`.
- Around `0x3E1F8-0x3E668`, descriptor-like data names hardware blocks: `PLINK`, `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `RDM2`, `TDMA`, `LMAU`, and `DEND`.
- The end of the chunk transitions into mostly zero-filled reserved/table space and starts a sentinel-like `0x12345678` word at `0x40C90`.

## State, Dependencies, And Risks

- Host-side state is immutable firmware image data; this chunk does not mutate driver structs or perform synchronization.
- Firmware-side state is opaque adapter memory. Visible themes include Fibre Channel loop/link initialization, LIP primitive handling, AL_PA reset behavior, timeout/reinit behavior, transmit/receive event labeling, and hardware queue/register descriptors.
- Dependencies include `uint8_t`, `_FW_LPE11000_H`, `EMLXS_FW_IMAGE_DEF`, the aligned array declaration, `emlxs_fw.h`, the LPe11000 adapter CPU/firmware memory map, FC loop protocol, mailbox/IOCB/DMA layouts, and exact byte-for-byte image integrity.
- Byte accuracy is the main invariant. Editing any initializer can corrupt instructions, branch displacements, literal pools, strings, lookup tables, reserved regions, or hardware register descriptors.
- Source-level C tests can only verify compilation and symbol availability; meaningful validation requires firmware image integrity and hardware/driver runtime testing.

## Cross-Chunk References

- Previous chunk 9 ends at byte row `0x3A4E0`; this chunk begins mid-routine at `0x3A4E8`.
- Next chunk 11 begins at `0x40C98` and continues the sentinel/table-like area started here.
- Branches, calls, literal-pool references, and pointer-like constants in this range target firmware addresses outside the requested lines.
- The per-file merge should keep this as an opaque slice of `emlxs_lpe11000_image[]`, tied to file-level metadata and the `emlxs_fw.h` firmware-table contract.