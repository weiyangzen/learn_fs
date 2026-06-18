# sources/distributed-fs/glusterfs/xlators/debug/Makefile.am

## Purpose
This Automake file lists debug translators built under `xlators/debug`.

## Important APIs, Types, And Functions
It sets `SUBDIRS = error-gen io-stats sink trace delay-gen`, causing those child directories to participate in recursive builds, and declares an empty `CLEANFILES`.

## Control Flow
Automake recursively enters the listed subdirectories in order during build, install, clean, and related targets.

## State And Persistence Behavior
No runtime state is managed. The file affects build outputs installed for debug translators.

## Dependencies And Integration Points
It integrates with the top-level GlusterFS Automake build and the per-translator `Makefile.am` files in each debug child directory.

## Risks
Removing a subdirectory drops that translator from builds; ordering can matter if generated files or install paths have hidden assumptions. Empty `CLEANFILES` is benign.

## Test Signals
`make`, `make distcheck`, and packaging manifests should confirm all expected debug xlators are built and installed.
