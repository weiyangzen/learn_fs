<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-functions.h

## Purpose
Declares shared admin helper APIs used by multiple command implementations.

## Important APIs and Types
Exposes booted-or-os validation, checksum version extraction, indexed deployment lookup, sysroot locking, and guarded reboot exec.

## Control Flow
No implementation is present; functions follow standard GLib boolean/error or returned-object conventions.

## State and Persistence
The header stores no state. Declared functions may read deployment metadata, acquire locks, or exec reboot.

## Dependencies and Integration Points
Includes `ot-main.h` for OSTree/GLib command context types. Used across admin builtins.

## Risks
Callers must respect ownership of returned strings and deployment refs. Functions that may exec or block on locks should be used only in command paths where that behavior is expected.

## Test Signals
Compile/link tests and the implementation tests for each declared helper cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.h -->
