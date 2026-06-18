# sources/cloud-native/ostree/src/libotutil/ot-tool-util.c

## Purpose
Implements small command/tool utility functions for parsing booleans, parsing `KEY=VALUE`, and finding entries in `GPtrArray` with a custom equality function.

## Important APIs, Types, And Functions
`ot_parse_boolean` accepts case-insensitive `1/true/yes` and `0/false/no/none`. `ot_parse_keyvalue` splits the first `=` into allocated key and value. `ot_ptr_array_find_with_equal_func` is a compatibility copy of GLib pointer-array find behavior.

## Control Flow
Boolean parsing compares the input against accepted literals and errors otherwise. Key/value parsing finds the first `=`, errors if missing, and duplicates both sides. Pointer-array search defaults to pointer equality if no equality function is provided, scans linearly, optionally writes the first matching index, and returns whether found.

## State And Persistence Behavior
No persistent state. Functions allocate returned strings for parsed key/value and only read arrays.

## Dependencies And Integration Points
Depends on GLib, GIO errors through `otutil.h`, and is used by command-line tools or compatibility code needing behavior from newer GLib.

## Risks
`ot_parse_keyvalue` permits empty keys or values because it only requires an equals sign. Boolean parser differs from `_ostree_parse_boolean` by being case-insensitive and accepting `none` as false.

## Test Signals
Tests should cover all accepted boolean spellings/cases, invalid booleans, key/value strings with missing, leading, trailing, and multiple equals signs, and pointer-array search with NULL/custom equality.
