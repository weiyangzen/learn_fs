# sources/distributed-fs/ceph-client/scripts/coccicheck

## Purpose
`coccicheck` is the kernel wrapper around Coccinelle `spatch`, supporting whole-tree semantic patch runs and online single-file checking through Kbuild.

## Important APIs, Types, and Functions
Environment variables drive behavior: `SPATCH`, `V`, `SPFLAGS`, `LINUXINCLUDE`, `C`, `KBUILD_EXTMOD`, `MODE`, `J`, `COCCI`, `DEBUG_FILE`, `srcroot`, and `srctree`. `run_cmd_parmap()` uses spatch `--jobs` when supported. `run_cmd_old()` manually launches indexed spatch workers. `coccinelle()` checks per-rule `Options:` and `Requires:` headers, prints submission hints in verbose mode, and runs selected modes.

## Control Flow and State
The script locates `spatch`, computes include arguments, chooses online or offline options, determines concurrency, selects mode defaults, initializes debug output, and then either scans all matching `.cocci` files under `scripts/coccinelle` or runs the specified `COCCI`. It tracks worker PIDs for signal cleanup in old parallel mode. It persists only optional debug logs and generated patch/report output from spatch.

## Dependencies and Integration
It depends on Bash, Coccinelle, `lscpu`, `getconf`, `find`, `grep`, and Kbuild environment. It integrates directly with `make coccicheck` and `CHECK=scripts/coccicheck`.

## Risks and Test Signals
The script relies on shell word expansion for options and may mishandle spaces in paths. Debug file existence causes an immediate bail. Test online `C=1/2`, offline all-rule scan, single `COCCI`, `MODE=chain`, `SPFLAGS` overrides, old/new spatch job support, and signal cleanup.
