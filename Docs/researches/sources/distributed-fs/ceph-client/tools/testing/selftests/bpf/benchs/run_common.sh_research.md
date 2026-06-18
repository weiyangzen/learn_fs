# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_common.sh

Purpose: shared shell library for benchmark runner scripts, defining a default `RUN_BENCH` command and parsers/formatters for common summary outputs.

Important APIs and functions: `RUN_BENCH="sudo ./bench -w3 -d10 -a"`; `header()` and `subtitle()` format sections; `hits()`, `drops()`, `percentage()`, `ops()`, `local_storage()`, and `total()` parse summary text with sed; `summarize*()` functions print aligned rows.

Control flow: no execution beyond definitions. Scripts source it and call functions with captured benchmark output.

State and persistence: sets shell variable `RUN_BENCH`; no file state.

Dependencies and integration points: assumes GNU-ish `sed`, `seq`, printf support for formatting, `sudo`, and stable bench report strings including units and `±`.

Risks: regex parsing is brittle and silently returns unparsed input if formats change; non-ASCII `±` can be locale-sensitive; default sudo command may not fit unprivileged CI.

Test signals: any script using these helpers should show compact parsed rows; malformed rows are a signal that benchmark output changed.
