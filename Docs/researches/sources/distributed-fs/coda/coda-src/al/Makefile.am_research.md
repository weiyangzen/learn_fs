<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/Makefile.am -->
# sources/distributed-fs/coda/coda-src/al/Makefile.am

Purpose: Automake definition for Coda's access-list/protection database support library and `pdbtool`.

Important APIs, types, and functions: Under `BUILD_SERVER`, builds `libal.la`, installs/declares `pdbtool` as an sbin program, and distributes `pdbtool.8`. Headers include `al.h`, `prs.h`, `pdb.h`, and `pdbarray.h`. Library sources include `pdbdb.c`, `pdbpack.c`, `alprocs.c`, `pdb.c`, `pdbprofile.c`, and `pdbarray.c`, with `pdbdb.c` and `pdbpack.c` listed twice. `AM_CPPFLAGS` adds RPC2, base, rwcdb, and util include paths. `LDADD` links local libal, util, rwcdb, base, readline, and termcap.

Control flow: Server builds compile the internal access-list library and pdb management tool; non-server builds still expose header lists but do not build the server-only artifacts.

State and persistence: No runtime state here. The compiled library/tool operate on Coda protection database state elsewhere.

Dependencies and integration points: Integrates access-list code with util, base, rwcdb, RPC2, readline, and termcap libraries. `pdbtool` is the administrative interface to protection database data.

Risks and test signals: Duplicate source entries may cause redundant compilation or Automake warnings depending on toolchain. Conditional build paths should be tested with `BUILD_SERVER` enabled and disabled. Link tests should validate readline/termcap and internal library ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/Makefile.am -->
