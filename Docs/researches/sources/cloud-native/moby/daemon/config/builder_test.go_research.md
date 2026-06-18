<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder_test.go -->
# sources/cloud-native/moby/daemon/config/builder_test.go

## Purpose
Tests BuildKit builder GC JSON compatibility and defaults.

## Important APIs, Types, And Functions
`TestBuilderGC`, `TestBuilderGC_DeprecatedKeepStorage`, `TestBuilderGCFilterUnmarshal`, and `TestBuilderGC_Enabled` call `MergeDaemonConfigurations`, JSON unmarshal, and filter match helpers.

## Control Flow
Tests write temp daemon JSON with builder GC policy, merge it into config, and compare expected rules. A regression test feeds malformed filter text without `=` to ensure no panic. Enabled tests table-drive absent/empty/explicit values.

## State And Persistence Behavior
Only temp config files and in-memory structs.

## Dependencies And Integration Points
Depends on `daemon/config`, internal filters, JSON, go-cmp, and gotest tools.

## Risks And Test Signals
Signals include deprecated map filter parsing, `keepStorage` migration, policy preservation, and `IsEnabled` defaulting true unless explicitly false.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder_test.go -->
