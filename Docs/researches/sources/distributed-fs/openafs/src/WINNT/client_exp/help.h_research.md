## sources/distributed-fs/openafs/src/WINNT/client_exp/help.h

Purpose: Centralizes help-file names, WinHelp command type, help context IDs, and the two help API declarations used by dialogs.

Important APIs/types: Defines `HELPFILE_NATIVE`, `HELPFILE_LIGHT`, `HELPTYPE`, and context IDs for authentication, tokens, ACLs, volumes, partition info, mount points, server status, submounts, and symlinks. Declares `SetHelpPath` and `ShowHelp`.

Control flow/state: No runtime logic; IDs here must match localized `.hlp` content and dialog handlers.

Dependencies/integration: Included via `stdafx.h`, so most client-exp modules see the help API. Resource and help authoring must remain synchronized.

Risks/tests: Duplicate or stale IDs route users to wrong pages; `DOWN_SERVERS_HELP_ID` intentionally aliases another ID. Test every `IDHELP` button and ensure native/light help files contain the declared contexts.
