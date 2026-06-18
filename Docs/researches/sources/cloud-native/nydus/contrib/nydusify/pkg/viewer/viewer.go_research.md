<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer.go

## Purpose

This file implements the nydusify filesystem viewer: it parses a target Nydus image, pulls bootstrap/config artifacts, prepares nydusd configuration, mounts the image, and waits for a termination signal before cleanup.

## Important APIs, Types, and Functions

`Opt` captures workdir, target reference, mount path, nydusd path, backend type/config, expected arch, fs version, and prefetch flag. `FsViewer` holds options, a parser, and `tool.NydusdConfig`. `New` validates target and constructs provider/parser. `PullBootstrap`, `getBootstrapFile`, `MountImage`, `View`, `view`, and `handleExternalBackendConfig` implement the workflow.

## Control Flow

`View` calls `view` and retries once over HTTP if `utils.RetryWithHTTP` says the error is retryable and the remote can switch protocol. `view` parses the image, detects model artifacts, builds nydusd config paths under `WorkDir`, pulls bootstrap and optional backend JSON, rewrites external backend config, enables digest validation for RAFS v5, mounts nydusd, then blocks until SIGINT or SIGTERM before deleting `WorkDir`.

## State and Persistence Behavior

The viewer deletes and recreates `WorkDir`, writes pretty JSON dumps, writes extracted bootstrap/backend files, creates blob cache and mount directories, runs a nydusd process through `tool.NewNydusd`, and removes the work directory after signal. It does not unmount directly in this file; unmount behavior is implied by daemon/tool handling.

## Dependencies and Integration Points

It integrates with image providers, parser, model-spec artifact type, checker/tool nydusd wrapper, external backend config rewrite, bootstrap layer filenames from utils constants, and OS signal handling.

## Risks and Test Signals

Risks include destructive `WorkDir` cleanup, indefinite blocking in non-interactive contexts, reliance on signal delivery, and external backend rewrite assumptions. Tests cover constructor errors, pretty dump, bootstrap pull paths, mount errors, external backend handling, and HTTP retry, but not a full successful signal-driven view lifecycle.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer.go -->
