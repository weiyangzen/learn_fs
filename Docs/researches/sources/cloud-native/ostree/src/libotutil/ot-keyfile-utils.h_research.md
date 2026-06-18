# sources/cloud-native/ostree/src/libotutil/ot-keyfile-utils.h

## Purpose
Declares keyfile parsing helpers and the `OtTristate` enum.

## Important APIs, Types, And Functions
Defines `OtTristate` values `OT_TRISTATE_NO`, `OT_TRISTATE_MAYBE`, and `OT_TRISTATE_YES`. Declares boolean/tristate parsers, defaulted keyfile getters, flexible string-list getters, and `ot_keyfile_copy_group`.

## Control Flow
No implementation flow. The declarations describe helper behavior used by config-loading code.

## State And Persistence Behavior
No state in the header. Declared functions allocate returned strings/lists and may mutate `GKeyFile` parser settings.

## Dependencies And Integration Points
Depends on GIO/GLib. Integrated by otcore prepare-root and broader libostree config consumers.

## Risks
Enum value ordering can matter if persisted or compared numerically. Ownership of returned strings/lists must be followed by callers.

## Test Signals
Compile coverage plus implementation parse/default tests are sufficient.
