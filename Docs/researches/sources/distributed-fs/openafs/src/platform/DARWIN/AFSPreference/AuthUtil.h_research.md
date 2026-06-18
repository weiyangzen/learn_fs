# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AuthUtil.h

Purpose: declares a singleton wrapper around macOS Authorization Services used by the preference pane and older file utilities to obtain, store, serialize, and use an `AuthorizationRef`.

Important APIs and state: `AuthUtil` stores `authorizationRef` and `isAuthorizationRefOwned`. It exposes `autorize`, `deautorize`, `authorization`, `setAuthorization:`, `extFormAuth`, `execUnixCommand:args:output:`, and singleton/memory-management overrides. The spelling of `autorize`/`deautorize` is part of the local API.

Control flow and persistence: no persistent storage is declared; the object is process-global runtime state. The `SFAuthorizationView` delegate in `AFSCommanderPref.m` injects an authorization reference via `setAuthorization:` so `TaskUtil` can serialize it for the XPC privileged helper.

Dependencies and integration: imports Cocoa and Security Authorization headers. Older `FileUtil` operations call `execUnixCommand`, while newer root tasks flow through `TaskUtil` and the XPC helper.

Risks: singleton lifetime and retain-count overrides assume manual reference counting. Callers must not outlive an externally owned `AuthorizationRef`. The API still exposes `AuthorizationExecuteWithPrivileges`-style execution, which is deprecated and higher risk than the helper-based path.

Test signals: verify singleton identity, external authorization replacement, owned authorization cleanup, external-form serialization failure behavior, and command execution with and without output capture.
