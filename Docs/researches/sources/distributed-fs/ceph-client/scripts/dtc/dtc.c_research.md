# sources/distributed-fs/ceph-client/scripts/dtc/dtc.c

## Purpose
`dtc.c` is the main entry point for the device tree compiler host tool. It parses CLI options, detects input/output formats, reads a device tree, validates and mutates it, then emits DTS, DTB, ASM, YAML when enabled, or null output.

## Important APIs, Types, and Functions
Global option state includes `quiet`, reserve/pad/min/align sizes, `phandle_format`, symbol/fixup flags, alias generation, and annotation level. Helpers are `is_power_of_2()`, `fill_fullpaths()`, `guess_type_by_name()`, and `guess_input_format()`. `main()` coordinates parser functions, checks, symbol/fixup generation, sorting, and output functions.

## Control Flow and State
CLI parsing uses `util_getopt_long()` and the local option tables. Defaults are inferred from filenames and blob magic. Dependency-file output writes escaped output targets. The selected reader is `dt_from_source()`, `dt_from_fs()`, or `dt_from_blob()`. After fullpath filling, plugin inputs enable fixups by default. The pipeline runs checks, optional aliases/symbols/fixups/local fixups, optional sort, output open, and selected writer.

## Dependencies and Integration
It depends on DTC subsystems for source parsing, flattened tree parsing/writing, filesystem tree reading, checks, source position dependencies, util option helpers, and libfdt.

## Risks and Test Signals
Many options set global state consumed by other modules. `-v` calls `util_version()` without an explicit break, relying on that function to exit. Input guessing can misclassify unreadable files by fallback. Test all input/output formats, dependency files, plugin default fixups, annotation restrictions, align power-of-two rejection, min/pad mutual exclusion, sorting, quiet/force behavior, and stdout output.
