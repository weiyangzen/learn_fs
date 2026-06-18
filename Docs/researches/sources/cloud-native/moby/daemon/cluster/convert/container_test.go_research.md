# sources/cloud-native/moby/daemon/cluster/convert/container_test.go

## Purpose
Tests the tmpfs options compatibility shim between Docker API's structured `[][]string` representation and swarmkit's string field.

## Important APIs, Types, And Functions
Tests unexported `tmpfsOptionsToGRPC` and `tmpfsOptionsFromGRPC`.

## Control Flow
One test marshals options such as `noexec` and `uid=12345` to a compact JSON string. The other unmarshals that string and deep-compares the original structure.

## State And Persistence
No state. The tested representation is what may be stored in swarmkit service specs.

## Dependencies And Integration Points
Directly covers helper behavior used by container mount conversion.

## Risks And Test Signals
Does not cover malformed JSON; production intentionally returns an empty value on unmarshal errors. Failures indicate backward-compatibility changes in stored tmpfs option encoding.
