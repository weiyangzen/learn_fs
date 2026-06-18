# sources/distributed-fs/glusterfs/xlators/features/cloudsync/Makefile.am

## Purpose
Top-level Automake file for the `cloudsync` feature translator directory. It delegates all real build work to `src`.

## Important APIs, types, and functions
No code APIs are declared. The build API is `SUBDIRS = src`, with an empty `CLEANFILES`.

## Control flow
During recursive Automake builds, this directory enters `src`, where the translator, generated fops, shared common code, and plugin subdirectories are built.

## State and persistence behavior
No runtime state or generated artifacts are produced here directly.

## Dependencies and integration points
Integrates the cloudsync subtree into the larger GlusterFS recursive build. Its only dependency is the existence of `src/Makefile.am`.

## Risks and test signals
Risk is low. Build validation should confirm recursive make enters `xlators/features/cloudsync/src` and that clean/install targets are handled by deeper Makefiles.
