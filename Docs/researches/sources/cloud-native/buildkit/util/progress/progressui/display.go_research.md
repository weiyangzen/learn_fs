<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display.go -->
# sources/cloud-native/buildkit/util/progress/progressui/display.go

Purpose: implements BuildKit solve progress rendering across quiet, plain text, TTY, and raw JSON modes. It owns the in-memory `trace` model that turns `client.SolveStatus` streams into terminal jobs, status rows, warning rows, terminal log panes, and final error log dumps.

Important APIs and types: `Display`, `DisplayMode`, `DisplayOpt`, `WithPhase`, `WithDesc`, and `NewDisplay` are the public construction surface. Internally `display` abstracts `init`, `update`, `refresh`, and `done`; concrete implementations are `discardDisplay`, `consoleDisplay`, `plainDisplay`, and `rawJSONDisplay`. The `trace`, `vertex`, `vertexGroup`, `interval`, `status`, `displayInfo`, `job`, and `ttyDisplay` types hold the accumulated solve state.

Control flow: `Display.UpdateFrom` initializes the chosen display, then selects on context cancellation, a refresh ticker, and solve status messages. TTY and plain displays rate-limit expensive rendering through `golang.org/x/time/rate`; raw JSON encodes every status immediately. `trace.update` ingests vertices, grouped vertices, statuses, warnings, and logs; it detects vertex transitions, merges progress-group state, updates virtual terminals, and records changed digests. `displayInfo` converts trace state into printable jobs, and `ttyDisplay.print` redraws the console using ANSI cursor movement.

State and persistence: all state is process-local. The trace caches vertices by digest, group state by progress group ID, merged time intervals, warning offsets, text log buffers, vt100 terminal buffers, and cached job projections. Environment variables affect behavior: `TTY_DISPLAY_RATE`, `PROGRESS_NO_TRUNC`, and terminal sizing state shared through package globals in `init.go`.

Dependencies and integration: integrates with BuildKit client solve status types, containerd console detection, vt100 terminal emulation, ANSI coloring, OCI digest keys, and BuildKit progress writers. It is the display sink used by `progresswriter.NewPrinter`.

Risks: terminal redraw correctness depends on terminal width/height and shared package globals (`termHeight`) mutated during rendering. Plain output suppresses frequent status changes, which is intentional but can hide very small progress deltas. Grouped vertices alias subvertex digests to the group vertex, so code that assumes one digest maps to one concrete vertex would be wrong. Log buffers are bounded only for text error printing; TTY trace keeps original logs for error dump.

Test signals: `display_test.go` covers `mergeIntervals`, including nil starts, adjacent intervals, overlaps, and open intervals. The rest of the rendering path is mostly untested here and relies on integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display.go -->
