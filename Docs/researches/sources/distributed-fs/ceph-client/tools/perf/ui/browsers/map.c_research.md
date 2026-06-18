# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.c

## Purpose

`map.c` implements a TUI symbol-map browser for a perf `struct map`. It displays each symbol's start/end address, binding, and name, and optionally supports name/address search when verbose indexing is enabled.

## Important APIs, Types, and Functions

The public API is `map__browse(struct map *map)`. Internal `struct map_browser` embeds `ui_browser`, stores the viewed `map`, and tracks address display width. `map_browser__write` renders rows from DSO symbols, `map_browser__search` resolves input by hex address or symbol name, `map_browser__run` handles keys, and `symbol__browser_index` accesses the extra index slot expected near symbol storage.

## Control Flow and State

`map__browse` walks `dso__symbols(map__dso(map))`, counts entries, finds maximum end address, and in verbose mode stores each symbol's row index. `map_browser__run` shows the map and loops until ESC/left/q/Ctrl-C. Search updates browser top/index when a symbol is found; otherwise it pushes a helpline message. No persistent state is written outside optional per-symbol index memory.

## Dependencies and Integration Points

This depends on perf map/DSO/symbol helpers, SLang browser primitives, keysyms, and helpline handling. It is reached from the histogram context menu's “Browse map details” action.

## Risks and Test Signals

The `symbol__browser_index` pointer arithmetic is explicitly fragile and depends on symbol allocation layout. Search is only useful when indexes were prefilled under verbose mode. Tests should browse maps with local/global/weak symbols, verify address-width formatting, search by `0x...` and name, and ensure empty or missing symbol trees fail gracefully.
