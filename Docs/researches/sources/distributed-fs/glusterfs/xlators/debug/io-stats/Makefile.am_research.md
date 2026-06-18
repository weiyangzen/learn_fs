# sources/distributed-fs/glusterfs/xlators/debug/io-stats/Makefile.am

## Purpose
Top-level Automake fragment for the GlusterFS `debug/io-stats` translator directory.

## Important APIs, types, and functions
`SUBDIRS = src` delegates all build work to the implementation subdirectory. `CLEANFILES =` is intentionally empty.

## Control flow
Automake descends into `src` when building, installing, cleaning, or distributing this translator.

## State and persistence behavior
No runtime state or persistence exists in this build file.

## Dependencies and integration points
This file connects the `xlators/debug/io-stats` directory into the recursive build. The actual module, headers, compiler flags, and library linkage are defined in `src/Makefile.am`.

## Risks and test signals
Build risk is low. A missing or misspelled `SUBDIRS` would exclude the translator from builds. Test signal is an autotools build confirming `io-stats.la` is reached through this directory.
