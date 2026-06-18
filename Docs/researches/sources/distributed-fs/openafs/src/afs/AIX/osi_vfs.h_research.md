# sources/distributed-fs/openafs/src/afs/AIX/osi_vfs.h

Purpose: AIX vnode/vfs compatibility macro header for common OpenAFS code.

Important APIs and macros: maps access bits (`VREAD`, `VEXEC`, `VWRITE`), mode bits (`VSUID`, `VSGID`, `VSVTX`), copy helpers, block sizes, vnode flags, append mode, `VTOI`, `v_op`, `iunlock`, buffer function declarations, buffer field aliases, and `dbtob`. It also defines `enum vcexcl` when needed.

Control flow: none.

State and persistence: none directly.

Dependencies and integration: included by AIX vnode/misc code that expects more portable vnode names.

Risks and test signals: macro aliases must match AIX headers for the target release. Mismatches show up as compile failures or incorrect vnode operation dispatch.
