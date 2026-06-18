# sources/cloud-native/moby/integration/system/info_test.go

## Purpose
Tests general `/info` API fields and daemon configuration reporting, including warning output for insecure TCP listeners, debug metrics, insecure registries, and registry mirrors.

## Important APIs, Types, And Functions
- `TestInfoAPI` checks core `Info` fields from the environment daemon.
- `TestInfoAPIWarnings` starts a daemon listening on `0.0.0.0:23756` and checks root-access warning strings.
- `TestInfoDebug` starts `--debug` and checks debug flag, descriptor/goroutine counts, and root dir.
- `TestInfoInsecureRegistries` starts with CIDR and host insecure registry options and validates `RegistryConfig`.
- `TestInfoRegistryMirrors` starts with two mirrors and validates normalized/sorted mirror URLs.

## Control Flow
Some tests use the shared daemon; daemon-configuration tests skip remote/Windows, run in parallel, start isolated daemons with specific flags, call `Info`, and compare returned fields.

## State And Persistence
Isolated daemons create temporary roots and sockets. Info calls are read-only, but daemon startup flags define reported persistent config for the daemon lifetime.

## Dependencies And Integration Points
Integrates daemon startup flags, registry config parsing, info API serialization, warning generation, debug-mode metrics, and test daemon helpers.

## Risks And Edge Cases
Remote and Windows environments skip local daemon startup cases. Warning tests compare string fragments from formatted `Info`, which can be fragile. Insecure registry CIDR ordering is handled by membership checks while mirrors are sorted before compare.

## Test Signals
Passing means core info fields are populated and internally consistent; insecure TCP warning includes the bound host; debug mode reports true and nonzero runtime counters; insecure registry and mirror config are normalized as expected.
