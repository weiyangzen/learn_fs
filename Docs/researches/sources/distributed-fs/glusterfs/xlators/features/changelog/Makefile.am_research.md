# sources/distributed-fs/glusterfs/xlators/features/changelog/Makefile.am

Purpose: this Automake file declares the top-level changelog feature subdirectories.

Important declarations: `SUBDIRS = src lib` builds both the changelog xlator source and the changelog client library. `CLEANFILES` is empty.

Control flow and state: no runtime logic or persistent state is present. The file controls build traversal order and inclusion in distribution builds.

Dependencies and integration points: the `lib` subdirectory contains `libgfchangelog`, which bitrot daemon uses through `gf_changelog_register_generic`. The `src` subdirectory contains the changelog feature xlator implementation referenced by library includes.

Risks: omitting either subdirectory breaks either server changelog support or external/library consumers. Build-system tests should catch accidental subdirectory removal.

Test signals: run Automake/configure builds and verify both changelog xlator and `libgfchangelog` targets are visited.
