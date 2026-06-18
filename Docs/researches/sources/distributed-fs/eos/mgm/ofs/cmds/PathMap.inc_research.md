# Research: sources/distributed-fs/eos/mgm/ofs/cmds/PathMap.inc

## Purpose

`PathMap.inc` implements MGM path remapping configuration. It stores source-to-target prefix mappings, optionally persists new mappings to the config engine, and translates incoming paths using the longest matching configured prefix.

## Important APIs, Types, and Functions

- `XrdMgmOfs::ResetPathMap()` clears all mappings under `PathMapMutex`.
- `XrdMgmOfs::AddPathMap(source,target,store_config)` inserts a new mapping if the source is absent and optionally calls `mConfigEngine->SetConfigValue("map", source, target)`.
- `XrdMgmOfs::PathRemap(inpath,outpath)` normalizes double slashes, appends a slash for directory-style matching, checks exact path and exact slash-appended mappings, then walks subpaths from deepest to shallowest to apply longest-prefix replacement.

## Control Flow

Reset and add take write locks. Path remap takes a read lock, initializes output to input, collapses repeated `//`, appends a slash to simplify directory-prefix matching, and returns unchanged when the map is empty or the path has no subpaths. Exact `inpath` and slash-appended mappings win before prefix matching. Prefix matching scans from the deepest subpath upward, replaces only the matching prefix, removes the temporary trailing slash, and returns.

## State and Persistence Behavior

The in-memory `PathMap` is protected by `PathMapMutex`. `AddPathMap` can persist mappings through the config engine when `store_config` is true. `PathRemap` is read-only except for its output parameter.

## Dependencies and Integration Points

Dependencies include `eos::common::Path`, `XrdOucString`, EOS RW mutexes, and the MGM config engine. Path remapping integrates into the `NAMESPACEMAP` macro used across command handlers, so changes affect nearly every path-based operation.

## Risks and Edge Cases

- Duplicate source mappings are rejected; updates require reset or separate deletion logic elsewhere.
- The matching algorithm appends/removes a slash and also tests raw `inpath`, so trailing-slash behavior needs exact coverage.
- Longest-prefix replacement is string-based; malformed source/target slashes can produce unexpected paths.
- Config persistence is optional and currently has a TODO around stop config handling.

## Test Signals

Tests should cover empty map, exact path mapping, slash-appended exact mapping, longest-prefix precedence, double-slash normalization, root/no-subpath input, duplicate add rejection, config persistence call, reset behavior, and mappings that target paths with or without trailing slashes.
