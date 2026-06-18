# sources/cloud-native/moby/integration-cli/docker_api_test.go

Purpose: defines the `DockerAPISuite` wrapper used by API integration tests in this directory. It delegates lifecycle hooks to the shared `DockerSuite`.

Important APIs, types, and functions: `type DockerAPISuite struct { ds *DockerSuite }`, `TearDownTest(ctx context.Context, t *testing.T)`, and `OnTimeout(t *testing.T)`.

Control flow: the test harness calls suite hook methods; each method forwards directly to the embedded shared suite pointer. There is no test case logic in this file.

State and persistence behavior: no direct state or persistence. The only state is the pointer to `DockerSuite`; cleanup and timeout diagnostic behavior are owned by that shared suite.

Dependencies and integration points: imports `context` and `testing`, and integrates API tests with the broader integration CLI suite lifecycle. Files such as `docker_api_logs_test.go`, `docker_api_network_test.go`, and `docker_api_stats_test.go` attach methods to this suite.

Risks and edge cases: the wrapper assumes `ds` is initialized by the test registration path. A nil `ds` would panic during teardown or timeout handling, but normal suite setup should prevent that.

Test signals: enables consistent teardown and timeout handling for all `DockerAPISuite` tests; it has no standalone assertions.
