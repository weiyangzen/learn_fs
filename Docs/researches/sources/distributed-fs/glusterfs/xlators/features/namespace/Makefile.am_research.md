# sources/distributed-fs/glusterfs/xlators/features/namespace/Makefile.am

## Purpose

This top-level Automake fragment delegates namespace translator builds to `src`.

## Important APIs, Types, and Functions

It defines `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow

The build system recurses into the `src` directory.

## State and Persistence Behavior

No runtime or persistent state is defined.

## Dependencies and Integration Points

It integrates with the parent feature translator build layout.

## Risks and Edge Cases

If this file is not included by the parent makefile or `src` is removed, `namespace.la` will not be built.

## Test Signals

Autotools build should enter this directory and compile `namespace/src/namespace.c`.
