# sources/distributed-fs/ceph-client/tools/rcu/extract-stall.sh

Purpose: extracts RCU CPU stall warning snippets from a console or dmesg log, including configurable context before and after each stall line while filtering out clocksource noise.

Important APIs/functions: `usage()` prints guidance and an error. The main body validates that `$1` is a readable file, assigns `preceding_lines` from `$2` defaulting to 3 and `trailing_lines` from `$3` defaulting to 10, and runs an `awk` state machine followed by `tr -d '\015'` and `grep -v clocksource`.

Control flow: the script prints the input path, then `awk` maintains a rolling `last[]` buffer while not in suffix mode. When a line matches `detected stall`, it prints the preceding buffer including the matched line and sets `suffix` to the trailing count. While `suffix > 0`, it prints following lines and emits a blank line at the end of the snippet.

State and persistence: no persistent state. Runtime state is held in awk variables `last[]` and `suffix`.

Dependencies and integration: POSIX shell plus `awk`, `tr`, `grep`, and `basename`. It integrates with RCU debugging workflows by reducing large logs to stall excerpts.

Risks: matching is plain `/detected stall/`, so it can include non-RCU lines with that phrase and miss differently worded warnings. `grep -v clocksource` removes any line containing that string, even if it is useful context. Unquoted `$(basename $0)` in `usage()` is minor shell-style risk.

Test signals: run against logs with no stall, one stall, adjacent stalls, CRLF line endings, custom preceding/trailing counts, and unreadable/missing files.
