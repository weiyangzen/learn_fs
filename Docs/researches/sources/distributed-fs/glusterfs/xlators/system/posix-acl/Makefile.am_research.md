# sources/distributed-fs/glusterfs/xlators/system/posix-acl/Makefile.am

Purpose: automake directory dispatcher for the POSIX ACL system translator. It delegates to the `src` directory where the module is built.

Important APIs, types, and functions: the build directive is `SUBDIRS = src`.

Control flow: automake recursion enters this directory from `xlators/system/Makefile.am`, then immediately enters `src` for compilation and install rules.

State and persistence: no runtime state. Build artifacts are produced by `src/Makefile.am`.

Dependencies and integration points: connects the translator's source directory to the parent GlusterFS system xlator build.

Risks and test signals: low risk except for build omission if the directive is wrong. Test signal is that `xlators/system/posix-acl/src/posix-acl.la` is reached by a normal build.
