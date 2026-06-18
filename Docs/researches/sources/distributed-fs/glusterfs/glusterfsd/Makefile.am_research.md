# sources/distributed-fs/glusterfs/glusterfsd/Makefile.am

Purpose: Automake directory dispatcher for the GlusterFS daemon subtree. It delegates all actual daemon build rules to `glusterfsd/src`.

Important build declarations: `SUBDIRS = src` makes the `src` directory participate in recursive Automake targets. `CLEANFILES =` is empty, so this level contributes no generated cleanup artifacts.

Control flow: During configure-generated make execution, standard recursive targets (`all`, `install`, `clean`, etc.) enter `src` in order. This file has no conditional logic.

State and persistence: No runtime state and no generated files at this level. Persistent installation behavior is defined in `src/Makefile.am`.

Dependencies and integration: Integrates with the top-level GlusterFS Automake hierarchy by exposing `glusterfsd/src` as a subdirectory. It assumes the top-level configure files define the usual recursive Automake environment.

Risks: Low technical risk. If future files are added at this directory level, they will not be built or cleaned until this file gains explicit rules.

Test signals: Build-system validation is the signal: `make`, `make install`, and `make distcheck` should traverse into `src`.
