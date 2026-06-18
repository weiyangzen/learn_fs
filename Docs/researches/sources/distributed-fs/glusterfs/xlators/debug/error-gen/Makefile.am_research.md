# sources/distributed-fs/glusterfs/xlators/debug/error-gen/Makefile.am

## Purpose
This Automake file delegates the error-gen debug translator build to its `src` directory.

## Important APIs, Types, And Functions
It sets `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow
Recursive Automake targets enter `error-gen/src`, which declares the actual xlator module.

## State And Persistence Behavior
No runtime state is managed.

## Dependencies And Integration Points
It is listed by `xlators/debug/Makefile.am` and connects that parent build to `error-gen/src/Makefile.am`.

## Risks
Omitting `src` would remove error-gen from recursive builds and packages.

## Test Signals
Recursive build output should include `error-gen.la` from the child source directory.
