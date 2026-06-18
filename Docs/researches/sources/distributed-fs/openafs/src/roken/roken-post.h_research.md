# sources/distributed-fs/openafs/src/roken/roken-post.h

Purpose: local postlude appended to generated `roken.h` after the upstream Heimdal template.

Important APIs/types/functions: undefines an empty upstream `__attribute__` macro when present and closes `OPENAFS_ROKEN_H`.

Control flow: preprocessor-only cleanup after the upstream header body. It prevents roken's compatibility macro from hiding later compiler attributes in downstream includes.

State/persistence: no runtime state; affects translation unit preprocessing after `roken.h` inclusion.

Dependencies/integration: concatenated by `src/roken/Makefile.in` into generated `roken.h`.

Risks: touching `__attribute__` is compiler-sensitive; if upstream changes its guard or attribute handling, this postlude can either become ineffective or interfere with valid compatibility code. Test signals are successful builds where `roken.h` is followed by headers using GCC/Clang attributes.
