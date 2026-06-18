# sources/distributed-fs/openafs/src/platform/LINUX/Makefile.in

## Purpose
Declares that Linux has no buildable platform-specific files in this `src/platform` subdirectory.

## Important APIs, Types, And Functions
Defines no-op `all`, `install`, `dest`, and `clean` targets.

## Control Flow
The platform dispatcher can enter `LINUX` and run standard make targets without producing artifacts.

## State And Persistence
No files are generated or installed.

## Dependencies And Integration Points
This is selected by `src/platform/Makefile.in` for Linux platform dispatch. Linux-specific OpenAFS behavior is elsewhere in the source tree.

## Risks And Test Signals
Risk is only future drift if platform files are introduced here. Test signal is no-op success during Linux builds.
