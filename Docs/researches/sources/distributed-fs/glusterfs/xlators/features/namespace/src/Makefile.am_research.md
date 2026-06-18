# sources/distributed-fs/glusterfs/xlators/features/namespace/src/Makefile.am

## Purpose

This Automake file builds and installs the `namespace.la` feature translator.

## Important APIs, Types, and Functions

It sets `xlator_LTLIBRARIES = namespace.la`, module flags, `namespace_la_SOURCES = namespace.c`, `namespace_la_LIBADD`, `noinst_HEADERS = namespace.h`, include paths for libglusterfs, RPC XDR, and xlators lib, plus standard warning flags.

## Control Flow

Build flow compiles `namespace.c`, links it as a Gluster xlator module, and installs it under the package xlator feature directory.

## State and Persistence Behavior

No generated or persistent runtime state is defined.

## Dependencies and Integration Points

The namespace translator links only against libglusterfs and includes helper headers from `xlators/lib/src`.

## Risks and Edge Cases

Missing `xlators/lib/src` include coverage could break `GET_ANCESTRY_PATH_KEY` or default helper use. Since there is no generated source, clean behavior is simple.

## Test Signals

Clean configure/build should produce `namespace.la`; include-order and warning checks should cover `namespace.h` and namespace fop declarations.
