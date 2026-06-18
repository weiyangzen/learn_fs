<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update_install_script.sh -->
# sources/control-plane/juicefs-csi-driver/hack/update_install_script.sh

## Purpose
Maintenance helper that refreshes embedded webhook manifest blocks inside `scripts/juicefs-csi-webhook-install.sh` from generated deploy YAML files.

## Important APIs, Types, and Resources
Reads `deploy/webhook.yaml` and `deploy/webhook-with-certmanager.yaml`, locates marker comments `# webhook.yaml start/end` and `# webhook-with-certmanager.yaml start/end` in the install script, and rewrites the marked ranges using `head`, `tail`, `cat`, `mv`, and `chmod`.

## Control Flow
For each manifest, it copies the current deploy YAML to a temporary file, computes marker line numbers with `cat -n | grep | awk`, writes a backup replacement containing head + manifest + tail, moves it over the install script, and removes temporaries.

## State and Persistence
Persists changes to `scripts/juicefs-csi-webhook-install.sh`; creates transient `.bak`, `webhook.yaml`, and `webhook-with-certmanager.yaml` files in the working directory.

## Dependencies and Integration Points
Depends on Bash, marker comments staying unique, generated deploy YAMLs being current, POSIX text utilities, and the install script path. Integrates generated manifests with standalone webhook install tooling.

## Risks
Risks include fragile line-number math, duplicate/missing markers corrupting the install script, unquoted variables, temporary files colliding with real files, and appending via `cat >>` if stale temp files exist.

## Test Signals
Run from repo root after regenerating manifests, diff the install script, execute shellcheck if available, and smoke-test the install script in a disposable cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update_install_script.sh -->
