# sources/distributed-fs/ceph-client/scripts/kconfig/merge_config.sh

## Purpose

`merge_config.sh` merges a base config and one or more config fragments, warns about overrides/redundancy/effective-value mismatches, optionally enforces strict mode, and optionally runs `make` to expand the merged fragment through Kconfig defaults.

## Important APIs, Types, and Functions

The script exposes options `-m`, `-n`, `-r`, `-y`, `-O`, `-s`, `-Q`, and `-h`. Internal shell variables include `RUNMAKE`, `ALLTARGET`, `WARNREDUN`, `BUILTIN`, `OUTPUT`, `STRICT`, `CONFIG_PREFIX`, `WARNOVERRIDE`, `KCONFIG_CONFIG`, `TMP_FILE`, and `PROCESSED_FILES`. AWK blocks implement config-name extraction, override warnings, strict detection, builtin-demotion prevention, redundant warnings, and final effective-config comparison.

## Control Flow

After option parsing and `KCONFIG_CONFIG` setup, the script copies the base file to a temp file. For each fragment, it validates readability, warns on duplicate input, uses AWK to remove overridden base entries while appending the fragment, honors `-y` by preserving `=y` over incoming `=m`, and records strict violations. With `-m`, it writes the merged temp config directly. Otherwise it runs `make KCONFIG_ALLCONFIG=$TMP_FILE ... alldefconfig` or `allnoconfig`, then AWK-compares requested values against the final `.config`.

## State and Persistence Behavior

It creates temporary `.tmp.config.*` files in the current directory and removes them through a trap. It writes the target `$KCONFIG_CONFIG` either directly in merge-only mode or indirectly through `make`. It may use `readlink -m` for `-O` output paths.

## Dependencies and Integration Points

It depends on POSIX shell plus common utilities `mktemp`, `cp`, `mv`, `readlink`, `make`, and `awk` (or `$AWK`). It integrates with Kconfig targets via `KCONFIG_ALLCONFIG`, `KCONFIG_CONFIG`, and optional `O=`.

## Risks and Edge Cases

`STRICT_MODE_VIOLATED` is read before explicit initialization in some shells when no violation occurred; because the script does not use `set -u`, this is tolerated. Fragment iteration uses unquoted `$MERGE_LIST`, so filenames with whitespace are unsupported. AWK matching is line-oriented and intentionally limited to `CONFIG_*` and `# CONFIG_* is not set` forms. `-O` requires an existing directory.

## Test Signals

Test override warnings, strict failures, duplicate fragments, redundant warnings, `-Q`, `-y` demotion prevention, `-m`, `-n`, custom `CONFIG_` prefix, output directory behavior, missing fragment/base file handling, and final mismatch warnings for unmet dependencies.
