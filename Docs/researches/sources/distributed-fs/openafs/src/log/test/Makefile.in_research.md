## sources/distributed-fs/openafs/src/log/test/Makefile.in

Purpose: Builds legacy test programs for AFS token and authentication interfaces.

Important targets and variables: `LDIRS`, `LIBS`, `all`, `testlog`, `gettoktest`, `clean`, `install`, and `dest`.

Control flow: Includes config and LWP make settings, then builds `testlog` and `gettoktest` with `AFS_LDRULE` against auth, rxkad, des, sys, rx, lwp, cmd, afsutil, and platform extra libs. Install and dest are intentionally empty.

State and persistence: Produces test binaries in the test directory. Running those binaries can modify token state, but the makefile itself only builds.

Dependencies and integration: Uses legacy libraries and LWP runtime rather than pthread make config. Invoked by `src/log/Makefile.in` target `test`.

Risks: Library names are old-style `-lauth -lrxkad -ldes` and depend on `TOP_LIBDIR` and `DESTDIR` search order. Empty install/dest means tests are build-tree tools only.

Test signals: `make -C src/log/test`, link success, clean removes binaries, and runtime tests in a controlled AFS environment.
