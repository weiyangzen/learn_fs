<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/Makefile.am

## Purpose
Build traversal manifest for bit-rot subcomponents.

## APIs, Types, and Functions
Declares `SUBDIRS = stub bitd`, building the bit-rot stub and daemon-side translator pieces.

## Control Flow, State, and Persistence
Automake descends into `stub` and `bitd` in that order. No runtime state exists here.

## Dependencies and Integration
The ordering implies shared stub headers or libraries are available before `bitd` compiles.

## Risks and Test Signals
Risks are missing child directories and ordering drift if `bitd` depends on generated stub artifacts. Full bit-rot builds are the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/Makefile.am -->
