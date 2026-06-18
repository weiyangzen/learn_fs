<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder.go -->
# sources/cloud-native/moby/daemon/config/builder.go

## Purpose
Defines daemon JSON configuration structures for BuildKit builder garbage collection, history, and entitlements.

## Important APIs, Types, And Functions
`BuilderGCRule.UnmarshalJSON`, `BuilderGCFilter.MarshalJSON`, `BuilderGCFilter.UnmarshalJSON`, `BuilderGCConfig.IsEnabled`, `BuilderGCConfig.UnmarshalJSON`, and structs `BuilderHistoryConfig`, `BuilderEntitlements`, `BuilderConfig`.

## Control Flow
GC rule and config unmarshalling map deprecated `keepStorage` fields to reserved-space fields. Filter JSON accepts the current array-of-`key=value` form and falls back to a deprecated map form.

## State And Persistence Behavior
No runtime state; these types control daemon JSON decode/encode and thus persisted daemon config semantics.

## Dependencies And Integration Points
Uses BuildKit daemon config duration, daemon internal filters, JSON, sorting, and string normalization. Consumed by `config.Config.Builder`.

## Risks And Test Signals
Risks include silently accepting malformed filters as empty values and compatibility pressure around deprecated fields. Builder config tests cover current/deprecated formats and default enabled behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder.go -->
