## sources/distributed-fs/openafs/src/libuafs/linktest.c

Purpose: Link-only smoke program for `libuafs.a`.

Important APIs and functions: `main` calls `uafs_SetRxPort`, `uafs_Setup`, `uafs_ParseArgs`, `uafs_Run`, `uafs_RxServerProc`, and `uafs_Shutdown`.

Control flow: The program sets RX port to 0, initializes the userspace AFS client with null mount and argument defaults, starts it, enters the RX server procedure, then shuts down. A comment states it is not intended to be run; its purpose is to prove that a program can link with libuafs and its dependencies.

State and persistence: If run, it would initialize userspace AFS runtime state and may interact with cache/config defaults. In intended build use, it only creates a binary.

Dependencies and integration: Includes socket/stat/types, RX, OpenAFS sysincludes, and `afs_usrops.h`. Built by `Makefile.common` as `linktest` against `libuafs.a`, `libcmd`, `libafsutil`, `libopr`, crypto, roken, crypt, and platform test libs.

Risks: Because it calls runtime initialization and server loop functions, accidentally executing it may block or perform unintended client setup. It ignores return codes, which is acceptable for link testing but not runtime diagnostics.

Test signals: Successful compilation and link are the primary signal. A secondary controlled run can verify symbol resolution, but should be treated carefully because the program was not designed as an execution test.
