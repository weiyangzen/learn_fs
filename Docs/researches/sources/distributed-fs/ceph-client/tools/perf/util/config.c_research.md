# sources/distributed-fs/ceph-client/tools/perf/util/config.c

Purpose: provides Git-style perf config parsing, default config dispatch, typed conversion helpers, an in-memory config-set cache, and build-id/stat global defaults.

Important APIs/functions: `perf_default_config`, `perf_config`, `perf_config_scan`, `perf_config_get`, typed parsers, `perf_etc_perfconfig`, `perf_home_perfconfig`, `perf_config_system`, `perf_config_global`, config-set lifecycle/collection APIs, `perf_stat__set_big_num`, and `set_buildid_dir`.

Control flow: parser reads char-by-char, skips UTF-8 BOM, handles sections and `[base "extension"]`, parses values with comments, quotes, escapes, and continuations, then calls a callback with `section.key`. Loading collects system/user config unless disabled or overridden. `perf_config` lazily initializes global `config_set` and applies callbacks. Default dispatch handles core, hist, UI, call-graph, buildid, stat, and addr2line prefixes.

State and persistence: global `stat_config`, `buildid_dir`, parser globals, and cached `config_set`. Config items record whether they came from system config. `set_buildid_dir` exports `PERF_BUILDID_DIR`.

Dependencies and integration: depends on callchain, hist, stat, evsel BPF settings, srcline/addr2line, build-id, subcmd paths, environment variables, Linux list/string/zalloc helpers, and file/stat parsing.

Risks: parser buffers cap names and values. Boolean parsing treats missing value as true. Numeric parsing has suffixes but limited overflow handling. `perf_config_get` returns config-owned pointers. Iteration callbacks must handle early exit via `goto`.

Test signals: system/user/exclusive configs, env disables, BOM, quoted sections, comments, escapes, bad lines, typed suffixes, default side effects, duplicate replacement, and leak checks.
