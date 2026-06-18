## sources/control-plane/rook/cmd/rook/userfacing/multus/validation/validation.go

Purpose: implements the visible Multus validation CLI for running, cleaning up, and configuring network validation tests before installing Rook with Multus.

Important APIs and functions: `Cmd`, `runCmd`, and `cleanupCmd` are Cobra commands. Global `validationConfig` holds a `multus.ValidationTest`. `runValidation()` handles config-file loading, CLI-derived defaults, validation, execution, report printing, success cleanup, and exit codes. `runCleanup()` deletes test resources. Custom pflag values `timeoutMinutes` and `timeoutSeconds` validate positive durations.

Control flow: init creates defaults, registers flags on run/cleanup, sets network/service-account/image/host-check and config-file options, and marks `--config` mutually exclusive with most run flags except `--host-check-only`. Run and cleanup obtain a Kubernetes client via `rook.GetInternalOrExternalClient()`. The run path reads YAML config if specified, otherwise builds a simple node config from `--daemons-per-node`; then validates and calls `validationConfig.Run(ctx)`. Success with no suggestions triggers cleanup and exit 0; failure or suggestions prints diagnostics and leaves resources for debugging.

State and persistence: creates and cleans Kubernetes test resources through `pkg/daemon/multus`. Reads optional config file and `KUBECONFIG`. Mutates process-global `validationConfig`, which can make tests or repeated command invocations order-sensitive.

Dependencies and integration points: integrates user-facing CLI, Kubernetes client selection, and multus validation daemon logic. Risks: explicit `os.Exit()` paths complicate unit tests; leaving resources after suggestions/failure is intentional but can surprise automation; config-file mutual exclusion must stay synced with new flags. Direct tests are not in this subset.
