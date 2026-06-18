<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/libtest-core.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/libtest-core.sh

Purpose: nondestructive copy of the shell assertion/TAP core library.

Important APIs/functions: same core helpers as `data-shared/libtest-core.sh`: `fatal`, `assert_*`, content/mode/whiteout checks, `skip`, TAP counters, and ERR reporting.

Control flow/state: sets UTF-8 locale and `G_DEBUG=fatal-warnings`, unsets `LANGUAGE`, and traps ERR for diagnostics.

Dependencies/integration: sourced by nondestructive kola shell tests. Depends on standard shell utilities.

Risks/test signals: duplicated library can drift from `data-shared/libtest-core.sh`; assertion behavior should remain consistent across destructive and nondestructive suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/libtest-core.sh -->
