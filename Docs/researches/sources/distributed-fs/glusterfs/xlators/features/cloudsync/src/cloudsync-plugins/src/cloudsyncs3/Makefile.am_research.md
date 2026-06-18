# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/Makefile.am

## Purpose
Delegates the Amazon S3 cloudsync plugin build to its `src` directory.

## Important APIs, types, and functions
Only `SUBDIRS = src` and empty `CLEANFILES`.

## Control flow
Recursive make enters the plugin implementation directory.

## State and persistence behavior
No direct state.

## Dependencies and integration points
Part of the conditional S3 plugin build chain.

## Risks and test signals
Low risk; verify recursion reaches `cloudsyncs3/src` when `BUILD_AMAZONS3_PLUGIN` is enabled.
