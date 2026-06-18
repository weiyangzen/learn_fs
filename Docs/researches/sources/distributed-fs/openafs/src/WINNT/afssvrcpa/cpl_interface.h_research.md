<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.h

## Purpose
Declares the Control Panel applet entry point with C linkage.

## Important APIs, Types, And Functions
Declares `LONG APIENTRY CPlApplet(HWND, UINT, LONG, LONG)`.

## Control Flow
No runtime flow; the Control Panel host calls the exported function.

## State And Persistence
No state declared.

## Dependencies And Integration Points
Requires Windows API types; implemented by `cpl_interface.cpp`.

## Risks And Edge Cases
The old `LONG` parameter signature should be reviewed for pointer-sized portability.

## Test Signals
Export discovery and Control Panel loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.h -->
