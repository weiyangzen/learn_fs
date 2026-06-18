# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.cpp

Purpose: parses AFS Account Manager command-line switches, connects to an admin server, optionally sets credentials, and optionally opens a cell without showing the normal cell dialog.

Important APIs/functions: `ParseCommandLine` recognizes `/cell`, `/remote`, `/user`, and `/password` with values. It validates duplicate/unknown/missing values, enforces user/password pairing, opens a remote or local admin server with `AfsAppLib_OpenAdminServer`, stores `g.idClient`, applies credentials through `AfsAppLib_SetCredentials`, and starts `taskOPENCELL` when `/cell` is supplied. `CommandLineHelp` formats syntax errors through `vMessage`.

Control flow: parsing walks the raw command line manually, supporting `-` or `/`, `:` or whitespace before values, and quoted values. Errors return `opCLOSEAPP`. Successful `/cell` dispatch returns `opNOCELLDIALOG`; otherwise normal startup continues.

State and persistence: static `aSWITCHES` is reset for presence each parse but retains value buffers overwritten as switches are found. Global `g.idClient` is set after admin-server connection, and credentials may update the admin-server session.

Dependencies/integration: uses `TaAfsUsrMgr.h`, `cmdline.h`, `AfsAppLib`, admin error constants, message resources, and Account Manager `taskOPENCELL`.

Risks: values are copied into fixed `cchRESOURCE` buffers without explicit bounds during parsing, so very long arguments can overflow. Static switch values are not cleared when absent, though presence flags control use. Passwords are stored in process memory as plain text. Tests should cover quoting, duplicate switches, missing values, remote/local failures, credential pairing, and long argument rejection/fuzzing.
