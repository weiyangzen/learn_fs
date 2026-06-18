# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate.go

## Purpose
This file defines a controller-runtime predicate used to detect meaningful monitor endpoint changes in the monitor endpoint ConfigMap. Its main use is triggering bootstrap peer token updates when monitor endpoint scheduling changes.

## Important APIs, Types, And Functions
`PredicateMonEndpointChanges[T *corev1.ConfigMap]()` returns `predicate.TypedFuncs[T]`. Create, delete, and generic events are ignored. Update events are considered only for ConfigMaps named `EndpointConfigMapName`. `wereMonEndpointsUpdated(namespace, oldCMData, newCMData)` compares the `mapping` JSON field by unmarshalling into `opcontroller.Mapping` and comparing the `Schedule` map.

## Control Flow And State
On update, the predicate casts the old and new objects to ConfigMaps, checks the name, and calls the mapping comparison helper. The helper requires both old and new `mapping` keys. It unmarshals both mappings; malformed JSON logs at debug level and returns false. If schedule lengths differ, the endpoint set changed. If lengths match, it sorts keys from the old schedule and deep-compares each old schedule entry against the corresponding new entry.

## Dependencies And Integration Points
The code depends on controller-runtime predicates/events, Rook monitor endpoint naming, `opcontroller.Mapping`, JSON decoding, sorting, `reflect.DeepEqual`, and Rook namespaced logging. It integrates with reconciler watch filters for ConfigMap updates.

## Risks And Test Signals
The comparison intentionally ignores create/delete events and malformed mapping updates, which avoids noisy reconciles but could miss repair opportunities after invalid data. A code risk is that `newKeys` is built by iterating over `oldMappingToGo.Schedule`; because the resulting `newKeys` is not used, this is harmless but misleading. The deep compare by old keys will still detect deleted/changed entries when lengths match because missing new entries compare unequal. `predicate_test.go` covers missing keys, identical content with different map order, changed monitor IP, and changed length.
