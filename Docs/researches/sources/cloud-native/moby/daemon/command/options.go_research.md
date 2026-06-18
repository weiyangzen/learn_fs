<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options.go -->
# sources/cloud-native/moby/daemon/command/options.go

## Purpose
Defines common daemon CLI options and TLS certificate defaulting behavior.

## Important APIs, Types, And Functions
Constants for default TLS filenames and flag names; package vars sourced from `DOCKER_CONFIG`, `DOCKER_CERT_PATH`, and `DOCKER_TLS_VERIFY`; `daemonOptions`; `defaultCertPath`; `newDaemonOptions`; `installFlags`; `setDefaultOptions`.

## Control Flow
`installFlags` installs debug, validate, TLS, TLS verify, cert path, key path, and host flags. `setDefaultOptions` makes `--tlsverify` imply TLS, defaults TLS verification when TLS is on, nils TLS options when TLS is off, and clears implicit cert/key files that do not exist.

## State And Persistence Behavior
Uses and mutates package-level `configDir` and `dockerCertPath`. Reads certificate file existence but does not write files.

## Dependencies And Integration Points
Integrates `tlsconfig.Options`, daemon config defaults, daemon host validation, pflag, and historical Docker env vars.

## Risks And Test Signals
Risks include package-level env snapshots, non-XDG `DOCKER_CONFIG` legacy behavior, and implicit TLS verification surprises. Tests cover flag installation defaults and daemon config TLS merge behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options.go -->
