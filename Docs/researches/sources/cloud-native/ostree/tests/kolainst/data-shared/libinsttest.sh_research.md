<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libinsttest.sh -->
## sources/cloud-native/ostree/tests/kolainst/data-shared/libinsttest.sh

Purpose: common installed-test shell harness for privileged kola tests.

Important APIs/functions: sources `${KOLA_EXT_DATA}/libtest-core.sh`; defines `_tmpdir_cleanup()`, `prepare_tmpdir()`, `run_tmp_webserver()`, `require_writable_sysroot()`, `nth_boot()`, `rpmostree_query_json()`, `assert_jq()`, and `assert_status_jq()`. It computes `host_commit` and `host_osname` from `rpm-ostree status --json`.

Control flow/state: validates `rpm-ostree` exists and the test is root; creates tempdirs under `/var/tmp` by default; can start a podman-backed Python HTTP server as a systemd unit; may remount `/sysroot` read-write.

Dependencies/integration: requires kola `KOLA_EXT_DATA`, rpm-ostree, jq, systemd, podman for webserver tests, and libtest-core assertions.

Risks/test signals: root and host mutation are assumed. The webserver uses a fixed container name and port 8000, so cleanup/collision failures are possible.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/data-shared/libinsttest.sh -->
