# sources/distributed-fs/glusterfs/xlators/features/quiesce/Makefile.am

## Purpose

This top-level Automake file delegates quiesce translator builds to `src`.

## Important APIs, Types, and Functions

It defines `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow

The parent build recurses into `src`.

## State and Persistence Behavior

No runtime state is defined.

## Dependencies and Integration Points

It integrates with the feature translator build tree.

## Risks and Edge Cases

If `src` is not traversed, `quiesce.la` and its generated message/memory type coverage are not built.

## Test Signals

Autotools build should enter this directory and compile `quiesce/src/quiesce.c`.
