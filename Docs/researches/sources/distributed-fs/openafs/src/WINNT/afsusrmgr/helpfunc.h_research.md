## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/helpfunc.h

Purpose: declares user-visible help operations and application help registration.

Important APIs/types/functions: `Help_FindCommand`, `Help_FindError`, `Help_About`, and `Main_ConfigureHelp`.

Control flow: menu commands call the first three functions; startup calls `Main_ConfigureHelp` before dialogs rely on context help.

State and persistence behavior: no persistent state in the header.

Dependencies and integration points: integrates the command menu in `command.cpp`, startup in `main.cpp`, and AfsAppLib help handling throughout dialog procs.

Risks: failing to call `Main_ConfigureHelp` early leaves `AfsAppLib_HandleHelp` without registered context maps.

Test signals: verify Help menu commands and F1/context help work immediately after startup.
