# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/logs.go

Purpose: implements `buildctl debug logs`, allowing users to replay build progress logs or retrieve an attached OpenTelemetry trace for a build reference.

Important APIs and flow: `logs` requires a build ref and resolves the client. With `--trace`, it fetches a history record, validates trace metadata, opens the trace blob from the content store, and copies raw trace bytes to stdout. Without `--trace`, it opens a `Status` stream for the ref, creates a progress writer with the requested mode, converts each protobuf status response into `client.SolveStatus`, and feeds the writer until EOF.

State and dependencies: reads daemon history, content store, and solver status state. It depends on control API streams, content proxy, progresswriter, OCI descriptor/digest handling, and app context.

Risks and test signals: progress mode can block if writer shutdown is mishandled, and trace mode outputs binary data. Missing refs and records without trace are explicit errors. There are no direct tests in this group.
