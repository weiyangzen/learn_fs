# sources/distributed-fs/openafs/src/roken/config.h

Purpose: minimal OpenAFS configuration bridge included by roken sources so they see OpenAFS platform definitions and roken symbol decoration macros.

Important APIs/types/functions: includes `<afsconfig.h>` and `<afs/param.h>`; conditionally defines `inline` for NT, HP-UX, AIX, SGI, and NetBSD; defines `ROKEN_LIB_FUNCTION`, `ROKEN_LIB_CALL`, and `ROKEN_LIB_VARIABLE`.

Control flow: all behavior is preprocessor-time. Windows maps calling convention and exported variables; Unix-like builds leave the roken symbol macros empty. Some older platforms suppress or remap `inline`.

State/persistence: no runtime state; it shapes generated/preprocessed roken code.

Dependencies/integration: included by bundled Heimdal roken source files and generated `roken.h` consumers.

Risks: redefining `inline` globally can affect compiler diagnostics and ABI expectations in headers included afterward. Windows export/import semantics are hard-coded as export. Tests are compiler matrix builds for affected platforms and inclusion-order checks with `roken.h`.
