# File Research: sources/block-storage/thin-provisioning-tools/src/utils/prof.rs

## Purpose
Provides simple Linux `/proc`-based memory usage reporting for debug logs.

## Main Components
- `get_memory_usage()` reads `/proc/self/statm`, extracts the resident page count, and returns resident memory in MiB assuming 4096-byte pages.
- `print_mem(report, msg)` logs `"<msg>: <meg> meg"` through `Report::debug()`.

## Behavior
`get_memory_usage()` returns IO errors from opening/reading `statm`, but uses `unwrap()` for field extraction and numeric parsing. `print_mem()` unwraps the entire memory read.

## Dependencies and Interactions
The helper is Linux-specific because it hardcodes `/proc/self/statm` and a 4096-byte page size. It depends on the project `Report` abstraction for output.

## Research Notes
This is diagnostic-only utility code. It is not robust to non-Linux platforms, unusual page sizes, or unexpected `statm` contents.
