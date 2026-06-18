# sources/distributed-fs/glusterfs/xlators/features/selinux/Makefile.am

## Purpose
This Automake fragment is the top-level build entry for the `features/selinux` translator directory. It delegates all build work to `src`.

## Important APIs and control flow
`SUBDIRS = src` makes recursive Automake enter `xlators/features/selinux/src`. `CLEANFILES =` is present but empty, so the parent directory contributes no generated cleanup targets.

## State, dependencies, and integration
There is no runtime state. The file integrates the SELinux translator into the larger GlusterFS recursive build by making the `src/Makefile.am` visible from the feature directory.

## Risks and test signals
The main risk is omission: if `src` is removed or renamed, the SELinux translator will silently stop building from this branch. Build validation should run autoreconf/configure or the project build system and confirm `selinux/src` is traversed.
