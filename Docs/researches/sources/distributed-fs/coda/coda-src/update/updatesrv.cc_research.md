# sources/distributed-fs/coda/coda-src/update/updatesrv.cc

## Purpose
`updatesrv.cc` is the Coda update server daemon. It listens on the update RPC2 subsystem, authenticates clients with the shared `db/update.tk` token, checks whether requested server database/configuration files have changed, and transfers changed regular files back to callers with RPC2 SmartFTP side effects.

## Important APIs, Types, And Functions
The daemon entry point is `main()`, with setup helpers `ReadConfigFile()` and `ReadExportList()`. `flist`, `namelist`, `checknames`, `InList()`, and `AccessAllowed()` implement the optional `db/files.export` allowlist and reject pathnames containing `..`. RPC callbacks include `Update_GetKeys()`, `Update_AuthFail()`, `UpdateNewConnection()`, and service method `UpdateFetch()`. `ServerLWP()` is the worker loop that calls `RPC2_GetRequest()` and dispatches `update_ExecuteRequest()`.

## Control Flow
Startup parses `-d`, `-l`, `-port`, and `-p`, loads `server.conf`, initializes `vice_config_path()` from `vicedir`, reads exported names, creates `misc`, detaches, redirects logs, changes to the serving prefix, writes `updatesrv.pid`, initializes LWP/RPC2/SFTP, exports `SUBSYS_UPDATE`, and spawns worker LWPs. Each worker waits for authenticated RPC2 requests, rejects open-kimono peers, executes update RPCs, logs failures, and unbinds bad connections. `UpdateFetch()` copies the requested name into a bounded buffer, checks access, stats the file, reports current server time, and only starts a SmartFTP server-to-client transfer when the file is regular and the caller's mtime differs.

## State And Persistence
Persistent external state is the Coda server tree under `vicedir`, especially `db/files.export`, `db/update.tk`, `misc/UpdateSrvLog`, and `misc/updatesrv.pid`. In-process state includes the export-name linked list, `prefix`, debug levels, token cache inside `secret_state`, and RPC2/LWP worker state. The daemon does not persist request history.

## Dependencies And Integration Points
This file integrates Coda's config layer, `vice_file` path construction, `getsecret`, RPC2, SmartFTP, LWP, service lookup, `update.h` generated stubs, and libutil logging/detach helpers. It is part of the server-to-server database update channel.

## Risks
Access control depends on a flat exact-name export list; if `files.export` is absent, all names under the working prefix are allowed. Path rejection only searches for adjacent dots and should not be treated as a full canonicalization layer. Worker creation passes the address of loop variable `i`, so logged worker ids can race. Token caching is mtime-based and the shared `secret_state` is static across workers. SmartFTP failures below `RPC2_ELIMIT` force unbinds, so transport errors can terminate sessions.

## Test Signals
Exercise startup with explicit/default ports, missing and populated `db/files.export`, bad and good `update.tk`, allowed and denied names, unchanged mtimes, changed regular files, missing files, `..` paths, multiple LWP workers, unauthenticated peers, SIGHUP/SIGUSR1/SIGQUIT behavior, and successful SmartFTP transfer completion.
