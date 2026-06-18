# sources/distributed-fs/ceph-client/scripts/show_delta

Purpose: `show_delta` reformats printk/dmesg lines with `[seconds]` timestamps to include deltas either from the previous timestamp or from a specified base timestamp/message.

Important APIs, types, and functions: `usage()` prints help. `get_time(line)` parses bracketed timestamps and returns `(float_time, rest)`. `convert_line(line, base_time)` preserves unparseable lines and emits `[%5.6f < %5.6f >]` for parseable lines. `main()` handles `-b` and `-h`, reads the whole file, resolves a numeric or string base, and prints converted lines.

Control flow: without `-b`, the global `last_time` tracks previous line time. With `-b`, all deltas are relative to the chosen base. A string base is matched against the beginning of the message rest.

State and persistence: no persistence; state is in memory and output is stdout.

Dependencies and integration points: intended as a developer utility for CONFIG_PRINTK_TIME or `time` kernel command-line logs. It uses Python 3 but contains Python 2-era `string.split`, `string.atof`, and `string.find` calls, which are not available in modern Python 3.

Risks: as written for Python 3, the `string` module calls will fail unless compatibility shims exist, so this script likely needs modernization to `str.split`, `float`, and `str.find`. It reads the whole file at once.

Test signals: run on sample dmesg output with and without `-b`, include unparseable lines, and verify Python 3 compatibility. A failing smoke test today would point to the legacy `string` API usage.
