# sources/cloud-native/containers-storage/jsoniter.go

## Purpose
This file centralizes JSON encoding/decoding for the `storage` package by assigning package variable `json` to `jsoniter.ConfigCompatibleWithStandardLibrary`.

## Important API
The exported surface is intentionally absent; the package-level variable is used internally as a drop-in replacement for the standard `encoding/json` API. In the researched files, `layers.go` uses `json.Unmarshal`, `json.Marshal`, and `json.NewDecoder` via this variable for layer metadata and additional layer info.

## Control Flow and State
There is no control flow beyond initialization. Runtime behavior depends on jsoniter's standard-library-compatible configuration. Persistent effects show up in files such as `layers.json`, `volatile-layers.json`, `mountpoints.json`, and additional-layer metadata, all written/read through package-level JSON calls.

## Dependencies and Integration Points
The dependency is `github.com/json-iterator/go`. The integration point is broad: all files in package `storage` that refer to `json` bind to this variable, not to an imported standard package.

## Risks and Edge Cases
Because this shadows the conventional package name, maintainers must remember that `json` is a variable. Compatibility with standard JSON is intended, but subtle differences in jsoniter behavior could affect persistent metadata compatibility.

## Test Signals
There is no direct test for this file. Indirect coverage comes from any storage tests that read/write JSON metadata, including the layer location tests and broader store tests outside this subset.
