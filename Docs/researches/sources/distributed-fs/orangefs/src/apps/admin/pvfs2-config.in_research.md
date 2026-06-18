# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-config.in

## Purpose
`pvfs2-config.in` is the template for the installed `pvfs2-config` shell helper. It reports OrangeFS build/install metadata such as prefix, exec-prefix, version, compiler include flags, client link flags, and server link flags.

## Important APIs, Types, And Functions
This is a shell script template using configure substitutions such as `@prefix@`, `@exec_prefix@`, `@PVFS2_VERSION@`, `@includedir@`, `@libdir@`, `@LIBS@`, `@THREAD_LIB@`, `@OPENSSL_LIB@`, transport build flags, and transport library directories. Supported options are `--prefix`, `--exec-prefix`, `--version`, `--cflags`, `--libs`, `--static-libs`, `--serverlibs`, and `--static-serverlibs`.

## Control Flow
The script rejects empty invocation, then loops over arguments. `--prefix=DIR` and `--exec-prefix=DIR` override output variables for that process. Query options echo substituted values. Link-flag options build `libflags` incrementally, adding optional GM, IB, OpenIB, RDMA, MX, Portals, and realtime libraries when configured.

## State And Persistence
It has no persistent state; overrides affect only the current process output. Its installed contents persist configure-time build decisions.

## Dependencies And Integration Points
It is consumed by downstream builds that compile/link against OrangeFS client or server libraries. It integrates with autoconf substitution and the project's transport selection options.

## Risks And Test Signals
Risks include stale or misspelled library flags, shell word-splitting of paths with spaces, `--static-libs` being identical to `--libs`, and downstream link failures if optional transport substitutions are wrong. Tests should run the installed script for every option in representative build configurations and compile a small client/server program using the emitted flags.
