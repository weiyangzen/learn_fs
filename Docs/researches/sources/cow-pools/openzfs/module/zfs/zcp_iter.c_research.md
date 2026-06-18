# File Research: sources/cow-pools/openzfs/module/zfs/zcp_iter.c

## Summary
Implements the `zfs.list` Lua submodule for channel programs. It returns iterator closures for children, snapshots, clones, user properties, system properties, bookmarks, and holds.

## Main Responsibilities
- Iterates clones of a snapshot.
- Iterates snapshots of a filesystem or volume.
- Iterates child datasets while skipping hidden names.
- Iterates user properties and the compatibility alias `properties`.
- Returns visible valid system-property names.
- Iterates bookmarks on a dataset.
- Iterates holds on a snapshot.
- Registers list functions and metatables into Lua.

## Key APIs
- `zcp_load_list_lib()`
- Internal iterator factories: `zcp_children_list()`, `zcp_snapshots_list()`, `zcp_clones_list()`, `zcp_user_props_list()`, `zcp_system_props_list()`, `zcp_bookmarks_list()`, `zcp_holds_list()`

## Important Behavior
Each list call validates arguments, captures an object id and serialized cursor in Lua upvalues, and returns a closure. Each invocation advances the cursor and returns the next item or no values at end.

`user_properties` materializes all properties into an nvlist and attaches a Lua `__gc` metatable so the nvlist is freed if iteration does not run to completion.

`system_properties` returns a Lua table of names for visible system properties valid for the requested dataset.

## State and Lifetime
Iterators repeatedly re-hold datasets by object id, so they tolerate object lifetime checks at each step. User property iteration stores an nvlist pointer in Lua userdata and frees it either at exhaustion or garbage collection.

## Risks
Datasets can disappear between iterator creation and iteration, producing either empty iteration or fatal errors depending on context. Cursor values are held as Lua numbers. User-property iteration depends on `fnvpair_value_nvlist()` containing `ZPROP_VALUE` and `ZPROP_SOURCE`.
