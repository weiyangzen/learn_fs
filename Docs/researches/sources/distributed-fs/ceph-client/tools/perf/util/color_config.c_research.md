# sources/distributed-fs/ceph-client/tools/perf/util/color_config.c

Purpose: parses boolean-like color config values into an effective color policy.

Important APIs/functions: exports `perf_config_colorbool`.

Control flow: `never` disables, `always` enables, `auto` uses TTY/pager detection, false disables, and true behaves like auto. Auto also rejects `TERM=dumb`.

State and persistence: no internal state; reads environment and pager/TTY state.

Dependencies and integration: depends on perf config boolean parsing, `isatty`, pager state, environment access, and color policy users.

Risks: missing value is parsed as true and therefore auto. `stdout_is_tty` may be passed precomputed or `-1`.

Test signals: `never`, `always`, `auto`, true/false aliases, unset value, `TERM=dumb`, pager active, and redirected stdout.
