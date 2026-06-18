# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.h

## Purpose
Declares the S3 plugin API and helper functions used inside `libcloudsyncs3.c`.

## Important APIs, types, and functions
Declares S3 request signing helpers, curl write callback, download entry point, child write callback, plugin lifecycle hooks, and memory/accounting dependencies. Includes `cloudsync-common.h` to expose `store_methods_t` compatibility.

## Control flow
Cloudsync core loads exported `store_ops`; the functions declared here are assigned to that struct inside the plugin C file.

## State and persistence behavior
No state itself. Declared functions operate on plugin config and cloudsync frame state.

## Dependencies and integration points
Includes libcurl and cloudsync common headers, forming the compile-time contract for the S3 plugin.

## Risks and test signals
Header does not declare remote-read support. Tests should ensure symbol export maps match declared lifecycle/download functions.
