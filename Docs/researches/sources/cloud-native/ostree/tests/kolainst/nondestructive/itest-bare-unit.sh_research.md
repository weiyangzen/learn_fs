<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-unit.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-unit.sh

Purpose: intended to run installed basic unit tests and verify permission-denied object reads, but currently aborts immediately with `fatal "FIXME - need to also sync over the installed tests"`.

Important APIs/functions: unreachable code would set `G_TEST_SRCDIR`, prepare `/var/tmp`, run installed `test-basic.sh` and `test-basic-c`, create a bare repo with unreadable content, verify root can read it, and verify `setpriv` non-root cannot.

Control flow/state: because `fatal` is before all substantive work, the active behavior is immediate failure. The rest is a planned/non-live test body.

Dependencies/integration: would require installed tests, `setpriv`, bare repo support, and libinsttest assertions.

Risks/test signals: as written this is a deliberate failing placeholder unless excluded by the kola harness. If enabled, signal is the FIXME fatal rather than the intended permission test.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-unit.sh -->
