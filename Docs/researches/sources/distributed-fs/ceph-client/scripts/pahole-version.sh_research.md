<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/pahole-version.sh -->
# sources/distributed-fs/ceph-client/scripts/pahole-version.sh

## Purpose

`pahole-version.sh` prints the numeric version of a `pahole` executable for BTF capability checks, using the kernel's compact three-digit style such as `119` for v1.19.

## Important APIs, Types, and Functions

It accepts the pahole command and any wrapper arguments as `"$@"`, checks that the resolved command is executable, and parses `--version` output with sed.

## Control Flow

If the command is not executable it prints `0` and exits with status 1. Otherwise it runs `"$@" --version` and converts a leading `v<major>.<minor>` pattern to `<major><minor>`.

## State and Persistence Behavior

It is read-only and writes only stdout/stderr.

## Dependencies and Integration Points

It depends on shell and `pahole` from dwarves. It integrates with Kbuild BTF generation gates.

## Risks and Edge Cases

Different pahole version formats can break parsing. The compact format can be ambiguous for multi-digit components, so callers must compare it the same way Kbuild expects. Incorrect version detection can enable unsupported BTF features.

## Test Signals

Run against several dwarves versions, missing executables, and wrapper output. Verify Kbuild BTF feature gates for versions below and above required thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/pahole-version.sh -->
