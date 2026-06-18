# sources/distributed-fs/glusterfs/xlators/features/quota/Makefile.am

## Purpose

This top-level Automake fragment delegates quota translator builds to `src`.

## Important APIs, Types, and Functions

It defines `SUBDIRS = src` and an empty `CLEANFILES` variable with trailing whitespace.

## Control Flow

The build system descends into `src` to build quota and quotad modules.

## State and Persistence Behavior

No runtime state is defined.

## Dependencies and Integration Points

It integrates with the GlusterFS feature translator build layout.

## Risks and Edge Cases

If recursion is broken, quota and quotad translators are omitted from the build. The trailing whitespace in `CLEANFILES = ` is harmless.

## Test Signals

Autotools build should recurse into `quota/src` and apply its `WITH_SERVER` gated build rules.
