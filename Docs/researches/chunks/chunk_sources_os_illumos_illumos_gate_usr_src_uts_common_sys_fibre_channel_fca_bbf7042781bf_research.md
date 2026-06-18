# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 33197-36514

## Scope

This chunk covers bytes in `emlxs_lpe11000_image[]` from firmware image offset `0x40C98` through `0x47440`. The surrounding header identifies this as the Emulex LPe11000-S firmware image `v2.82a4 (zd282a4.all)`, exported only when `EMLXS_FW_IMAGE_DEF` is set.

The chunk is data, not C control flow. It contains firmware metadata, ARM instruction streams, literal/address tables, diagnostic format strings, dispatch/jump tables, and code that manipulates firmware-private state offsets.

## APIs And State

- Host-visible API remains the outer header symbols defined before the image: `emlxs_lpe11000_label`, firmware entry/address constants, and the byte array `emlxs_lpe11000_image[]`.
- The chunk itself exposes no C functions, structs, or macros; its ABI is the exact byte layout consumed by the Emulex driver/adapter firmware loader.
- Early bytes continue a table/data region from the previous chunk, with sentinel values such as `0x12345678` at `0x40C98` and `0x40CA8`, small numeric tables, repeated zero padding, and address-like words around `0x41038-0x41060`.
- Firmware identity/build metadata appears around `0x41298-0x412F8`, including the ASCII string `Z2D2.82A4`, matching the outer `v2.82a4` label.
- The machine-code regions repeatedly access fixed offsets such as `0x60-0x7a`, `0x90-0xb2`, `0x140-0x178`, `0x260-0x378`, and `0x2c0-0x350` from base registers. These are firmware-private control blocks, queues, counters, flags, and descriptor/list heads rather than C-visible state.
- Literal pools and lookup tables include address vectors near `0x413F0-0x41410`, `0x41570-0x415B8`, command/property descriptor tables around `0x415B8-0x41790`, and branch-dispatch tables around `0x44400-0x44670` and `0x44970-0x44A40`.
- Diagnostic strings appear at `0x417A8-0x417F0`, including timestamp/hex formatting and a receive-error message (`TIME: %08x %s`, `%08x:`, `%08x %08x`, `Rcverr Frm %x. Idx %x.`).

## Control Flow

- Offsets `0x41300-0x41558` contain ARM setup/copy/cache-management style routines: PC-relative literal loads, store/load multiple sequences, loops over 0x20-byte chunks, and coprocessor/cache/TLB-style instructions (`EE...`) before returning.
- `0x417F0` begins branch-heavy firmware logic after the diagnostic string block. It updates status/counter fields around offsets `0x68`, `0x71`, `0x144`, `0x1fc`, and checks flags at `0x140`.
- `0x41938-0x419E8` implements a small memory move/fill-like helper using aligned word transfers and trailing byte writes.
- `0x41A00-0x42120` contains wrappers and control-path helpers that branch to far routines outside this chunk, update status bytes such as `0x61-0x6e`, and maintain fields around `0x2a4`, `0x2e0`, `0x2f8`, `0x340`, `0x348`, `0x350`, and `0x378`.
- `0x421A0-0x428A0` handles descriptor/list style operations: it copies blocks, advances ring/list pointers, compares producer/consumer-like values, updates queue counters, and branches based on message/status codes.
- `0x428A8-0x436E0` continues queue/control state updates, including cache/register maintenance operations, byte counters at `0x61-0x76`, and command classification using embedded constants such as `0x24`, `0x30`, `0x40`, and several high-valued status codes.
- `0x44400-0x44670` is a dense dispatch area with many unconditional ARM branches. It maps decoded command/status cases to local and far handlers, so later chunks likely contain many referenced routines.
- `0x446A0-0x47440` contains command/message processing routines. They decode status bytes, set completion/error codes, copy descriptor words, update flags at offsets like `0x07`, `0x08`, `0x24`, `0x3c`, `0x40`, and `0x44`, and call far handlers for transport, queue, or event processing.

## Dependencies

- Depends on the illumos `emlxs` Fibre Channel adapter driver including this header and defining `EMLXS_FW_IMAGE_DEF` in exactly one compilation unit when the firmware image is needed.
- Depends on the adapter/firmware loader preserving this byte stream exactly; image offsets, endianness, alignment, and literal-pool placement are semantically significant.
- Depends on ARM firmware execution semantics. The chunk uses ARM opcodes, PC-relative addressing, branch/link instructions, coprocessor/cache-maintenance instructions, and fixed firmware control-block offsets.
- Depends on firmware routines and tables outside this chunk. Many `EA`/`EB` branch targets point before and after the chunk, so this region is not independently understandable or replaceable.
- Diagnostic strings imply an internal firmware logging/trace facility that formats timestamps, hex words, receive errors, frame IDs, and indices.

## Risks

- Any byte edit changes firmware behavior; even comments or C formatting should not alter array byte order, count, or alignment.
- Static source review cannot validate firmware correctness, provenance, or safety because logic is compiled binary embedded as C data.
- The chunk has many fixed offsets into firmware-private structures. If the host driver assumes a matching firmware version, mixing this blob with incompatible constants or loader expectations can cause adapter misbehavior.
- Literal pools and branch tables are interleaved with code. Treating the region as ordinary data or disassembling from the wrong offset can produce misleading control-flow conclusions.
- Repeated far branches create strong cross-chunk coupling; auditing only this chunk misses target routine semantics, error handling, and hardware register side effects.

## Cross-Chunk References

- Previous chunk supplies the beginning of the data/table region that continues into `0x40C98`; line 33197 starts mid-table rather than at a logical symbol boundary.
- Later chunk continues directly after `0x47440`; the boundary cuts through command/message handling logic, with the next instruction at `0x47448` continuing the same routine.
- Far branch/call targets visible in this chunk reference firmware code outside the range, including large positive and negative displacements around the `0x41Axx`, `0x42xxx`, `0x44xxx`, `0x46xxx`, and `0x47xxx` regions.
- The chunk's version string and build metadata should be correlated with the outer header label and earlier image header constants (`emlxs_lpe11000_*`) when merging the final per-file report.