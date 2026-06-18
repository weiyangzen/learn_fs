# sources/cloud-native/moby/integration/container/resize_test.go

Purpose: Container TTY resize API tests for successful resize, raw query validation, and invalid container state.

Important APIs and flow: `TestResize` runs a TTY container and calls `ContainerResize` with height/width. It then uses raw `POST /containers/<id>/resize?h=...&w=...` requests to send unset, empty, nonnumeric, negative, and out-of-range values that the typed client would reject earlier, expecting HTTP 400 and specific error messages. The invalid-state case resizes a created but not running container and expects a conflict.

State and dependencies: Uses running or created containers and raw API responses. No persistent external state is used.

Risks and signals: It guards API parsing and error text for resize query parameters as well as runtime state validation. Failures may break CLI/user feedback or allow invalid terminal dimensions into runtime calls.
