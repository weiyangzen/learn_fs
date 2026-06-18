## sources/control-plane/rook/cmd/rook/discover.go

Purpose: defines the hidden `rook discover` command used by the operator to run the device discovery daemon. It periodically discovers storage devices and optionally augments data via `ceph-volume inventory`.

Important APIs and functions: `discoverCmd` is the Cobra command. `init()` registers `--discover-interval` and `--use-ceph-volume`, applies `ROOK_*` environment overrides, and binds `RunE` to `startDiscover()`. `startDiscover()` sets logging, logs startup flags, creates the in-cluster Rook context, and calls `discover.Run()`.

Control flow: command execution is straightforward: parse flags/env, initialize logging, create Kubernetes/Rook clients via `rook.NewContext()`, then delegate the long-running loop to `pkg/daemon/discover`. Errors from discovery are treated as fatal with `rook.TerminateFatal()`.

State and persistence: this file has no direct persistence. State is in the daemon package and Kubernetes resources it updates. The command consumes process env, command flags, and in-cluster configuration.

Dependencies and integration points: integrates with `cmd/rook/rook` for logging/context, `pkg/daemon/discover` for actual scanning, Cobra for CLI, and the shared flag/env loader. Risks: hidden command assumes it runs in a Kubernetes pod with valid service account credentials; bad intervals or ceph-volume behavior are not validated here. Test signals are absent in this file; confidence depends on daemon package tests and operator deployment tests.
