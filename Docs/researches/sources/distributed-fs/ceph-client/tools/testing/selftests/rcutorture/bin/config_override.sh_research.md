# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config_override.sh

Purpose: merges a base Kconfig fragment with an override fragment so override assignments replace conflicting base assignments.

Important APIs and functions: validates both files, generates a pipeline of `grep -v` filters from override variable names, applies it to base, then appends override.

Control flow: create temp directory, convert override lines into shell pipeline text, run it against base, and concatenate override at the end.

State and persistence: writes merged config to stdout only.

Dependencies and integration: used by `kvm-test-1-run.sh` to layer CFcommon, scenario, and command-line Kconfig settings.

Risks and test signals: matching is line-prefix based on text before `=`, so malformed override lines can create bad grep patterns. Later settings always win by construction.
