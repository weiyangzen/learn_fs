## sources/distributed-fs/openafs/src/libacl/test/Makefile.in

Purpose: this makefile builds the interactive ACL test utility.

Important targets: `all` builds `acltest`; `acltest` links `acltest.o` with `-lacl`, `-lprot`, `-lubik`, `-lrx`, `-llwp`, `-lauth`, `-lrxkad`, `-lsys`, and platform libs. `clean` removes objects, archives, binary, and core files.

State and persistence: build artifacts only.

Dependencies and integration points: relies on top-level config/LWP make fragments and library search paths pointing at `TOP_LIBDIR`, destination AFS libs, and the parent directory.

Risks: no `install` or `dest` behavior. The test requires a protection server at runtime, so a successful build is not a full behavior signal.

Test signals: successful link of `acltest`; manual interactive use verifies ACL conversion and rights checks.
