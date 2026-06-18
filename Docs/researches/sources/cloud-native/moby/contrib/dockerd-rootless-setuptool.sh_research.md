# sources/cloud-native/moby/contrib/dockerd-rootless-setuptool.sh

## Purpose
Installs, checks, and uninstalls rootless Docker user services and CLI context configuration for non-root users.

## APIs, Types, And Functions
Important functions include `INFO`, `WARNING`, `ERROR`, `init`, `cmd_entrypoint_check`, `cmd_entrypoint_nsenter`, `show_systemd_error`, `install_systemd`, `install_nonsystemd`, `cli_ctx_exists`, `cli_ctx_create`, `cli_ctx_use`, `cli_ctx_rm`, `cmd_entrypoint_install`, `cmd_entrypoint_uninstall`, and `usage`.

## Control Flow, State, And Integration
`init` validates Linux, non-root execution, PATH, HOME, XDG runtime state, subuid/subgid, and optional systemd support. Install paths create systemd user units or non-systemd shell instructions, manage Docker CLI contexts, and respect force/iptables flags. Persistent state includes user systemd units, CLI contexts, runtime dirs, and shell environment guidance.

## Risks And Test Signals
Risks include privilege confusion, bad systemd user environment, stale contexts, iptables limitations, and incomplete cleanup. Integration is with `dockerd-rootless.sh`, RootlessKit, systemd user services, and Docker CLI context management.
