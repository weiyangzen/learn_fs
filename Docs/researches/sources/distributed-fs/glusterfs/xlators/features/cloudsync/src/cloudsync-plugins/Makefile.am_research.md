# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/Makefile.am

## Purpose
Top-level plugin subtree Makefile for cloudsync plugins.

## Important APIs, types, and functions
Build directive is `SUBDIRS = src`; no code APIs.

## Control flow
Recursive make descends into `src`, where conditional plugin directories are selected.

## State and persistence behavior
No direct state or artifacts beyond recursive build traversal.

## Dependencies and integration points
Integrates plugin builds under the cloudsync source build.

## Risks and test signals
Low risk. Build tests should confirm plugin conditionals are evaluated in the child Makefile.
