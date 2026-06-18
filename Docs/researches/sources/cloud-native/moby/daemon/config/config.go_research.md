<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config.go -->
# sources/cloud-native/moby/daemon/config/config.go

## Purpose
Defines the platform-common daemon configuration model, default construction, config-file loading, flag/file conflict detection, validation, reload support, credential masking, and legacy option migration.

## Important APIs, Types, And Functions
Constants for defaults/API versions; maps `flatOptions`, `skipValidateOptions`, `skipDuplicates`, `migratedNamedConfig`; structs `LogConfig`, `NetworkConfig`, `TLSOptions`, `DNSConfig`, `CommonConfig`, `DaemonLogConfig`, `Proxies`; functions `New`, `Reload`, `MergeDaemonConfigurations`, `getConflictFreeConfiguration`, `configValuesSet`, `findConfigurationConflicts`, `ValidateMinAPIVersion`, `Validate`, `parseExecOptions`, `MaskCredentials`, `migrateHostGatewayIP`, `Sanitize`.

## Control Flow
`New` applies common defaults then platform defaults. Config loading reads JSON, decodes BOM-aware UTF-8/UTF-16 variants, flattens non-flat nested keys for conflict detection, adjusts bool flag values for explicit false config values, records `ValuesSet`, unmarshals into `Config`, and runs migrations. Merge overlays flags config onto file config using mergo, then validates.

## State And Persistence Behavior
Reads daemon JSON from disk and carries explicit config keys in `ValuesSet`. It does not write config. Reload calls a supplied callback after validation.

## Dependencies And Integration Points
Integrates pflag, daemon option types, registry validation, generic resource parsing, platform validation hooks, text encodings, and containerd logging formats.

## Risks And Test Signals
Risks include pre-merge reload validation for partial configs, flattening exceptions hiding conflicts, env-driven minimum API constraints, and URL credentials in error messages. Tests cover Unicode, conflicts, validation, reload, DNS parsing, credential masking, and sanitization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config.go -->
