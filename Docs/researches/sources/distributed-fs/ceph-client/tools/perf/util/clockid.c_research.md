# sources/distributed-fs/ceph-client/tools/perf/util/clockid.c

Purpose: parses perf record clock id options and maps supported clock names to kernel `clockid_t` values while recording clock resolution.

Important APIs/functions: exports `parse_clockid` and `clockid_name`; internal `get_clockid_res` calls `clock_getres`.

Control flow: unset clears `use_clockid`; duplicate settings fail; numeric strings are accepted directly; names may include a `CLOCK_` prefix and are matched against monotonic, monotonic_raw, realtime, boottime, tai, and aliases.

State and persistence: mutates the `record_opts` supplied via parse-options. No global mutable state.

Dependencies and integration: uses subcmd parse-options, `record_opts`, `clock_getres`, `NSEC_PER_SEC`, and perf UI warnings.

Risks: numeric parsing accepts ids that the kernel may later reject. `clock_getres` failure only warns and leaves resolution zero.

Test signals: each alias, prefix variants, numeric ids, unset behavior, duplicate option error, unknown name warning, and old distro clock definitions.
