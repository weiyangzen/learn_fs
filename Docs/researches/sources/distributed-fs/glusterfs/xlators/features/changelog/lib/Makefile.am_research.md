# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/Makefile.am

Purpose: this Automake file declares the changelog library subdirectory build.

Important declarations: `SUBDIRS = src` sends the build into the library source directory. `CLEANFILES` is empty.

Control flow and state: no runtime behavior. This is a thin build routing file.

Dependencies and integration points: it ensures `xlators/features/changelog/lib/src` participates in the build, producing `libgfchangelog.la` and related headers used by examples and by bitrot's changelog integration.

Risks: low, but accidental changes can silently exclude the library from builds while leaving the xlator itself intact.

Test signals: distribution and recursive make targets should confirm the `src` directory is entered.
