# sources/distributed-fs/glusterfs/xlators/performance/quick-read/Makefile.am

Purpose: top-level Automake fragment for `quick-read`.

Important APIs, types, and functions: declares `SUBDIRS = src` and an empty `CLEANFILES`.

Control flow: recursive build enters `src` for actual module compilation.

State and persistence: build-only metadata.

Dependencies and integration: relies on parent Automake recursion and the `src` directory.

Risks and test signals: low risk; validate with recursive build and dist checks.
