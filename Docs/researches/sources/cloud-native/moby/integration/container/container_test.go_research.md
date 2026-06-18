## sources/cloud-native/moby/integration/container/container_test.go

Purpose: validates JSON request-body error handling for Docker API POST endpoints that expect JSON. It ensures unsupported content types, invalid JSON, trailing content, and empty body cases return appropriate client errors rather than server errors.

Control flow iterates endpoints `/commit`, `/containers/create`, `/containers/foobar/exec`, `/containers/foobar/update`, and `/exec/foobar/start`. For each endpoint it runs parallel subtests posting raw strings with `request.Post`, either `ContentType("text/plain")` or `request.JSON`, then reads response bodies and checks status/message content.

State is only HTTP request/response state against the test daemon. Dependencies include `internal/testutil/request`, per-test spans from `setupTest`, and Go HTTP status constants. Risks are exact error-message drift and parallel subtests sharing the same daemon, though requests are independent. Test signals are `400 Bad Request` for invalid content type/JSON/trailing content, body messages with specific diagnostics, and empty-body status below 500.
