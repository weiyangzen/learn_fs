<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libtest-core.sh -->
## sources/cloud-native/ostree/tests/kolainst/data-shared/libtest-core.sh

Purpose: shared assertion and TAP helper library copied into installed/kola tests.

Important APIs/functions: `fatal`, `assert_not_reached`, `tap_ok`, `tap_end`, `assert_streq`, `assert_str_match`, file/dir presence assertions, content assertions, mode and whiteout assertions, `assert_files_equal`, `skip`, and `report_err` trap.

Control flow/state: sets UTF-8 locale, unsets `LANGUAGE`, exports `G_DEBUG=fatal-warnings`, and traps ERR to report the failed command.

Dependencies/integration: used by `libinsttest.sh` and nondestructive copy. Depends on POSIX/GNU tools such as `grep`, `stat`, `cmp`, and `sed`.

Risks/test signals: content checks depend on exact messages and regex dialect. Signals are immediate fatal exits with diagnostic file dumps and TAP counters where used.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libtest-core.sh -->
