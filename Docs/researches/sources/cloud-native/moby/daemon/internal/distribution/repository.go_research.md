# sources/cloud-native/moby/daemon/internal/distribution/repository.go

## Purpose
Returns all reachable pull repositories for a reference, including mirrors where configured.

## APIs, Control Flow, and Integration
`GetRepositories` trims and validates the name, resolves pull endpoints, creates a repository for each endpoint with pull scope, logs per-endpoint failures, collects successful repositories, and returns the last error if none were reachable. It wraps reserved-name validation as invalid parameter.

## State, Dependencies, and Risks
No persistence; it performs network pings/auth setup through `newRepository`. Risks include returning partial success silently when some endpoints fail and `lastError` being nil only if endpoint list is empty/unusual. Used by callers that need repository handles rather than full pull orchestration.
