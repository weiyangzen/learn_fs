# sources/cloud-native/moby/integration-cli/docker_cli_logout_test.go

Purpose: validates logout behavior with external credential helpers, including hostnames stored with and without URL schemes.

Important APIs and functions: registry auth suite methods, fixture credential helper `docker-credential-shell-test`, `os.MkdirTemp`, `os.WriteFile`, `os.ReadFile`, `filepath.Abs`, `exec.Command`, `s.d.Cmd`, and `cli.DockerCmd`.

Control flow: one test adds the auth fixture to `PATH`, creates a temp `config.json` with `credsStore`, logs in, confirms no inline `"auth"` is stored, tags/pushes, logs out, confirms registry entries are removed, and verifies pull fails without credentials. The hostname test preloads the helper with `https://host`, writes config entries for scheme and bare host, logs in, then logs out and asserts both entries disappear.

State and persistence: intentionally writes temp Docker config files and uses an external credential store. It also tags and pushes registry images through a daemon started with busybox.

Dependencies and integration points: credential helper fixture, private registry, temp Docker config directories, daemon command wrapper, and filesystem config persistence.

Risks: sensitive to credential-helper protocol behavior and config key normalization; failures can leave temp helper state outside the Docker config if the fixture is broken.

Test signals: logout removes credentials from helper-backed config for both scheme-qualified and bare registry hostnames, and registry access fails after logout.
