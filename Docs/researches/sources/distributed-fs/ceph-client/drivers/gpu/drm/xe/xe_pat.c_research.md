<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.c

## Purpose

`xe_pat.c` owns the Xe driver's page attribute table programming. It defines the platform-specific PAT register encodings for Xe_LP, Xe_HP/G, Xe_HPC, Xe_LPG, Xe2, Xe3, and Xe3p variants, maps driver cache levels to PAT indices, programs graphics and media GT PAT registers, and exposes debug dump helpers for hardware and software PAT state.

## Important APIs, Types, and Functions

The core private type is `struct xe_pat_ops`, which selects graphics/media programming functions, hardware dump behavior, and the modern entry formatter. `xe_pat_init_early()` selects the PAT table, ATS/PTA special entries, entry count, and `xe->pat.idx[]` cache-level map from platform/IP version. `xe_pat_init()` writes the table to a GT unless running as an SR-IOV VF. `xe_pat_dump()` reads hardware registers with forcewake, while `xe_pat_dump_sw_config()` prints the software-selected table. Query helpers `xe_pat_index_get_coh_mode()`, `xe_pat_index_get_comp_en()`, and `xe_pat_index_get_l3_policy()` expose PAT metadata used by page-table and BO code.

## Control Flow and State

Initialization starts before GT bring-up with platform dispatch in `xe_pat_init_early()`. Older platforms use compact four/eight-entry tables and direct or MCR programming paths. Xe2 and newer use 32-entry tables with no-promote, compression, L3 class, L3/L4 policy, and coherency fields; some entries are intentionally reserved and marked invalid. Later `xe_pat_init()` chooses media or graphics programming based on GT type and writes `_PAT_INDEX()`, optional `_PAT_ATS`, and optional `_PAT_PTA` registers. Persistent state lives in `xe->pat`: selected table pointer, operation table, entry count, cache index map, and special ATS/PTA entries.

## Dependencies and Integration Points

This file depends on register definitions, MCR multicast access, forcewake, platform macros, workarounds, SR-IOV mode checks, and the UAPI cache-level concepts in `xe_drm.h`. Page-table encoding relies on the cache-to-PAT index map and query helpers. Debugfs and diagnostics call the dump paths through `drm_printer`.

## Risks and Test Signals

The highest risk is platform table drift: wrong PAT encodings cause subtle coherency, compression, or cacheability bugs. The query helpers only warn on out-of-range indices and still dereference the table. Xe2+ compression combined with coherency is explicitly constrained by CCS clearing behavior. Tests should verify platform selection, entry counts, reserved entry formatting, cache-level index map, SR-IOV VF no-op programming, MCR versus non-MCR media/graphics access, and debug dump behavior when forcewake cannot be acquired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pat.c -->
