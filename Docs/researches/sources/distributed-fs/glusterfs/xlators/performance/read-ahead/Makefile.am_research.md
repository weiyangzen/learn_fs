# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/Makefile.am

Purpose: top-level Automake fragment for the `read-ahead` performance translator.

Important APIs, types, and functions: declares `SUBDIRS = src` and an empty `CLEANFILES`.

Control flow: recursive build descends to `src` where the module is built.

State and persistence: build-only metadata.

Dependencies and integration: depends on the `src` subdirectory and parent build recursion.

Risks and test signals: low risk; recursive build and packaging checks should ensure this translator remains included.
