## sources/control-plane/rook/cmd/rook/rook/rook.go

Purpose: shared command infrastructure for the Rook binary. It defines the root command, logging setup, Kubernetes/Rook client context creation, operator pod introspection helpers, fatal termination behavior, Ceph version detection, and flexible Kubernetes client creation for user-facing tools.

Important APIs and functions: `RootCmd`, `SetLogLevel()`, `LogStartupInfo()`, `NewContext()`, `GetOperatorImage()`, `GetOperatorServiceAccount()`, `CheckOperatorResources()`, `TerminateOnError()`, `TerminateFatal()`, `GetOperatorBaseImageCephVersion()`, and `GetInternalOrExternalClient()`.

Control flow: init registers persistent `--log-level`, initializes Cobra help/completion, applies `ROOK_*` env overrides, and sets a quiet controller-runtime zap logger. `NewContext()` creates an in-cluster REST config and Kubernetes, Rook, NetworkAttachmentDefinition, and apiextensions clients; failures terminate. `GetInternalOrExternalClient()` tries each `KUBECONFIG` path, then default CLI config, then in-cluster config.

State and persistence: global `logLevelRaw`, `RootCmd`, and package logger drive process behavior. `TerminateFatal()` appends errors to `/dev/termination-log` and exits through fatal logging. `CheckOperatorResources()` sets `OPERATOR_RESOURCES_SPECIFIED` when the running operator container has resources configured.

Dependencies and integration points: central dependency for almost all Rook CLI commands. It depends on client-go, Rook generated clients, NAD clients, controller-runtime logging, and Rook utility packages. Risks: in-cluster-only `NewContext()` makes hidden commands unsuitable outside pods; termination-log writes assume the file exists and is writable; global logging/env state can make tests order-sensitive. No direct tests are listed here.
