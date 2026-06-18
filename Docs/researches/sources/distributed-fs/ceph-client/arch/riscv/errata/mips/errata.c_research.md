<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/mips/errata.c

## Purpose
Applies MIPS P8700 pause-opcode erratum alternatives when the required vendor ISA extension is present.

## Important APIs, Types, And Functions
Functions are `errata_probe_pause()`, `mips_errata_probe()`, and `mips_errata_patch_func()`. It checks `CONFIG_ERRATA_MIPS_P8700_PAUSE_OPCODE` and vendor extension `XMIPSEXECTL`.

## Control Flow
The patch function skips early boot, computes required errata bits, iterates `.alternative` entries for `MIPS_VENDOR_ID`, validates patch IDs, and patches old text with alternative text under `text_mutex`.

## State And Persistence
Persistent state is the patched kernel text. Probe state is recomputed per call.

## Dependencies And Integration Points
Integrated with RISC-V alternative entries, text patching, MIPS vendor extension detection, and errata ID lists.

## Risks And Edge Cases
Patch IDs must remain within `ERRATA_MIPS_NUMBER`. Applying patches after boot requires synchronization through `text_mutex`; early stage intentionally does nothing.

## Test Signals
Signals are alternative patch application on affected CPUs, warnings for invalid IDs, and correct pause behavior in CPU idle/spin paths.

Source read size: 67 lines, 1537 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/errata.c -->
