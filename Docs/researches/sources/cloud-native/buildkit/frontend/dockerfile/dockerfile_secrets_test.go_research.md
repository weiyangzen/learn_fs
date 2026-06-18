# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_secrets_test.go

## Purpose
This file tests Dockerfile secret mounts in RUN instructions, including file parameters, required-secret failure, environment-variable injection, status redaction, and combined env/file mounting. It registers `secretsTests` into `allTests`.

## Important APIs, Types, and Functions
Tests are `testSecretFileParams`, `testSecretRequiredWithoutValue`, `testSecretAsEnviron`, and `testSecretAsEnvironWithFileMount`. They use BuildKit sessions, `secretsprovider.FromMap`, `client.SolveStatus`, status channels, `assert` and `require`, platform skips, and local mounts.

## Control Flow and Assertions
`testSecretFileParams` supplies `mysecret` and verifies a mounted secret file has expected uid/gid/mode bits, then a later RUN confirms no stub remains. `testSecretRequiredWithoutValue` does not attach a secret provider and expects `secret mysecret: not found`. `testSecretAsEnviron` mounts a secret with `env=SECRET_ENV`, verifies the value is visible in the command environment and no default secret file exists, then reads solve status vertex names to ensure secret values are masked. `testSecretAsEnvironWithFileMount` confirms `env=` and `target=` can both be used for the same secret.

## State, Persistence, and Dependencies
Secret values are session-scoped attachables and should not persist into layers unless explicitly written by the command. The file depends on BuildKit session secret plumbing, Dockerfile mount parsing, status stream redaction, and POSIX tmpfs-backed file mounts for file-mode tests.

## Integration Points
The tests integrate Dockerfile frontend secret mount options with session providers, executor mount setup, frontend status naming/redaction, platform path differences, and layer persistence boundaries.

## Risks and Test Signals
Critical risks are secret leakage in status names, secret files persisting after RUN, required secrets silently becoming optional, file mode/ownership regressions, and Windows unsupported tmpfs paths accidentally running. Signals include exact error text, stat output, file absence checks, status-channel inspection, and env/file dual-access assertions.
