# sources/distributed-fs/glusterfs/xlators/system/Makefile.am

Purpose: automake directory dispatcher for GlusterFS system translators. It declares `posix-acl` as the only subdirectory in this source snapshot.

Important APIs, types, and functions: the only build directive is `SUBDIRS = posix-acl`, which makes automake descend into the POSIX ACL translator subtree during build, install, clean, and distribution targets.

Control flow: top-level xlator build recursion enters `xlators/system`, reads this file, and delegates all work to `xlators/system/posix-acl`.

State and persistence: no runtime state. Persistent build/install effects are produced by the subdirectory makefiles.

Dependencies and integration points: integrates the `posix-acl` module into GlusterFS's automake build hierarchy. Removing or changing this entry would detach the system ACL translator from normal builds.

Risks and test signals: the file is intentionally minimal, but stale `SUBDIRS` entries would break builds or omit translators. Test signal is a full autotools build where the `posix-acl` subdirectory is visited.
