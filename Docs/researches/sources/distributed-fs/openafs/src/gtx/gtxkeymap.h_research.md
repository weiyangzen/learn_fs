# sources/distributed-fs/openafs/src/gtx/gtxkeymap.h

Purpose: defines a small trie-like keymap system for GTX keyboard command dispatch.

Important APIs and types: `KEYMAP_NENTRIES` is 256; entries are `KEYMAP_EMPTY`, `KEYMAP_PROC`, or `KEYMAP_SUBMAP`. `struct keymap_entry` stores a command name, function pointer or submap, and rock. `struct keymap_map` contains a refcount field and 256 entries. `struct keymap_state` tracks the initial and current map. Public functions create, bind, delete, initialize, process, reset, and duplicate strings.

Control flow and state: multi-character bindings are represented by nested `keymap_map` submaps. `keymap_state.currentMap` advances into submaps until a final procedure executes or a missing entry resets state.

Dependencies and integration: frames own one keymap and one state; input server feeds keycodes into `keymap_ProcessKey`; tests bind printable keys and escape-prefixed sequences.

Risks: the exposed refcount is unused by the implementation, and deleting recursively assumes exclusive ownership of submaps. Key values outside 0..255 are rejected. Test signals should cover duplicate binding replacement, deletion by binding a `NULL` proc, submap teardown, and invalid key input.
