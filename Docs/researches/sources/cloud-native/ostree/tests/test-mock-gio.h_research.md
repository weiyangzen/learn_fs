<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.h -->
# sources/cloud-native/ostree/tests/test-mock-gio.h

## Purpose
`test-mock-gio.h` declares the mock GIO object types implemented in `test-mock-gio.c`.

## Important APIs, Types, And Functions
The header defines `OSTREE_TYPE_MOCK_VOLUME_MONITOR`, `OSTREE_TYPE_MOCK_VOLUME`, `OSTREE_TYPE_MOCK_DRIVE`, and `OSTREE_TYPE_MOCK_MOUNT`, plus typedefs for instance and class structs. It declares the four constructors for monitors, volumes, drives, and mounts.

## Control Flow
There is no runtime flow in the header. It provides declarations that let tests instantiate mocks and pass them through GIO interface APIs.

## State And Persistence
No state is defined here beyond opaque type declarations and constructor signatures.

## Dependencies And Integration Points
It includes GIO, GLib object headers, libglnx, and `ostree-types.h`, making the mock types available to OSTree test code without exposing implementation fields.

## Risks And Test Signals
ABI consistency with `test-mock-gio.c` matters. Passing build signals include type macros resolving, constructor prototypes matching implementation, and downstream tests compiling against the mock interfaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.h -->
