# sources/cloud-native/containerd/internal/userns/idmap_test.go

## Purpose
Tests user namespace ID mapping translation, overflow handling, and serialization.

## Important APIs, Types, And Functions
Tests cover `RootPair`, `ToHost`, `Marshal`, `Unmarshal`, and helper behavior through table-driven mappings.

## Control Flow
Cases build `IDMap` values, translate container users to host users, expect errors for unmapped/overflow IDs, compare marshaled strings, and parse valid/invalid mapping strings.

## State And Persistence
Only in-memory mappings and serialized strings.

## Dependencies And Integration Points
Uses OCI runtime spec mapping structs and testify.

## Risks
Tests focus on deterministic mappings and do not cover concurrent access, because `IDMap` is not synchronized.

## Test Signals
Good coverage for mapping boundaries and serialization contracts.
