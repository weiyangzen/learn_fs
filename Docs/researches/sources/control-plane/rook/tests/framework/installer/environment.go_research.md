# sources/control-plane/rook/tests/framework/installer/environment.go

Purpose: this file exposes small environment helpers used by installer tests to discover Helm, logging, storage, base directories, and device filters.

Important APIs/types/functions: `TestHelmPath`, `TestLogCollectionLevel`, `StorageClassName`, `UsePVC`, `baseTestDir`, `TestScratchDevice`, `getDeviceFilter`, and `getEnvVarWithDefault`.

Control flow: each helper reads an environment variable and returns a default when unset. `TestHelmPath` checks `TEST_HELM_PATH`, then falls back to `exec.LookPath("helm")`. `baseTestDir` maps `TEST_BASE_DIR=WORKING_DIR` to the current working directory.

State and persistence behavior: no direct persistence. Returned values drive host-path directory creation, PVC mode, Helm execution, log collection, and OSD device selection elsewhere.

Dependencies and integration points: uses `os`, `os/exec`, current working directory, and the installer logger. Integrated by `CephInstaller`, `NewHelmHelper`, and manifest generation.

Risks: missing Helm path can propagate as an empty command string until Helm execution fails. Defaults such as `/data`, `/dev/nvme0n1`, and empty storage class/device filter are environment-specific. Logging environment values may expose sensitive paths but not credentials in this file.

Test signals: environment-driven tests should cover Helm path override/fallback, `WORKING_DIR` resolution, PVC mode detection from `TEST_STORAGE_CLASS`, and default values in local CI.
