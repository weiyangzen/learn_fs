# sources/distributed-fs/openafs/src/kauth/admin_tools.c

Purpose: implements the `kas` administrative command engine for Authentication Server database inspection, user management, password/key operations, server statistics/debugging, ticket cache helpers, and interactive mode.

Important APIs and functions: exported `ka_AdminInteractive`; command handlers `ListUsers`, `ExamineUser`, `CreateUser`, `DeleteUser`, `SetFields`, `Unlock`, `StringToKey`, `SetPassword`, `GetRandomKey`, `Statistics`, `DebugInfo`, `ForgetTicket`, and `ListTickets`; setup hooks `MyBeforeProc`/`MyAfterProc`; helpers `DefaultCell`, `DumpUser`, `handle_errors`, `parse_flags`, `ka_islocked`, `PrintName`, `PrintedName`, and `ListTicket`.

Control flow and state: global state includes current Ubik `conn`, selected `cell`, `whoami`, admin `passwd`, command name, interactive `finished`, cached startup argv, chosen admin principal, `noauth`, and explicit server list. `ka_AdminInteractive` registers command syntax and aliases, installs before/after hooks, dispatches initial argv, then optionally loops reading `ka> ` commands. `MyBeforeProc` derives identity/cell/server options, obtains or prompts for admin credentials, fetches admin/auth tokens, connects to the AuthServer maintenance service, and auto-prompts missing password parameters. `MyAfterProc` destroys `conn` after each command.

Dependencies and integration: uses Ubik/RX/RXKAD, token cache APIs, kauth protocol stubs, command parser, DES/hcrypto, password validation child helpers from `kkids`, and com_err.

Risks: security-sensitive legacy DES password handling; password strings live in global/static buffers and command items; hidden commands can print raw keys; retry/error handling varies by command; many fixed-size string copies rely on protocol maximums. Test signals should cover authenticated and `-noauth` connections, explicit server lists, all user lifecycle commands, lockout field packing, token listing/forgetting, password prompt flows, and cleanup of Ubik connections after failures.
