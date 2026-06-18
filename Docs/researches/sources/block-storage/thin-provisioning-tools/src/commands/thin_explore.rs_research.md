# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_explore.rs

Development TUI for exploring thin metadata btrees interactively.

Main features:
- Uses `termion` for raw terminal/input and `ratatui` for rendering.
- Displays superblock fields, metadata/data space-map summaries, mapping/details roots, and data block size.
- Provides panels for superblock, device details tree, top-level mapping tree, and bottom-level thin-device mapping tree.
- Supports navigation with `j`/down, `k`/up, `l`/right, `h`/left, and quit with `q`.
- Can start from a decoded `--node-path` emitted by thin check errors.

Internal design:
- `Events` owns an input thread and channel.
- `Adjacent` trait compresses adjacent runs for display.
- Generic `NodeWidget` renders btree headers and entries.
- `Panel` trait abstracts rendering/input/path traversal for each metadata view.
- `perform_action` reads child btree nodes from the sync engine and pushes/pops panels.

CLI:
- Optional `--node-path/-p`.
- Required input device/file.
- Adds version args only.

Notable detail: this is read-only and opens `SyncIoEngine::new(path, false)`.
