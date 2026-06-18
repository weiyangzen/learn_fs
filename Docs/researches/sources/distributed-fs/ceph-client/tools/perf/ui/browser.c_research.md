# sources/distributed-fs/ceph-client/tools/perf/ui/browser.c

Purpose: Implements the generic S-Lang text UI browser used by perf TUI views.

Important APIs/types/functions: Public functions in `browser.h` are implemented here: color selection, coordinate helpers, list/rbtree/argv seeking and refresh, title/helpline lifecycle, scrolling, event loop handling, warnings/help/dialogs, resize handling, color config, vertical lines, jump arrows, fused-instruction marks, and `ui_browser__init`.

Control flow: `ui_browser__show` initializes dimensions, title, and helpline under `ui__lock`. `ui_browser__run` repeatedly refreshes, reads keys, handles resize and navigation, updates `index`, `top_idx`, `top`, and `horiz_scroll`, and returns unhandled command keys to callers. Refresh delegates row writing to the browser-specific callback and then draws scrollbar/fill/no-samples UI.

State and persistence: State is held in `struct ui_browser`: current index, top entry, dimensions, title, helpline, current color, filters, and navigation flags. Configured colors are loaded from perf config into static color-set descriptors and S-Lang state.

Dependencies and integration points: Depends on S-Lang wrappers, perf UI locks, helpline stack, key symbols, Linux list/rbtree helpers, and perf config. Specialized browsers set callbacks and call this event loop.

Risks: Seeking callbacks must preserve `top`/`top_idx` invariants or navigation can assert or render wrong entries. List filtering assumes at least one unfiltered entry when entries exist. Terminal resize and lock ordering are important for TUI stability.

Test signals: Exercise list, rb-tree, and argv browsers; simulate navigation keys, resize, empty data, filtering, horizontal scroll, and color config. Run perf TUI annotate/header views under S-Lang.
