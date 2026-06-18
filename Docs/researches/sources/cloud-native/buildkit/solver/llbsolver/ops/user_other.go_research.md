# sources/cloud-native/buildkit/solver/llbsolver/ops/user_other.go

Purpose: non-Linux, non-Windows fallback for file operation user resolution.

Important APIs/types/functions: build tag `!linux && !windows`, `getReadUserFn`, and `readUser`.

Control flow: `getReadUserFn` returns `readUser`. `readUser` returns nil for nil chown options and otherwise errors with "only implemented in linux and windows".

State/persistence: none.

Dependencies/integration: keeps the package buildable on other platforms while making chown-by-user behavior explicitly unsupported.

Risks: any file op requiring chown resolution on unsupported platforms fails at runtime. Numeric-only chown is not implemented here even though it might be possible, so platform behavior differs from Linux/Windows.

Test signals: no direct tests in this subset; build tags are the main coverage.
