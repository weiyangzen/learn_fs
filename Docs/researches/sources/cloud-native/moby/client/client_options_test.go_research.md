<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_options_test.go -->
# sources/cloud-native/moby/client/client_options_test.go

Purpose: validates the functional options used by `New`. It is the main regression suite for environment variables, API version override precedence, custom clients, user agents, headers, timeouts, and response hooks.

Important coverage: tests exercise `WithHostFromEnv`, `WithTimeout`, `WithAPIVersion`, `WithAPIVersionFromEnv`, deprecated version aliases, option override priority, `WithUserAgent`, `WithHTTPHeaders`, `WithHTTPClient`, and `WithResponseHook`.

Control flow and dependencies: tests set environment variables with Go test helpers, create clients with combinations of options, and inspect resulting client fields or outgoing mock requests. They depend on `gotest.tools` assertions, `net/http`, and package mock transports.

State and integration behavior: environment mutation is test-scoped. No persistent state. The tests protect integration with Docker CLI style env vars and request header generation in the request layer.

Risks and test signals: this file catches subtle compatibility regressions: empty API versions should allow negotiation, env API version wins over manual version per current implementation, duplicate canonical HTTP headers fail, custom HTTP clients are cloned, and nil response hooks are rejected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_options_test.go -->
