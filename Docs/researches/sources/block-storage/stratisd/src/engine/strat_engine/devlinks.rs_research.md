# File Research: sources/block-storage/stratisd/src/engine/strat_engine/devlinks.rs

This file centralizes simple Stratis `/dev` link conventions.

Key responsibilities:
- Defines `UEVENT_CHANGE_EVENT` as `"change"`.
- Provides `filesystem_mount_path(pool_name, fs_name)` to build `/dev/stratis/<pool>/<filesystem>` paths from `DEV_PATH`.

Important behavior:
- Uses `PathBuf` collection from path components instead of string concatenation.

Tests:
- No local tests in this file.
