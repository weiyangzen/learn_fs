<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/env.go -->
# sources/cloud-native/moby/daemon/pkg/opts/env.go

## Purpose
Validates and normalizes environment-variable flag entries while intentionally leaving variable-name syntax mostly to the container workload.

## Important APIs, Types, And Functions
`ValidateEnv(val string) (string, error)` is the exported validator. It uses `strings.Cut` to detect `KEY=VALUE` and `os.LookupEnv` to fill values for bare names.

## Control Flow
If the key before `=` is empty, the function returns an invalid-variable error. If `=` is present, it returns the original string. If no `=`, it looks up the key in the current process environment and returns `KEY=value` only when present; otherwise it returns the original bare key.

## State, Dependencies, And Integration Points
Reads process environment but persists nothing. It integrates with Docker CLI/daemon option parsing for `--env`-style values.

## Risks And Test Signals
Host environment affects bare-key normalization. The intentionally permissive name policy accepts spaces, digits, and punctuation. `env_test.go` covers explicit empty-name failures and PATH lookup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/env.go -->
