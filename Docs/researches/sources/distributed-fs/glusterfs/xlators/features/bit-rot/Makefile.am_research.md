<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/Makefile.am

## Purpose
Directory-level Automake entry for the bit-rot feature.

## APIs, Types, and Functions
Declares `SUBDIRS = src`.

## Control Flow, State, and Persistence
Build traversal descends into `src`. There is no runtime state or cleanup rule here.

## Dependencies and Integration
Included by the top-level features Makefile. Actual bit-rot build definitions are below `src`.

## Risks and Test Signals
Risk is limited to traversal/distribution omissions. A build that enters `bit-rot/src` is the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/Makefile.am -->
