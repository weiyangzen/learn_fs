# sources/distributed-fs/glusterfs/xlators/performance/open-behind/Makefile.am

Purpose: top-level Automake fragment for the `open-behind` translator directory.

Important APIs, types, and functions: declares `SUBDIRS = src`; no C APIs.

Control flow: recursive build descends into `src` to compile the translator module.

State and persistence: build-only metadata with no runtime state.

Dependencies and integration: depends on the `src` subdirectory and parent Automake recursion.

Risks and test signals: low risk; recursive build and dist packaging should confirm the directory is included.
