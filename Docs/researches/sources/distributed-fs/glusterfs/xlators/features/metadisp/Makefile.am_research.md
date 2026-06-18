# sources/distributed-fs/glusterfs/xlators/features/metadisp/Makefile.am

## Purpose

This top-level Automake fragment makes `metadisp/src` the build subdirectory for the metadisp feature translator.

## Important APIs, Types, and Functions

The only build variables are `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow

Automake descends into `src` during build, install, clean, and distribution phases.

## State and Persistence Behavior

No runtime state or persistent data is defined here.

## Dependencies and Integration Points

It depends on the parent GlusterFS build system discovering feature translator subdirectories. All actual library, generated-source, include, and clean rules are delegated to `src/Makefile.am`.

## Risks and Edge Cases

If `src` is omitted or renamed, the metadisp translator is not built even though the source remains present. The empty `CLEANFILES` means generated artifacts must be cleaned in the nested makefile.

## Test Signals

Autotools configuration and `make` should recurse into this directory and build `metadisp.la` through the nested makefile.
