# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/res_sample.c

## Purpose

`res_sample.c` presents a menu of representative samples for a histogram entry and opens contextual `perf script` output around the selected sample. It supports normal, disassembly, and source-code context modes.

## Important APIs, Types, and Functions

`res_sample_init` reads the `samples.context` config value into the static `context_len`, defaulting to 10 ms. `res_sample_browse` builds display labels from `struct res_sample` timestamps, CPU, and TID, then constructs a `perf script` command with `--time`, optional `--cpu`, optional `--tid`, event-specific formatting from `attr_to_script`, optional `--inline`, lost/switch/task events, `--ns`, and a `less` search positioned at the sample timestamp.

## Control Flow and State

The function allocates menu strings, uses `ui__popup_menu`, frees the menu, and returns if the choice is invalid. For a valid sample it computes a time range around `r->time` using `context_len`, formats the exact sample timestamp, builds the command with `asprintf`, and delegates terminal handling to `run_script`. Persistent state is only the process-global configured `context_len`.

## Dependencies and Integration Points

It depends on browser script helpers, `perf_exe`, event attributes, time formatting, `symbol_conf`, and global `input_name`. It is invoked by the TUI histogram context menu for entries with representative samples.

## Risks and Test Signals

Command-string construction must preserve quoting assumptions and tolerate missing CPU/TID/input name. Time underflow around early samples and large configured context windows are edge cases. Tests should cover all `enum rstype` modes, inline on/off, CPU/TID filters, and entries with zero, one, or many representative samples.
