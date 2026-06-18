<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_test.go -->
# sources/cloud-native/moby/client/container_wait_test.go

Purpose: validates asynchronous wait behavior, error classification, proxy interruption handling, and result decoding.

Important coverage: daemon internal errors, transport connection errors, route `POST /containers/container_id/wait`, wait condition query, successful wait response, invalid ids through error channel, proxy plaintext errors after headers, and long proxy errors constrained by `containerWaitErrorMsgLimit`.

Control flow and dependencies: tests consume the returned result/error channels, use custom response bodies, and assert error contents/classes.

State and risks: no persistence. This is high-signal for concurrency and streaming decode behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_test.go -->
