## sources/distributed-fs/ceph-client/include/linux/coresight-stm.h

Purpose: This header is a kernel include wrapper for the CoreSight STM UAPI definitions.

Important APIs, types, and functions: It includes `<uapi/linux/coresight-stm.h>` and defines only its include guard.

Control flow: There is no control flow.

State and persistence: No state is declared in this wrapper; STM user/kernel ABI details live in the UAPI header.

Dependencies and integration points: It bridges in-kernel CoreSight STM users with the exported UAPI definitions.

Risks and test signals: Risks are limited to include ordering or UAPI drift. Test signals are CoreSight STM builds and user ABI compile checks.
