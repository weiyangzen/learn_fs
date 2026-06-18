# sources/distributed-fs/glusterfs/rpc/rpc-transport/Makefile.am

## Purpose

This Automake file routes the RPC transport build into the `socket` subdirectory. It was read as a complete one-line file.

## Important APIs, Types, and Functions

The only build directive is `SUBDIRS = socket`.

## Control Flow

There is no runtime control flow. During `make`, Automake descends into `rpc/rpc-transport/socket` to build transport modules.

## State and Persistence Behavior

No runtime state or persistence is represented. Build state is the generated Makefile dependency graph.

## Dependencies and Integration Points

This is the top-level RPC transport build hook and integrates with the socket transport subtree.

## Risks and Edge Cases

Adding another transport requires updating this file or it will not be built. A missing or empty subdirectory build would silently limit available RPC transports to those listed here.

## Test Signals

Autotools `make`/`make distcheck` coverage should verify that the socket subdirectory is entered and packaged.
