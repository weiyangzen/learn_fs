# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_secrets.go

Purpose: converts secret mounts for RUN and masks secret environment values in progress command names.

Important APIs: `dispatchSecret`, `withSecretEnvMask`, and `secretEnv` implementing `shell.EnvGetter`.

Control flow: secret id comes from cache ID, source, target basename, or errors if none exists. Target is derived from mount target or `/run/secrets/<id>` unless mounted as env. Outline metadata records id, location, and required flag. LLB secret options include ID, optional flag, env name, and file uid/gid/mode with default `0400` when metadata is specified. `withSecretEnvMask` overlays env-mounted secrets with `****` for command rendering.

State and persistence: records outline secret metadata on `dispatchState`; secret contents are never persisted in Dockerfile conversion.

Dependencies and integration: used by `dispatchRunMounts` and `dispatchRun` command name formatting; integrates LLB secret options and parser ranges.

Risks and test signals: risks include id derivation surprises, target/env interactions, required flag accuracy, and accidentally exposing secret values in custom names. Secret mount tests and outline tests cover this.
