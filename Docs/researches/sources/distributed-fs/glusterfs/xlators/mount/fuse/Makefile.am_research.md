# sources/distributed-fs/glusterfs/xlators/mount/fuse/Makefile.am

## Purpose

This Automake file is the dispatcher for the FUSE mount translator subtree. It always recurses into `src` and `utils`, separating the translator library build from helper utilities.

## Important Build Variables

- `SUBDIRS = src utils` defines the recursive build order for the FUSE subtree.
- `CLEANFILES` is present but empty.

## Control Flow and Integration

When the parent mount `Makefile.am` includes the `fuse` directory, Automake enters this file and then builds `src` followed by `utils`. The `src` subdirectory builds `fuse.la`, the mount translator module; `utils` is expected to build related command-line or support utilities.

## State and Persistence Behavior

This file has no runtime persistence. It contributes build graph state by declaring which child directories participate in recursive make.

## Dependencies

It depends on both `src` and `utils` subdirectories existing and having valid Automake files. It also depends on the parent configure logic selecting the FUSE subtree only when relevant platform dependencies are available.

## Risks and Edge Cases

- Recursive make fails if either child directory is absent or not configured.
- The fixed order means any utility needing artifacts from `src` can rely on `src` being visited first, but accidental reverse dependencies from `src` to `utils` would be problematic.
- Empty `CLEANFILES` provides no cleanup signal for generated files in this directory.

## Test Signals

Run a FUSE-enabled build and verify both child directories are visited. Packaging checks should confirm both source and utility files are present in distribution output.
