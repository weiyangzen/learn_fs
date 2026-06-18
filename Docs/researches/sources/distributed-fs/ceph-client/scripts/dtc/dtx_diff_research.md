# sources/distributed-fs/ceph-client/scripts/dtc/dtx_diff

## Purpose
`dtx_diff` normalizes DTS, DTB, or `/proc/device-tree` style inputs to sorted DTS and either prints one decompiled tree or diffs two normalized trees.

## Important APIs, Types, and Functions
`usage()` documents modes. `compile_to_dts()` detects directory, binary FDT magic, or DTS source and invokes `dtc` with the right input format. It preprocesses DTS with `cpp` using kernel DT include flags. The main body parses flags for color, full unified diff, source tree, git root, annotation, and sorting.

## Control Flow and State
After parsing args, the script locates a preferred kernel-built `scripts/dtc/dtc`, falling back to `dtc` in `PATH` with detailed build hints. It builds `cpp_flags` and a `DTC` command string. With two inputs it runs `diff` over process substitutions of normalized output; with one input it prints normalized DTS. It persists no files except subprocess temp state.

## Dependencies and Integration
It depends on Bash, `cpp`, `dtc`, `hexdump`, `diff`, `git`, `which`, and kernel source include-prefixes. `dt_to_config` uses it as a normalizer.

## Risks and Test Signals
The script relies on `ARCH` for include paths and can include the wrong local file when diffing trees from different directories. Command strings and paths are not robustly quoted. Test source, blob, and fs inputs; two-way diffs; `-S` and `-s`; `KBUILD_OUTPUT`; color fallback; annotation; unsorted mode; missing dtc; and bad `ARCH`.
