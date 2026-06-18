# sources/cloud-native/moby/integration-cli/docker_cli_login_test.go

Purpose: validates CLI login behavior without a TTY and against an htpasswd-protected private registry.

Important APIs and functions: `DockerCLILoginSuite`, `exec.Command(dockerBinary, "login")`, `bytes.NewBufferString` to provide non-TTY stdin, `dockerCmdWithError`, and `cli.DockerCmd` for registry login.

Control flow: `TestLoginWithoutTTY` runs `docker login` with stdin backed by a buffer and expects failure when no interactive TTY is available, except for a Windows skip. `TestLoginToPrivateRegistry` first attempts wrong credentials and expects `401 Unauthorized`, then logs in with suite-provided registry credentials.

State and persistence: successful registry login writes auth material through the CLI's normal config path; the test itself does not inspect the config file.

Dependencies and integration points: private registry auth suite, `dockerBinary`, OS-specific terminal behavior, and registry username/password helpers.

Risks: TTY error behavior can vary by CLI version and OS; password-on-command-line usage is test-only but mirrors legacy CLI behavior; registry auth failures depend on exact server response text.

Test signals: login must reject non-interactive use when credentials cannot be gathered and must authenticate correctly with valid private registry credentials after rejecting invalid ones.
