# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/cyaml.h

## Purpose
Declares the public cYAML tree API for LNet user-space configuration code.

## Important APIs And Types
Defines `enum cYAML_object_type`, `struct cYAML`, cleanup/walk callbacks, parse/build APIs, print/dump APIs, free/user-data cleanup APIs, lookup/iteration helpers, constructors, insertion helpers, and `cYAML_build_error()`.

## Control Flow
Callers parse YAML or build trees programmatically, traverse through helpers or raw child/sibling links, dump/print, clean optional user data, and free the tree. Sequence iteration uses a caller-maintained cursor.

## State And Persistence
Returned trees and dump buffers are heap-owned by the caller. User data is opaque and caller-owned. No global state is exposed.

## Dependencies And Integration Points
Requires stdint, bool, and `FILE` context. Used by `cyaml.c` and other `liblnetconfig` user-space sources.

## Risks
Raw mutable links allow callers to corrupt tree invariants. Function comments have minor copy/paste inaccuracies. Sequence iteration depends on correct cursor reset. Constructors take `char *` but implementation duplicates strings.

## Test Signals
Compile inclusion, parse/free, constructor insertion order, direct vs recursive lookup, sequence cursor reset, dump ownership, and user-data cleanup.
