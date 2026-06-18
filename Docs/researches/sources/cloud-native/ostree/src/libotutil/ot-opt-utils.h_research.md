# sources/cloud-native/ostree/src/libotutil/ot-opt-utils.h

## Purpose
Declares the command-line usage error helper.

## Important APIs, Types, And Functions
Declares `ot_util_usage_error(GOptionContext *context, const char *message, GError **error)`.

## Control Flow
No runtime flow in the header.

## State And Persistence Behavior
No state. The declared function writes to stderr and sets an error.

## Dependencies And Integration Points
Depends on GIO/GLib option types. Included by CLI code using `GOptionContext`.

## Risks
The API is void, so callers cannot chain it in boolean-returning expressions without custom handling.

## Test Signals
Compile and CLI behavior tests cover the header.
