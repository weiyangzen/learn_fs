# sources/distributed-fs/openafs/src/splint.cfg

## Purpose
`splint.cfg` configures lightweight static analysis for the OpenAFS source tree with Splint. It deliberately asks for weak checking and disables checks that are noisy for this codebase.

## Important APIs, types, and functions
There are no code APIs. The important settings are `-weak`, `-name-checks`, `+unix-lib`, `-D__signed__=signed`, `-fixed-formal-array`, and `+match-any-integral`.

## Control flow
The file is consumed by Splint when analysis is run. Options relax namespace and array-formal warnings, model standard Unix library behavior, and normalize the old Red Hat `__signed__` keyword issue.

## State and persistence behavior
No runtime state is created. Its persistent effect is on static-analysis diagnostics and therefore on developer gating.

## Dependencies and integration points
It depends on Splint option syntax and historical system headers. It integrates with any developer or CI target invoking Splint from `src`.

## Risks
`-weak` and `+match-any-integral` can hide meaningful type and integer-conversion issues. The config is intentionally permissive, so it should not be treated as a strong memory-safety proof.

## Test signals
Validation is a Splint invocation over representative OpenAFS files, confirming the config is accepted and suppresses intended legacy warnings without masking build-breaker parser errors.
