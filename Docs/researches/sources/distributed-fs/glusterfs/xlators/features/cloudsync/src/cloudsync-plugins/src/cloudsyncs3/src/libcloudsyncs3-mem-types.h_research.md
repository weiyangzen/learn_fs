# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3-mem-types.h

## Purpose
Defines memory accounting tags for the S3 cloudsync plugin.

## Important APIs, types, and functions
The enum `libaws_mem_types_` reserves `gf_libaws_mt_aws_private_t` and `gf_libaws_mt_end`.

## Control flow
`mem_acct_init()` in `libcloudsyncs3.c` registers this range for plugin allocations.

## State and persistence behavior
No durable state. It classifies `aws_private_t` allocation.

## Dependencies and integration points
Includes GlusterFS memory type definitions and is included by `libcloudsyncs3.h`.

## Risks and test signals
Header guard end comment references cloudsync rather than AWS, but functionally harmless. Test memory accounting with S3 plugin init/fini.
