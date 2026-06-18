# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/Makefile.am

## Purpose

This Automake file builds and installs the `quiesce.la` feature translator.

## Important APIs, Types, and Functions

It defines `xlator_LTLIBRARIES = quiesce.la`, module flags, `quiesce_la_SOURCES = quiesce.c`, `quiesce_la_LIBADD`, `noinst_HEADERS = quiesce.h quiesce-mem-types.h quiesce-messages.h`, include paths, and warning flags.

## Control Flow

Build flow compiles the quiesce source and links a Gluster xlator module against libglusterfs.

## State and Persistence Behavior

No generated build state is produced; clean state is empty.

## Dependencies and Integration Points

The translator depends on libglusterfs headers, RPC XDR include paths, and message/memory type headers in the same directory.

## Risks and Edge Cases

Memory type and message headers must stay in the noinst header list for distribution and compile dependency tracking. Missing timer/thread support in libglusterfs would break the implementation at compile time.

## Test Signals

Clean build of `quiesce.la`, include dependency tracking, and warning checks for `quiesce.c` are the main signals.
