# sources/distributed-fs/openafs/src/platform/HPUX/Makefile.in

## Purpose
Declares an empty HP-UX platform-specific support directory.

## Important APIs, Types, And Functions
The makefile exposes standard no-op targets: `all`, `install`, `dest`, and `clean`.

## Control Flow
All standard invocations return successfully without compiling or installing anything.

## State And Persistence
No state, build outputs, or destination files are generated.

## Dependencies And Integration Points
Used by the platform dispatcher when `MKAFS_OSTYPE` selects `HPUX`. HP-UX-specific behavior in nearby code is handled through conditional compilation, not this makefile.

## Risks And Test Signals
Risk is target drift if platform artifacts are later added. Test signal is that HP-UX platform dispatch remains valid and no unexpected artifacts appear.
