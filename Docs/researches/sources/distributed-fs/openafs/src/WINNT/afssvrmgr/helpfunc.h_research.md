# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/helpfunc.h

## Purpose
`helpfunc.h` declares the Server Manager help and About entry points.

## Important APIs, Types, And Functions
It exposes `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`.

## Control Flow
No header logic exists. Menu handlers call the first three functions to open modal dialogs; application startup calls `Main_ConfigureHelp` to bind dialog/control IDs to help topics.

## State And Persistence
No state is declared here. Implementation state is static in `helpfunc.cpp` and AfsAppLib's help registry.

## Dependencies And Integration Points
The header is consumed by menu and startup code in the Win32 GUI. It depends on the broader application headers for Win32 and TCHAR definitions.

## Risks And Test Signals
Risks are limited to declaration/implementation drift. Compile coverage plus menu invocation of each help function validates the contract.
