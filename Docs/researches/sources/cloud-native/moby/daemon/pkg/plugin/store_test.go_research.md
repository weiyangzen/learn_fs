<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/store_test.go

## Purpose
Tests plugin capability filtering and reference-count behavior.

## Important APIs, Types, And Functions
`TestFilterByCapNeg`, `TestFilterByCapPos`, and `TestStoreGetPluginNotMatchCapRefs` use `v2.Plugin.FilterByCap`, `Store.Add`, and `Store.Get`.

## Control Flow
The tests build fake plugins with interface capability IDs, assert mismatched capability errors, assert matched capability success, and confirm store lookup does not increment refs when capability filtering fails, both disabled and enabled.

## State, Dependencies, And Integration Points
State is an in-memory `Store` and plugin structs. It validates behavior consumed by daemon subsystems that acquire plugins by capability.

## Risks And Test Signals
The tests do not cover ambiguous names, partial IDs, legacy fallback, or handler callbacks. They strongly protect refcount correctness on failed lookups.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store_test.go -->
