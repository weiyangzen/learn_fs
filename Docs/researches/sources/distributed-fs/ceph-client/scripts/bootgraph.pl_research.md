# sources/distributed-fs/ceph-client/scripts/bootgraph.pl

## Purpose
`bootgraph.pl` converts timestamped `dmesg` initcall/debug output into an SVG timeline showing boot-time function durations and async waits.

## APIs, Types, And Functions
It uses Perl `Getopt::Long`, hashes for start/end/type/PID rows, and direct SVG text/rect printing. It supports `--header` to include `uname -a` and current date.

## Control Flow
The script reads stdin, records `calling <func>+` start lines, `initcall <func> returned` end lines, `async_waiting`/`async_continuing` spans, and stops collecting at memory-protection/freeing markers. It then scales the first-to-last time range to a 1950-pixel graph, assigns rows by PID, filters very short durations, and emits SVG rectangles and labels plus a timeline.

## State And Persistence
State is in memory while processing the log. The persistent artifact is SVG written to stdout by caller redirection.

## Dependencies And Integration Points
It depends on boot logs with `CONFIG_PRINTK_TIME` and `initcall_debug`. It integrates with boot performance analysis tooling.

## Risks And Test Signals
Risks include regex drift with log format changes, division by zero on degenerate logs, and SVG label escaping omissions. Test signals are non-empty SVG for valid dmesg input and an explanatory error/help path when no initcall data is found.
