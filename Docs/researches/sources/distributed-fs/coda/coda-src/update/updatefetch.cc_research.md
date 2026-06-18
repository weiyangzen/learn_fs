# sources/distributed-fs/coda/coda-src/update/updatefetch.cc

Purpose: one-shot client to fetch a single file from an SCM `updatesrv` using the same update RPC and token mechanism as `updateclnt`.

Important functions: `ReadConfigFile` initializes the configured `vicedir`. `ProcessArgs` requires `-h server`, `-r remote`, and `-l local`, with optional debug and port. `U_InitRPC` initializes LWP/RPC2/SFTP. `Connect` binds to `SUBSYS_UPDATE` on `codasrv-se/udp` or explicit port using `db/update.tk` and AUTHONLY/XOR. `FetchFile` opens a SmartFTP `FILEBYNAME` side effect to `LocalFileName`, calls `UpdateFetch` with time zero to force transfer, and unlinks the local file on failure. `main` creates/truncates the local file before fetching.

State/persistence: writes the requested local file and may delete it on transfer error. It reads server config and update token.

Dependencies, risks, tests: depends on RPC2/SFTP, generated update client stubs, token secret, and writable local path. Risks include truncating/creating the local destination before successful fetch, fixed-size host/filename copies, no parent-directory creation, and no atomic temp/rename behavior unlike `updateclnt`. Test successful fetch, auth failure, missing token, remote missing, local unwritable path, explicit port, and preserving existing local file on failure if behavior is changed.
