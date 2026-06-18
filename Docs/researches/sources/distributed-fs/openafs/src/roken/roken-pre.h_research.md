# sources/distributed-fs/openafs/src/roken/roken-pre.h

Purpose: local prelude prepended to generated `roken.h`.

Important APIs/types/functions: starts the include guard with `#ifndef OPENAFS_ROKEN_H` and `#define OPENAFS_ROKEN_H`.

Control flow: preprocessor-only guard setup before the upstream Heimdal `roken.h.in` contents.

State/persistence: no runtime state.

Dependencies/integration: concatenated with upstream `roken.h.in` and `roken-post.h` by the roken makefile.

Risks: the guard name must match the postlude. A mismatch would allow duplicate declarations or leave the generated header syntactically unclosed. Test signals are repeated inclusion of generated `roken.h` in a compile test.
