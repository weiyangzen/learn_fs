# sources/distributed-fs/coda/coda-src/dir/Makefile.am

## Purpose
Automake definition for the internal Coda directory library.

## APIs, Types, and Functions
Builds `libcodadir.la` from `fid.c`, `codadir.c`, `codadir.h`, `dirbody.c`, `dirbody.h`, `dirinode.c`, and `dhcache.c`. It sets include paths for RPC2/RVM, base, kerndep, util, and vicedep headers.

## Control Flow, State, and Persistence
No runtime flow. Build state is limited to automake target composition and compiler flags.

## Dependencies and Integration
This library is linked by directory-aware tools such as `removeinc` and by server/client code that manipulates Coda directory bodies and DirInodes.

## Risks and Test Signals
Risks are missing test utilities from the build target and tight include coupling to generated vicedep headers. Test signals are successful `libcodadir.la` build and downstream link of consumers.
