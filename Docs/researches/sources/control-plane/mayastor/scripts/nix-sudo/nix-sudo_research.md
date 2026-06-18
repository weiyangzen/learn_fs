# sources/control-plane/mayastor/scripts/nix-sudo/nix-sudo

Purpose: wrapper that runs commands under `sudo -E` while resolving the first non-option argument to its Nix-shell binary path.

Important APIs/types/functions: builds `CMD` by escaping backslashes and quotes, treats `*=*` and `-*` arguments as pre-binary flags/env assignments, resolves the command with `which`, then executes `bash -c "sudo -E $CMD"`.

Control flow: iterates all args, shifts as it consumes them, preserves options before the command, and quotes all accumulated arguments.

State/persistence: no direct state; executes privileged commands preserving environment.

Dependencies/integration: used by cleanup/report scripts so sudo can find Nix-provided tools.

Risks: hand-built shell quoting is security-sensitive. If the command cannot be resolved by `which`, `BIN` may become empty and execution will fail oddly.

Test signals: commands like `nix-sudo nvme list` should run the Nix-shell `nvme` binary via sudo.
