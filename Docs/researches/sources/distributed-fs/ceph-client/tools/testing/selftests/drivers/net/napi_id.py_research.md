<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id.py

Purpose: Python kselftest that verifies accepted TCP sockets report a nonzero `SO_INCOMING_NAPI_ID` via the companion C helper.

Important functions/APIs: `test_napi_id` chooses a random port, starts `napi_id_helper` in the background, connects to it from the remote endpoint with `socat`, and asserts helper exit status; `main` runs through `NetDrvEpEnv`, `ksft_run`, and `ksft_exit`.

Control flow: the C helper signals readiness, Python sends one byte through the test endpoint pair, waits for the server process, and checks it returned zero.

State/dependencies: relies on the net driver Python selftest library, compiled helper in `cfg.test_dir`, endpoint namespaces/remote host, and `socat`. Risks include helper binary not built, endpoint transport not traversing NAPI, and race if server readiness fails. Test signals are helper return code and ksft equality assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id.py -->
