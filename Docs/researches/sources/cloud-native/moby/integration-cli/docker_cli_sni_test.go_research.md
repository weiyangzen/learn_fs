## sources/cloud-native/moby/integration-cli/docker_cli_sni_test.go

Purpose: intended regression coverage that the Docker CLI sets TLS SNI when contacting a registry-like HTTPS endpoint. The suite type forwards teardown and timeout to `DockerSuite`. `TestClientSetsTLSServerName` is currently skipped as flaky.

Control flow would start an `httptest.NewTLSServer`, record `r.TLS.ServerName` for incoming requests, derive the expected server name from the server URL, run `docker pull <hostport>/dockercli/image:latest`, and assert every recorded request used the expected SNI value.

State is in the in-memory slice of observed server names and the transient TLS server. Dependencies include Go `httptest`, `net/url`, `exec.Command`, and the external `dockerBinary`. Risks are inherent flakiness, multiple request attempts, TLS handshake errors, and registry pull behavior that may change before reaching the handler. Test signal is disabled, but if enabled it would fail on missing hits or mismatched TLS ServerName.
