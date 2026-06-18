# File Research: sources/block-storage/lvm2/tools/stub.h

## Purpose
`stub.h` provides stub implementations for removed or unsupported historical LVM commands.

## Commands
It defines handlers for `lvmsadc`, `lvmsar`, `pvdata`, `lvmchange`, and `vgconvert`. Each handler logs an explanatory error and returns `ECMD_FAILED`.

## Key Behavior
The messages point users toward supported replacements: `dmstats` for `lvmsadc`/`lvmsar`, `lvs`/`pvs`/`vgs` or `vgcfgbackup` for `pvdata`, `dmsetup` for driver reset workflows, and an older LVM version for LVM1-to-LVM2 conversion.

## Integration Notes
Despite the `.h` suffix, this file contains function bodies. It is intended to be included where command handlers are generated or registered for compatibility names.
