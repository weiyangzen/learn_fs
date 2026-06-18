# File Research: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools.rs

Primary production multiplexer binary for thin-provisioning-tools. It registers the normal public commands for cache, era, and thin metadata operations, then dispatches by command name.

Key behavior:
- Builds a `Vec<Box<dyn Command>>` containing `cache_check`, `cache_dump`, `cache_metadata_size`, `cache_repair`, `cache_restore`, `cache_writeback`, era check/dump/invalidate/repair/restore, and many thin commands.
- Strips the leading executable basename when invoked as `pdata_tools`, allowing `pdata_tools <command> <args>`.
- Also compares the next argument basename to each command name, so symlink-style invocation can work through path basenames.
- Prints a compact command list and returns `exitcode::USAGE` when no command or an unknown command is provided.

Dependencies are limited to `std::ffi::OsStr`, `std::path::Path`, `std::process::exit`, and `thinp::commands::*`.
