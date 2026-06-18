# sources/cloud-native/nydus/src/bin/nydus-image/inspect.rs

## Purpose
This Rust module implements an interactive/request-mode RAFS bootstrap inspector for `nydus-image`. It can show filesystem metadata, list directories, change directories, stat files and chunks, list blobs and prefetch entries, resolve chunks by blob offset, and check inodes.

## Important APIs, Types, And Functions
`RafsInspector` stores request mode, `RafsSuper`, bootstrap reader, current directory inode, parent inode stack, and a RAFS v6 file-to-parent map. `new` loads a bootstrap with `RafsSuper::load_from_file`. Command methods include `cmd_stats`, `cmd_list_dir`, `cmd_change_dir`, `cmd_stat_file`, `cmd_list_blobs`, `cmd_list_prefetch`, `cmd_show_chunk`, and `cmd_check_inode`. Traversal helpers include `generate_file_parents`, `path_from_ino`, `walk_dir`, and `walk_dir_inner`. `stat_single_file` prints inode attributes; `get_file_name` handles v6 hardlink naming; `get_blob_id_by_index` maps blob indices to IDs. `ExecuteError` models control/error results. `Executor::execute` parses commands and dispatches. `Prompt::run` provides the REPL loop and optional JSON output handling.

## Control Flow
The inspector loads RAFS metadata once, then commands read from that in-memory metadata and the bootstrap reader as needed. Directory navigation updates `cur_dir_ino` and `parent_inodes`. Commands that need full paths or v6 hardlink parents lazily build `file_parents` by walking from root. The prompt loops on stdin, executes commands, prints text output or serializes JSON values in request mode, and exits on `q`/`exit`.

## State And Persistence
Persistent source data is the bootstrap file. Runtime mutable state includes current directory inode, parent stack, cached file parent mapping, and a mutex-protected bootstrap reader used for prefetch table reads. The inspector itself does not modify the bootstrap.

## Dependencies And Integration Points
It depends on `nydus_rafs` metadata traits, `RafsIoReader`, `nydus_storage::BlobChunkInfo`, `nydus_api::ConfigV2`, serde JSON, and Unix permission formatting. It is a CLI-facing module in `nydus-image` and consumes RAFS v5/v6 metadata conventions.

## Risks
`Executor::execute` parses `chunk` offset with `unwrap`, so invalid chunk arguments can panic unlike `icheck`. `cmd_change_dir` prints "`name is `" with an empty reason when a child is absent. Several methods print directly even in paths that return `Option<Value>`, so request-mode JSON coverage is partial. `path_from_ino` and hardlink handling require full-tree walks and can be expensive on large images.

## Test Signals
No unit tests are present in this file. Functional signals are successful command execution against known bootstraps: sane stats, correct directory navigation/listing, blob and prefetch tables, inode resolution including v6 hardlinks, and chunk lookup by compressed offset.
