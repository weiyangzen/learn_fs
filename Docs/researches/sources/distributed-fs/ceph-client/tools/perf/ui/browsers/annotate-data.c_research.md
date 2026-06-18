# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate-data.c

Purpose: Implements a TUI browser for annotated data types, showing per-field memory-access overhead in a foldable type tree.

Important APIs/types/functions: `struct browser_entry` represents one visible or foldable type member. `struct annotated_data_browser` embeds `ui_browser`. Key routines collect entries from `annotated_data_type`, aggregate per-byte histograms with `get_member_overhead`, traverse foldable trees, render overhead/type fields, toggle fold state, and expose `hist_entry__annotate_data_tui`.

Control flow: Collection recursively builds browser entries from `adt->self` and member children, adds synthetic closing-brace entries, folds by default, and counts visible rows. The browser seek/next/prev logic traverses visible folded state rather than the raw list. Runtime key handling supports navigation through the generic browser plus `e` and `E` fold toggles.

State and persistence: Browser state includes entry tree, current entry, visible entry counts, fold flags, and per-event histogram aggregates. It is allocated per invocation and freed before return.

Dependencies and integration points: Integrates with perf hist entries, grouped evsels, `annotated_data_type`, `type_hist`, symbol display options, and the generic `ui_browser`.

Risks: Recursive allocation failure can leak children already built because intermediate error cleanup is limited. `browser__write_overhead` initializes `nr_samples` to zero instead of using histogram samples, which affects sample-count display.

Test signals: Open data annotation on types with nested fields, empty event groups, skipped-empty events, fold/unfold recursively, and sample/period/percent display modes. Use leak checks on allocation-failure injection if possible.
