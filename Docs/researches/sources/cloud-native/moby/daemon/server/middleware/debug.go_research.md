# sources/cloud-native/moby/daemon/server/middleware/debug.go

## Purpose
Adds debug logging around API requests, including method, URL, route vars, status for errors, and sanitized small JSON POST bodies.

## Important APIs, Types, And Functions
`DebugRequestMiddleware` wraps an API handler. `maskSecretKeys` recursively redacts sensitive keys in decoded JSON maps/arrays.

## Control Flow
The middleware prepares log fields, optionally peeks at JSON POST bodies up to 4 KiB, restores the request body through a buffered reader wrapper, decodes JSON into a map, masks secrets, serializes form data for log fields, calls the wrapped handler, and logs any error response status. Non-POST, non-JSON, or large requests skip body logging.

## State And Persistence
It reads/peeks the request body but preserves it for downstream handlers. It mutates the decoded logging copy of request JSON by masking values. It writes debug logs only.

## Dependencies And Integration Points
Uses `httputils.CheckForJSON`, `httpstatus.FromError`, containerd/log, logrus formatter detection, and ioutils body wrappers. Installed by `handlerWithGlobalMiddlewares` when debug logging is enabled.

## Risks And Edge Cases
Only selected key names are scrubbed; new secret-bearing fields may need updates. Body logging is limited to JSON objects/arrays that fit in 4 KiB. `Peek(maxBodySize)` treats non-EOF as too large or read error and skips body fields.

## Test Signals
`debug_test.go` verifies recursive, case-insensitive masking for secret/config data and credential-like fields.
