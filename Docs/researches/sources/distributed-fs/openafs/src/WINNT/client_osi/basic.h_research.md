## sources/distributed-fs/openafs/src/WINNT/client_osi/basic.h

Purpose: Declares the OSI basic lock test entry point.

Important APIs/types: `main_BasicTest(HANDLE)` runs the stress test and updates a window display.

Control flow/state: No state or logic; it is a narrow interface from the Win32 test harness to `basic.c`.

Dependencies/integration: Requires `HANDLE` from Windows headers and is included by `main.c`.

Risks/tests: Compile order must define `HANDLE`. Test menu invocation and return-code display.
