# sources/distributed-fs/coda/coda-src/volutil/Makefile.am

Purpose: automake definition for Coda volume utility libraries and programs.

Important targets: under `BUILD_SERVER`, builds noinst libraries `libvolutil.la`, `libvolserv.la`, and `libdumpstuff.la`; installs/defines `volutil`, `codareaddump`, `codamergedump`, and `codadump2tar`; and distributes man pages. `libvolutil_la_SOURCES` aggregates many volume subcommands plus dump helpers. `libvolserv_la_SOURCES` provides server-side volutil RPC implementation. Program source lists define specific dump/read/merge/tar frontends.

Control flow/state: `AM_CPPFLAGS` wires include paths across base, kernel dependency, util, vicedep, dir, ACL, partition, auth, vv, lka, vol, and resolution trees with large-file flags. `*_LDADD` expresses library dependencies for each frontend, including RPC2/RVM/readline/termcap as needed.

Dependencies/integration: this is the build integration point connecting volutil commands to auth, vicedep, util, kerndep, base, vv, dir, ACL, rwcdb, and RPC/RVM libraries. Risks include duplicate dump sources in `libvolutil_la_SOURCES`, conditional server-only build coverage, and fragile dependency order. Test signals: `make` with `BUILD_SERVER`, link every program, distcheck/manpage inclusion, and targeted rebuild after changing volume/dump libraries.
