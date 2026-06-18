## sources/control-plane/rook/cmd/rook/util/cmdreporter.go

Purpose: hidden utility command that runs a command to completion and stores stdout, stderr, and return code in a Kubernetes ConfigMap. It is intended to be invoked via operator helpers rather than by end users.

Important APIs and functions: `CmdReporterCmd` defines flags `--command`, `--config-map-name`, and `--namespace`, all required. `runCmdReporter()` parses the JSON-list command string, creates a signal-aware context, builds the Rook Kubernetes context, constructs `pkg/daemon/util.CmdReporter`, and runs it.

Control flow: init declares flags and panics if required marking fails. Runtime parsing is delegated to `util.CmdReporterFlagArgumentToCommand()`. A nonzero child command return code is not itself a command error; errors are reserved for parse/run/storage failures per the command long description.

State and persistence: writes or overwrites command result data in a ConfigMap and applies ownership/application labeling in the daemon utility. Reads in-cluster Kubernetes credentials. Hidden command state is only flag globals.

Dependencies and integration points: used by operator/k8sutil wrappers for jobs or diagnostics. Risks: command input is powerful by design; RBAC and caller construction must constrain it. ConfigMap overwrite behavior is intentional but requires label conflict safeguards downstream. No direct tests in this file; parser/reporter package tests are the likely signal.
