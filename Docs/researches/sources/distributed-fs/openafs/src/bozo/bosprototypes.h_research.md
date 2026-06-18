# sources/distributed-fs/openafs/src/bozo/bosprototypes.h

`bosprototypes.h` centralizes internal prototypes shared by bosserver, bnode operation modules, and bos RPC procedures. It exposes the bnode management surface, bosserver helpers, bosoprocs helpers, and an inline key-structure cast.

Important declarations include `bnode_*` instance/process operations, `bozo_ReBozo`, `WriteBozoFile`, pid-file helpers, restricted-mode getters/setters, `GetRequiredDirPerm`, `bozo_ShutdownAndExit`, `initBosEntryStats`, and `DirAccessOK`. `ktc_to_bozoptr` casts a `ktc_encryptionKey` to the wire `bozo_key` structure used by bos RPCs.

This header has no runtime control flow or persistence, but it fixes cross-module contracts that affect `BosConfig` persistence, process supervision, pid files, and RPC key handling. Dependencies are `rx/rxkad.h` and types from included bnode/bos headers in consumers.

Risks are ABI/API drift between prototypes and implementation, especially for pointer ownership (`char **` outputs), lock preconditions (`WriteBozoFile`, `DirAccessOK`), and the inline cast assuming layout compatibility. Test signals are compile-time: all bozo objects must build with warnings enabled, and callers should be checked for lock and allocation ownership conventions.
