# sources/distributed-fs/ceph-client/tools/perf/Makefile

Purpose: Top-level perf make entry that forwards user targets into `tools/build/Makefile.build` and perf-specific makefiles.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Normalizes output directories, includes scripts, forwards goals to `Makefile.perf`, and provides clean/install/help style targets.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel tools build infrastructure, make variables such as `O`, `OUTPUT`, `DESTDIR`, and perf sub-make files.

Risks: Output-directory normalization and recursive make variable forwarding are easy to break for out-of-tree builds.

Test signals: Build, clean, install, and help targets with in-tree and `O=` output directories.

Source coverage: researched from the complete local file (122 lines, 2830 bytes).
