# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_debug.h

## Purpose

`bnx2fc_debug.h` declares the driver logging bitmask, lightweight ELS/MISC debug macros, and printf-checked prototypes for context-aware debug helpers.

## Important APIs, Types, and Definitions

Log bits are `LOG_IO`, `LOG_TGT`, `LOG_HBA`, `LOG_ELS`, `LOG_MISC`, and `LOG_ALL`. `bnx2fc_debug_level` is external. `BNX2FC_ELS_DBG()` and `BNX2FC_MISC_DBG()` call `pr_info()` only when enabled. `BNX2FC_IO_DBG()`, `BNX2FC_TGT_DBG()`, and `BNX2FC_HBA_DBG()` are declared with `__printf` attributes.

## Control Flow

The macros are conditional logging gates. Function calls route richer context-aware logging to `bnx2fc_debug.c`.

## State and Persistence Behavior

No state is owned here. `bnx2fc_debug_level` persists as module/global runtime configuration.

## Dependencies and Integration Points

The header relies on kernel printk and compiler format-check support included via `bnx2fc.h`. It is used across all bnx2fc implementation files.

## Risks and Edge Cases

ELS and MISC macros use raw `pr_info()` without host context, so multi-adapter correlation is weaker. Format checking applies to function helpers; macro call sites rely on normal printk checking.

## Test Signals

Build with warning checks, toggle each log bit including `LOG_ALL`, and exercise multi-HBA logs to confirm context-bearing helpers are used where needed.
