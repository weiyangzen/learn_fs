<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait.go -->
# sources/cloud-native/moby/client/container_wait.go

Purpose: waits asynchronously for a container to reach a requested condition and reports either a wait response or an error over channels.

Important APIs/types/functions: `ContainerWaitOptions{Condition container.WaitCondition}`, `ContainerWaitResult{Result <-chan container.WaitResponse, Error <-chan error}`, `containerWaitErrorMsgLimit`, and `Client.ContainerWait`.

Control flow: creates result and buffered error channels, validates container id, encodes optional `condition`, posts to `/containers/{id}/wait`, and returns channels after response headers are received. A goroutine decodes the response body. If JSON syntax fails, it captures up to 2 KiB of proxy/plaintext error body through a tee reader and sends that as an error.

State and integration behavior: no local persistence. The method deliberately returns before the wait completes but after server acknowledgment, enabling caller synchronization with starts/restarts. It closes the response in the goroutine or immediately on request error.

Dependencies: JSON decoding, container wait API type, shared `post`, id validation, and proxy error handling.

Risks and test signals: risks include goroutine leaks if channels are not consumed, proxy-truncated JSON handling, and distinguishing connection errors from API-version negotiation errors. `container_wait_test.go` covers daemon/connection errors, condition query, normal wait result, proxy interruption, long errors capped by limit, and JSON decode behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait.go -->
