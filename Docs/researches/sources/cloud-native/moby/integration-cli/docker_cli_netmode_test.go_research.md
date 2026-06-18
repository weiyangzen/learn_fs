# sources/cloud-native/moby/integration-cli/docker_cli_netmode_test.go

Purpose: validates CLI/daemon rejection or acceptance of `--net` combinations with hostname, links, MAC addresses, DNS, add-host, publish, and expose options.

Important APIs and functions: `DockerCLINetmodeSuite`, constant `stringCheckPS`, helper `dockerCmdWithFail`, `cli.DockerCmd`, and `dockerCmdWithError`.

Control flow: positive tests run `busybox ps` with host, bridge, none, and hostname combinations and check command output. Negative tests call `dockerCmdWithFail`, assert nonzero exit, and inspect conflict messages for container network mode, host network mode, invalid `container:` syntax, unknown networks, links, DNS, add-host, `-P`, `-p`, `--expose`, and MAC address conflicts.

State and persistence: only transient containers are created; no persistent daemon configuration is changed.

Dependencies and integration points: Linux and user-namespace gates, busybox, CLI validation layer, and daemon-side network mode validation.

Risks: some validation is noted as missing or skipped; error text assertions are brittle; behavior differs between CLI-side and daemon-side validation.

Test signals: supported network modes run a command successfully, while invalid option combinations fail before producing ambiguous container networking state.
