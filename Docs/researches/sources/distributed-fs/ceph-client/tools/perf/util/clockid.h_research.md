# sources/distributed-fs/ceph-client/tools/perf/util/clockid.h

Purpose: exposes clock id parsing and display helpers for perf record options.

Important APIs/types: declares `parse_clockid` and `clockid_name`.

Control flow: parser is intended for subcmd option callbacks; lookup converts stored ids back to known names.

State and persistence: no state.

Dependencies and integration: includes `<time.h>` and forward-declares `struct option`; used by record command option tables.

Risks: `opt->value` must point to `struct record_opts`.

Test signals: parse-options tests for named, numeric, and unset clock ids.
