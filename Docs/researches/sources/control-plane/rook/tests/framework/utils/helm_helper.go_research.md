# sources/control-plane/rook/tests/framework/utils/helm_helper.go

Purpose: `HelmHelper` wraps Helm CLI execution for Rook test installs, upgrades, and uninstalls.

Important APIs/types/functions: `HelmHelper` with executor and `HelmPath`; `NewHelmHelper`; `Execute`; `InstallLocalHelmChart`; `InstallVersionedChart`; `InstallOrUpgradeHelmRepoChart`; `UninstallHelmReleaseIfExists`; `DeleteLocalRookHelmChart`; helper `createValuesFile`; root finder `FindRookRoot`.

Control flow: install methods assemble Helm CLI args, optionally create a temporary `values-test.yaml`, and call `helm install`, `upgrade`, or `upgrade --install`. Local installs retry up to five times. Versioned installs add the `rook-release` repo and install chart versions. Repo chart installs force-update a repo, update repos, then install/upgrade. Uninstall tolerates “not found” messages. `FindRookRoot` walks parents until a `tests` folder is found.

State and persistence behavior: mutates Helm releases, repos/cache, namespaces, and temporary values files. `values-test.yaml` is removed after install attempt.

Dependencies and integration points: used by Helm installer methods; depends on Rook repo layout, Helm binary path, YAML marshaling, and Rook command executor.

Risks: temporary values file uses a fixed relative filename, which can race under parallel tests in the same working directory. `FindRookRoot` treats any parent with `tests` as root. Helm repo/network failures can make tests flaky. Missing `HelmPath` fails at command execution time.

Test signals: command argument construction, values serialization, retry behavior, not-found uninstall tolerance, and local chart path resolution.
