<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_test.go -->
# sources/cloud-native/moby/daemon/config/config_test.go

## Purpose
Provides broad platform-common tests for daemon config file decoding, conflict detection, validation, reload behavior, API version bounds, DNS parsing, and proxy credential sanitization.

## Important APIs, Types, And Functions
`makeConfigFile`, `TestDaemonConfigurationUnicodeVariations`, `TestFindConfigurationConflicts*`, `TestValidateConfigurationErrors`, `TestValidateConfiguration`, `TestValidateMinAPIVersion`, `TestConfigDNS`, `TestReload*`, `TestMaskURLCredentials`, and `TestSanitize`.

## Control Flow
Tests create temp JSON files, configure pflag sets including named options, merge or reload config, and compare returned config/errors. Validation tests merge partial overrides into defaults before calling `Validate`.

## State And Persistence Behavior
Temp files only. Some reload tests depend on root privileges for default missing config behavior. Global environment is not materially changed.

## Dependencies And Integration Points
Uses mergo, text encodings, registry opts, IPAM opts, pflag, go-cmp, and gotest. It is the main regression suite for `config.go`.

## Risks And Test Signals
Signals include BOM handling, invalid UTF-8 offsets, unknown option errors, masked proxy credentials in conflicts, platform-specific exec-opt validation, reload callback atomicity expectations, DNS scope handling, and duplicate-label normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_test.go -->
