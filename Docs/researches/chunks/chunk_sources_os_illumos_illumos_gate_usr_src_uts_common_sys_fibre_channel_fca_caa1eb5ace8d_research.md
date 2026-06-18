# Chunk Research: `fw_lpe11002.h` Lines 16607-19924

This chunk is a contiguous slice of the `emlxs_lpe11002_image[]` firmware byte array for the Emulex LPe11002 Fibre Channel adapter. It covers source lines 16607-19924, corresponding to firmware image offsets `0x20628` through `0x26DD0`, roughly 26 KiB of byte initializers. The data is guarded by `EMLXS_FW_IMAGE_DEF` in the enclosing header; when the firmware image is not compiled in, the same header later defines the image pointer and size as `0`.

There are no C functions, structs, public methods, or in-driver control-flow constructs in this range. The host-visible API for this chunk is the surrounding firmware contract: `emlxs_lpe11002_label`, load-address/version macros, the aligned `static uint8_t emlxs_lpe11002_image[]`, and `emlxs_lpe11002_size`. `emlxs_fw.h` includes this header and places those symbols in the `EMLXS_FW_TABLE` entry for `LPe11002_FW`.

The bytes are ARM-style firmware instructions and literals. The chunk contains many function-like prologue/epilogue patterns, branch/link sequences, load/store operations, and register/control operations. Visible instruction patterns include about 59 stack-save/prologue-like lines, 67 return/restore-like lines, 95 branch-with-link lines, 88 branch lines, 454 load/store-heavy lines, and 25 coprocessor/cache-control style lines. These counts are source-pattern aids only; exact routine boundaries require disassembly with the adapter firmware base address and relocation context.

Key visible behavior:

- The chunk starts in the middle of a routine continued from the prior chunk.
- Multiple short routines branch on small numeric states such as `0`, `1`, `2`, `3`, `5`, `8`, `9`, `0xa`, `0xc`, `0xd`, `0x11`, `0x20`, `0x80`, `0x81`, and `0x82`.
- The firmware repeatedly reads and writes fields that look like adapter or firmware-object state, including offsets near `+0x20`, `+0x28`, `+0x3c`, `+0x66`, `+0x67`, `+0x100`-`+0x164`, `+0x194`-`+0x1a8`, and `+0x260`-`+0x2d8`.
- Several loops copy or compare fixed-size blocks, including repeated 5-word transfers and a 32-byte byte-copy loop.
- There are list/queue-like operations using fields around `+0x20` through `+0x3c`.
- The range includes status/control bit manipulation and apparent hardware-control operations; `EE 07 ...` patterns near the end look like ARM coprocessor/cache/TLB maintenance or hardware-control instructions.
- The final visible lines at `0x26D28`-`0x26DD0` are another helper routine that conditionally calls out-of-range helpers. The chunk ends mid-routine.

State and dependencies:

- Host state is not directly changed by C in this chunk.
- Runtime state is adapter-side firmware state addressed by these ARM instructions.
- The byte array must remain byte-exact and aligned.
- No filesystem or VFS APIs are involved; this is illumos Fibre Channel adapter firmware data.

Risks:

- Any byte edit can corrupt firmware instructions, branches, literals, register writes, or layout assumptions.
- Source-level C tooling cannot validate this adapter-side behavior.
- Polling/looping and hardware-control patterns could hang initialization, queue processing, link recovery, or interrupt/control paths if corrupted.
- Numerous out-of-range branches mean this chunk cannot be reasoned about as isolated logic.
- Version coupling is strict with `LPe11002-S: v2.82a4 (zf282a4.all)` and the `emlxs_lpe11002_*` macros.

Cross-chunk references:

- Previous chunk: begins mid-routine at offset `0x20628`.
- Next chunk: continues from offset `0x26DD8`.
- Earlier/later chunks: many `B` and `BL` encodings target helpers outside this range.
- File-level merge note: this chunk report was written to `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_fibre_channel_fca_caa1eb5ace8d_research.md`; no final per-file report was created.