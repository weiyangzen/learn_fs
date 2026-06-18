# sources/cloud-native/moby/integration/container/stop_test.go

Purpose: Stop API tests for restart-policy containers, timeout semantics, and raw HTTP status codes.

Important APIs and flow: `TestStopContainerWithRestartPolicyAlways` starts containers that continually restart, waits for running/restarting, then stops them and expects stopped state. `TestStopContainerWithTimeout` runs a command that sleeps then exits 42 and checks zero/short timeout force-kill exit code versus long/negative timeout graceful exit. `TestContainerAPIPostContainerStop` sends raw `POST /containers/<id>/stop` for running, already stopped, and missing containers, checking HTTP 204, 304, and 404 plus optional state.

State and dependencies: Uses restart policies, stop timeouts, inspect state, and raw API responses. Windows timeout behavior is skipped or has longer poll constants.

Risks and signals: It guards stop semantics for restart policy suppression, negative timeout as unlimited wait, and documented HTTP status behavior. Failures impact CLI stop and API compatibility.
