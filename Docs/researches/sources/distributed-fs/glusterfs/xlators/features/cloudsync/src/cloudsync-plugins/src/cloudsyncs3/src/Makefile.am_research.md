# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/Makefile.am

## Purpose
Builds the `cloudsyncs3.la` plugin module installed under the cloudsync plugin directory.

## Important APIs, types, and functions
Defines `csp_LTLIBRARIES = cloudsyncs3.la`, sources `libcloudsyncs3.c` plus shared `cloudsync-common.c`, exports symbols from `libcloudsyncs3.sym`, and installs to `$(libdir)/glusterfs/$(PACKAGE_VERSION)/cloudsync-plugins`.

## Control flow
Compiles the plugin with GlusterFS include paths, curl/curlpp and crypto flags, links against `libglusterfs`, and leaves the final module available for `dlopen("cloudsyncs3.so")`.

## State and persistence behavior
Build artifact is the installed S3 plugin shared object. No runtime state here.

## Dependencies and integration points
Depends on libcurl, OpenSSL/libcrypto, curlpp flags in the Makefile, and the cloudsync plugin ABI in `cloudsync-common.h`.

## Risks and test signals
Link flags are split between `AM_CPPFLAGS` and `AM_CFLAGS`, which can hide portability problems. Tests should build with S3 enabled, inspect exported `store_ops`, and verify installed file name matches `cloudsync.c`.
