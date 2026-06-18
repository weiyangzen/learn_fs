# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_filter.h

## Purpose
Declares the internal `cxgb4` filter-management interface shared between the main adapter driver, filter implementation, ethtool filter support, TC offload modules, and firmware event dispatch. It also defines `WORD_MASK`, a convenience all-ones 32-bit TCB mask used by filter programming code.

## Important APIs, Types, and Functions
The header exposes asynchronous reply handlers `filter_rpl`, `hash_filter_rpl`, and `hash_del_filter_rpl`; direct filter state/resource helpers `clear_filter`, `set_filter_wr`, `delete_filter`, `writable_filter`, `clear_all_filters`, and `init_hash_filter`; exact-match capability probing through `is_filter_exact_match`; and ethtool filter lifecycle hooks `cxgb4_init_ethtool_filters` and `cxgb4_cleanup_ethtool_filters`.

Types are intentionally not defined here. The declarations rely on driver-wide structures from `cxgb4.h` and message structures from `t4_msg.h`, notably `struct adapter`, `struct filter_entry`, `struct ch_filter_specification`, `struct cpl_set_tcb_rpl`, `struct cpl_act_open_rpl`, and `struct cpl_abort_rpl_rss`.

## Control Flow and State
There is no runtime control flow in this header. It defines a narrow contract: callers may ask whether a filter entry is writable, submit or delete fixed-index filters, clear per-entry state, clear all adapter filters during teardown, and route firmware/CPL replies back into the filter state machine. Persistent state is owned by the implementation through adapter TID/filter tables and firmware hardware tables; this file only exposes the operations that mutate or reconcile that state.

## Dependencies and Integration Points
Includes `t4_msg.h` for CPL reply/request type declarations. It is included by `cxgb4_filter.c` for self-consistency and by `cxgb4_main.c` to dispatch firmware event queue replies, configure hash-filter capability during adapter init, install server filters for offload listeners, and clear filters on PCI remove. Other local modules use these declarations for ethtool and TC filter integration.

The ethtool declarations are implemented outside the listed file, so this header is also the compile-time bridge between generic filter handling and ethtool-specific rule bookkeeping.

## Risks and Test Signals
Risk is mostly interface drift: mismatched prototypes or incomplete declarations can break event dispatch or leave cleanup paths unable to release filter resources. Because several declared functions are called during teardown and interrupt/event handling, return semantics and sleepability assumptions must stay aligned with callers.

Test signals include full-driver builds with ethtool/TC offload enabled, `modpost` symbol/prototype checks, firmware event queue paths reaching the correct reply handlers, remove/shutdown cleanup calling `clear_all_filters`, and ethtool filter init/cleanup coverage.
