# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config2csv.sh

Purpose: generates a CSV matrix of Kconfig options and boot parameters across rcutorture scenario files.

Important APIs and functions: reads `CFLIST` by default, expands literal `CFLIST` in arguments, strips comments/blank lines, includes `.boot` file tokens, and dynamically builds an awk script that sorts scenarios and config keys.

Control flow: validate output path, determine scenario list, create temp directory, emit awk assignments for scenario inclusion and option values, run awk to produce CSV, and copy it to requested output.

State and persistence: writes only the requested CSV; temp directory is removed by trap.

Dependencies and integration: designed to run in a config scenario directory. Requires awk with `asorti`, grep, sed, tr.

Risks and test signals: simplistic parsing treats non-`key=value` lines as `key=?`. It is for comparison/reporting, not config validation.
