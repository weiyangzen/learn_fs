# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/main.go

Purpose: Builds the `ctr-remote` CLI by extending containerd's standard `ctr` app with stargz-specific image commands and the hidden fanotify command.

Important API: `main`.

Control flow: It creates the base `ctr` app, prepares custom commands (`rpull`, `optimize`, `convert`, `get-toc-digest`, `ipfs-push`), finds the `images` command, replaces any subcommands with matching names, appends missing custom subcommands, then appends the hidden top-level `FanotifyCommand`. It runs the CLI with `os.Args` and prints failures to stderr before exiting nonzero.

State and persistence: No persistent state; this is command registration and process exit handling.

Dependencies and integration: Imports containerd's `ctr/app`, urfave cli, and the local commands package. The hidden fanotify command is intentionally top-level so `SpawnFanotifier` can call `ctr-remote fanotify /`.

Risks: If containerd's app command shape changes and the `images` command is absent or renamed, custom image commands will not be inserted, but fanotify still appends. Map iteration means appended custom subcommand order is not deterministic for commands not replacing existing names.

Test signals: No direct tests; simple CLI assembly.
