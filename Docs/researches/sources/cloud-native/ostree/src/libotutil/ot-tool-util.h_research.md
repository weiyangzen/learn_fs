# sources/cloud-native/ostree/src/libotutil/ot-tool-util.h

## Purpose
Declares small tool utility APIs for argument parsing and pointer-array search.

## Important APIs, Types, And Functions
Declares `ot_parse_boolean`, `ot_parse_keyvalue`, and `ot_ptr_array_find_with_equal_func`.

## Control Flow
No implementation flow. Consumers use these helpers in CLI parsing and compatibility logic.

## State And Persistence Behavior
No state. Declared parsers allocate output strings where applicable.

## Dependencies And Integration Points
Depends on GIO/GLib. Shared by OSTree command-line tools.

## Risks
Callers must free allocated key/value outputs and handle parser differences from keyfile boolean parsing.

## Test Signals
Compile coverage and implementation parser tests are relevant.
