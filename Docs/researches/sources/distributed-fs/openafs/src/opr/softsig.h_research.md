# sources/distributed-fs/openafs/src/opr/softsig.h

Purpose: public API for OPR soft signal handling.

Important APIs/types/functions: declares `opr_softsig_Init` and `opr_softsig_Register`. On NT includes `afs/procmgmt_softsig.h` for platform-specific support.

Control flow: no runtime logic.

State and persistence: no header-owned state.

Dependencies/integration: included by pthreaded applications wanting centralized signal handling.

Risks and test signals: low-risk declaration header; behavior risk resides in `softsig.c`. Compile coverage validates platform includes.
