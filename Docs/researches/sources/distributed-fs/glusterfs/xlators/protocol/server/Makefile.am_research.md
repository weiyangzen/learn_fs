# sources/distributed-fs/glusterfs/xlators/protocol/server/Makefile.am

## Purpose

This top-level automake fragment for `xlators/protocol/server` declares only `SUBDIRS = src`, delegating all build content to the `src` directory.

## Important APIs, types, and functions

There are no C APIs or functions in this file. Its only build API is the recursive automake directory declaration.

## Control flow

During an automake build, entering this directory recurses into `src`, where the server xlator shared object, sources, headers, compiler flags, and install locations are defined.

## State and persistence behavior

No runtime state or persistence exists here. Build state is limited to automake's recursive traversal.

## Dependencies and integration points

This file integrates with the parent automake tree and the child `src/Makefile.am`. Removing or changing `SUBDIRS` would disconnect the protocol/server implementation from recursive builds.

## Risks and test signals

The main risk is accidental omission of the `src` subtree from builds. Test signal is simple: `make` from the parent should enter `xlators/protocol/server/src` and produce/install `server.la` when server support is enabled.
