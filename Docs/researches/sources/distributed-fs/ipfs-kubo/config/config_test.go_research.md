# Research: sources/distributed-fs/ipfs-kubo/config/config_test.go

Purpose: Tests config cloning, reflection-to-map shape, and key validation.

Important APIs/types/functions: `TestClone`, `TestReflectToMap`, and `TestCheckKey`.

Control flow, state, and persistence: Tests use in-memory `Config` values. `TestClone` mutates the original after cloning to confirm map slices are not shared. `TestReflectToMap` checks representative struct, slice, map, pointer, string, int64, and bool conversions. `TestCheckKey` validates accepted nested/dynamic config paths and rejected unknown fields.

Dependencies and integration points: Directly exercises `Config.Clone`, `ReflectToMap`, and `CheckKey`, which support `ipfs config` command validation.

Risks and test signals: The reflection test checks selected fields, not the entire schema. It does not exercise all dynamic maps. It is useful for catching regressions in validation of `Provide.*`, gateway public gateway dynamic keys, and plugin config dynamic keys.
