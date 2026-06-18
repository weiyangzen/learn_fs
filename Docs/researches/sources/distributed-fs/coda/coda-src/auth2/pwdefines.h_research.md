# sources/distributed-fs/coda/coda-src/auth2/pwdefines.h

## Purpose
Small shared header defining initialization mode constants for the auth2 password support layer.

## APIs, Types, and Functions
Defines `PWFIRSTTIME` as `0` and `PWNOTFIRSTTIME` as `1`, guarded by `_PWDEFINES_H`.

## Control Flow, State, and Persistence
No control flow or runtime state. The constants drive `InitPW()` behavior in `pwsupport.c`: first-time initialization seeds globals and allocates the password array, while later reloads refresh from disk.

## Dependencies and Integration
Included by `pwsupport.c` and any code that needs to call `InitPW()` with the correct mode.

## Risks and Test Signals
Risk is limited to API clarity: raw integer constants make accidental inversion possible. Test signals are successful first auth-server startup and password-file reload when mtime changes.
