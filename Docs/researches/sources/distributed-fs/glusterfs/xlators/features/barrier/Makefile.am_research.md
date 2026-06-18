<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/Makefile.am

## Purpose
Directory-level Automake entry for the barrier feature translator.

## APIs, Types, and Functions
Declares `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow, State, and Persistence
Build traversal descends into `src`; no runtime state exists in this file.

## Dependencies and Integration
Included from the top-level features Makefile. The module build itself is in `barrier/src/Makefile.am`.

## Risks and Test Signals
Risk is limited to build traversal or distribution omissions. A full build that enters `barrier/src` is the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/Makefile.am -->
