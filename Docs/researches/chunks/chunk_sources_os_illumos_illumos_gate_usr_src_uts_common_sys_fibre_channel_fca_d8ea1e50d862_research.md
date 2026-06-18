# Chunk Research: `fw_lp10000.h` Lines 23244-26561

This chunk is not ordinary C source. It is a contiguous slice of the `emlxs_lp10000_image[]` firmware byte array for the Emulex LP10000 Fibre Channel adapter, covering image offsets `0x2D590` through `0x33D3F` within a total firmware image declared as `0x5BD00` bytes. The surrounding header exposes the host-side contract through `emlxs_lp10000_label`, firmware version/address macros, and the conditional `static uint8_t emlxs_lp10000_image[]` under `EMLXS_FW_IMAGE_DEF`; this chunk itself defines no C functions, types, structs, or callable APIs.

The bytes are ARM-style firmware instructions, literal pools, and embedded diagnostic strings. The visible firmware behavior centers on Fibre Channel loop/link state transitions, link-down and old-port handling, synchronization acquisition/loss, exchange and buffer management, abort/RRQ handling, and LIP/link-close events.

Key visible behaviors:

- The chunk starts mid-routine from the previous chunk. Early code continues bit/field tests and register updates, then enters repeated helper-call patterns around offsets `0x2D610`-`0x2D9F8`.
- Several routines manipulate apparent firmware state fields and memory-mapped registers. Common visible offsets include `+0x04`, `+0x08`, `+0x0C`, `+0x10`, `+0x14`, `+0x18`, `+0x1C`, `+0x24`, `+0x28`, `+0x2C`, `+0x30`, `+0x3C`, `+0x44`, `+0x48`-`+0x53`, `+0x5B`, `+0x70`, `+0x74`, `+0x78`, `+0x79`, `+0x80`, `+0x9C`, `+0xD3`, `+0xD8`, `+0xDB`, `+0xDC`, `+0x184`, `+0x28C`, and `+0x38C`.
- Embedded diagnostics expose link-state and loop-state vocabulary: `LKDN`, `LD EXP`, `LPCS`, `ELLF`, `LDBU`, `IntL EXP`, `Try_OLDP`, `Try_LOOP`, `ACTV`, `RSync`, `Beg: PCFG`, `not MON`, `OLD_PORT`, `ISSUE LPRQ_INIT`, `TO_LOOP*`, `TO_OLDP*`, `OLDPACTV`, `Our SID`, `LOOP ACTIVE!!!`, `LOSS SYNC`, `SYNC`, `WSIG`, `MBEG`, `MSCH`, `MSTR`, `2GIG`, `1GIG`, `FAIL`, `lost`, and `Ill phase`.
- Exchange and buffer paths are also visible through diagnostics: `XMT XRI mismatch`, `BARJT`, `BAACC buf`, `ABTSbuf`, `RJT buf`, `XCB 0: Can't start xchg`, `RI %x deadx`, `bad buffer rls`, `Rls free buf`, `dup get`, `Abt Req`, `Fnd abt x`, `ZXCB`, `ZXCB OK frame`, `Int err`, `Begin RRQ`, `Call new cmd for RRQ`, `Dup Free buf`, `killing xchg due to continue`, `ReQ xcb`, `ReQ dcb`, and `State %02x->%x`.
- Near `0x33A68`-`0x33AD8`, the bytes form a branch-table-like sequence with several forward branch targets. The adjacent string `Ill phase` suggests a phase/state dispatcher with default illegal-phase handling.
- Near the end of the chunk, visible LIP and close-timeout handling appears through `RCVD_LIP_F8`, `lipf8_rcvd`, `tx_close_timeout`, and `LPB and LPE Rcvd=>ignored`. The chunk ends before this later state path completes.

Dependencies:

- Host-side dependencies are the opaque firmware-image interface in this header and its consumers in the `emlxs` driver, especially `emlxs_fw.h`, which registers `LP10000_FW` with `emlxs_lp10000_size`, `emlxs_lp10000_image`, label, and version fields.
- Adapter matching in `emlxs_adapters.h` maps LP10000/LP10000DC/LP10000ExDC and Oracle-branded LP10000 variants to `LP10000_FW`, so this blob is shared across several related 2Gb Fibre Channel HBA models.
- Runtime dependencies are on-card firmware conventions, the LP10000 adapter CPU, SLI1/SLI2 firmware layout, hardware register meanings, and Fibre Channel loop/exchange protocols.
- All branch targets, literal addresses, and state offsets depend on exact byte ordering, alignment, and image placement. The `#pragma align 8(emlxs_lp10000_image)` and final image size are part of that contract.

Risks:

- Any byte-level edit can corrupt instruction encoding, branch displacement, literal pools, debug strings used as format references, or firmware state-machine tables.
- Source-level C tooling cannot validate this chunk's behavior; meaningful validation requires firmware provenance, checksums if present elsewhere, or hardware/driver load testing.
- The visible code includes retry, polling, synchronization, and phase-transition paths. Misbehavior here could surface as link bring-up failures, loop instability, lost sync, LIP storms, stuck exchanges, or failed recovery from link-down events.
- Buffer and exchange paths mention duplicate free, bad buffer release, abort request, RRQ, and exchange kill handling. These are high-risk firmware paths because corruption can lead to command loss, stale exchanges, or adapter lockups.
- The firmware metadata identifies this image as `LP10000-S: v1.92a1 (td192a1.all)` with SLI1/SLI2 version constants. Mixing this byte slice with another firmware revision would be unsafe.

Cross-chunk references:

- The chunk begins in the middle of executable firmware flow; the preceding chunk contains the setup and branch targets feeding the initial code at `0x2D590`.
- Many `B`/`BL`-style instruction patterns jump to helpers outside this range, both backward to earlier firmware code and forward into later chunks.
- The final lines stop at `0x33D38`, mid-path after the `LPB and LPE Rcvd=>ignored` diagnostic; handling for subsequent port-state cases continues in the next chunk.