# sources/distributed-fs/openafs/src/kauth/kas.c

## Purpose
Implements the `kas` administrative command entry point. It initializes kauth client state and dispatches into the interactive/admin command implementation.

## Important APIs, Types, And Functions
The only function is `main`. It initializes multiple OpenAFS error tables, optional Windows socket support, calls `ka_Init`, and dispatches to `ka_AdminInteractive`.

## Control Flow
After platform setup and error-table initialization, `main` skips `ka_Init` for help/version/apropos-style invocations. It then rewrites the argument vector when no subcommand, cell/server/noauth/admin/password options, or a principal-looking first argument indicate the implicit `interactive` command. Otherwise it passes the original argv to `ka_AdminInteractive`, finalizes Rx, and exits based on the returned code.

## State And Persistence
The file stores no durable state. It initializes client-side kauth/Rx state and may cause downstream admin commands to mutate the KA database.

## Dependencies And Integration Points
It depends on command parsing and admin implementation in `admin_tools.c`, client initialization from the kauth library, Rx finalization, and platform-specific Windows socket setup.

## Risks And Test Signals
Risks are argument rewriting edge cases, failure to initialize cell info before real commands, and inherited security risk from password arguments passed to downstream admin tooling. Test signals include help/version without cell config, implicit interactive behavior, explicit subcommand dispatch, principal/cell option handling, Windows winsock failure handling, and clean `rx_Finalize`.
