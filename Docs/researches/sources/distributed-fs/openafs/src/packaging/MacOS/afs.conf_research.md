# sources/distributed-fs/openafs/src/packaging/MacOS/afs.conf

Purpose: shell-style default OpenAFS client configuration for Mac packaging, used when `afsd.options` does not override it.

Important APIs/types/functions: defines variables consumed by launch scripts: `VERBOSE`, `OPTIONS`, `AFS_SYSNAME`, `AFS_PRECACHE`, `AFS_POST_INIT`, and `AFS_PRE_SHUTDOWN`. Comments document many `afsd` flags and optional hook functions.

Control flow: no executable control flow besides optional user-defined shell functions in comments. Launch scripts source or parse these variables to start/shutdown the client.

State and persistence: installed as a sample/default config under `/var/db/openafs/etc/config`. Users may edit derived copies.

Dependencies/integration: used by Mac `openafs.launchdaemon`/launch scripts and `afsd`. The default `OPTIONS` enables dynamic root, fakestat, AFSDB, cache/stat sizing, daemons, volumes, and chunksize.

Risks and test signals: comments mention Linux for sysname despite Mac location, suggesting copied documentation. Defaults may be stale for modern clients. Test signal is successful client launch with expected afsd flags and optional hook behavior.
