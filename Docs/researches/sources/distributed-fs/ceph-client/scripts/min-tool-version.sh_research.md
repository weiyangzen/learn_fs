<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/min-tool-version.sh -->
# sources/distributed-fs/ceph-client/scripts/min-tool-version.sh

## Purpose

`min-tool-version.sh` prints the minimum supported version for a named kernel build tool. It centralizes version floors consumed by build checks and documentation.

## Important APIs, Types, and Functions

The command accepts exactly one tool name. Supported names are `binutils`, `gcc`, `llvm`, `rustc`, and `bindgen`. The GCC floor is special-cased for `ARCH=parisc64`, and the LLVM floor is special-cased for `SRCARCH=loongarch`.

## Control Flow

After argument-count validation, a `case` statement echoes the tool-specific version or fails with an unknown-tool error.

## State and Persistence Behavior

The script is read-only. Output is the version string on stdout; errors go to stderr with a non-zero exit.

## Dependencies and Integration Points

It depends only on POSIX shell and environment variables set by Kbuild. It integrates with compiler/toolchain version checks and must stay synchronized with `Documentation/process/changes.rst`.

## Risks and Edge Cases

The values are policy, not detection. Drift between this script, docs, and actual compiler feature use can reject valid setups or accept broken ones. Architecture environment variables must be set correctly for special cases.

## Test Signals

Run for every known tool, for `ARCH=parisc64`, for `SRCARCH=loongarch`, and for an unknown tool. Build tests with exactly-minimum and just-below-minimum toolchains validate the floors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/min-tool-version.sh -->
