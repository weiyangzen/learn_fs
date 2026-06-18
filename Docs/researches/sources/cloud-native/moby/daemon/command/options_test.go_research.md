<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options_test.go -->
# sources/cloud-native/moby/daemon/command/options_test.go

## Purpose
Verifies common daemon option flag installation and default certificate paths.

## Important APIs, Types, And Functions
`TestCommonOptionsInstallFlags` and `TestCommonOptionsInstallFlagsWithDefaults` use `newDaemonOptions`, `installFlags`, `pflag.FlagSet.Parse`, and `defaultCertPath`.

## Control Flow
The first test parses explicit TLS cert flags and asserts they populate `TLSOptions`. The second parses no flags and asserts CA, cert, and key paths default under `defaultCertPath`.

## State And Persistence Behavior
No disk writes. Reads package-level default cert path state, which may derive from environment.

## Dependencies And Integration Points
Depends on `daemon/config`, pflag, and test assertions. Protects CLI flag compatibility.

## Risks And Test Signals
Signals are exact path propagation. The tests do not cover `setDefaultOptions` file-existence clearing or env var changes after package init.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options_test.go -->
