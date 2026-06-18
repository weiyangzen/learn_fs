# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configcheck.sh

Purpose: verifies a built `.config` satisfies a requested config fragment and reports mismatches.

Important APIs and functions: `test_kconfig_enabled()` checks exact `VAR=value` presence; `test_kconfig_disabled()` treats missing variable or `VAR=n` as disabled. It strips quotes from `.config` and strips `#CHECK#` markers from template.

Control flow: stage config/template into temp files, generate shell checks for disabled options and enabled/non-n options, source those generated scripts, and print mismatch diagnostics.

State and persistence: read-only except temp files.

Dependencies and integration: called by `configinit.sh` and `kvm-recheck.sh`.

Risks and test signals: emits diagnostics but does not explicitly aggregate exit status beyond functions; consumers rely mostly on output presence. Quote stripping can hide meaningful quoted value differences.
