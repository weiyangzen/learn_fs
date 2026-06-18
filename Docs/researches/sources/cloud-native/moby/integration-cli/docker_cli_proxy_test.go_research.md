# sources/cloud-native/moby/integration-cli/docker_cli_proxy_test.go

Purpose: verifies Docker CLI proxy environment handling for Unix sockets and TCP daemon endpoints.

Important APIs and functions: `DockerCLIProxySuite`, `DockerDaemonSuite`, `icmd.RunCmd`, `appendBaseEnv`, `net.InterfaceAddrs`, and daemon start with `-H tcp://...:2375`.

Control flow: the Unix socket test runs `docker info` with `HTTP_PROXY` pointing at a dead proxy and expects success, proving local Unix socket connections bypass HTTP proxy settings. The TCP test finds a non-loopback host IP, starts the daemon listening on that TCP address, verifies `docker info` fails through the bad proxy, then succeeds when `NO_PROXY` includes the daemon IP.

State and persistence: starts a daemon TCP listener but does not persist config.

Dependencies and integration points: local Linux daemon, host network interfaces, Go proxy environment semantics, Docker CLI transport selection, and daemon command wrapper.

Risks: host interface selection can pick an unsuitable address; port 2375 conflicts or firewall behavior may affect the test; proxy error text is not asserted, only failure.

Test signals: proxy variables must not affect Unix socket connections, must affect TCP connections, and `NO_PROXY` must exempt the TCP daemon host.
