# sources/distributed-fs/openafs/src/rx/multi.example/Makefile.in

Purpose: legacy makefile for Rx `multi_Rx` sample client/server.

Important APIs/types/functions: targets `sample_client`, `sample_server`, generated `sample.cs.c`, `sample.ss.c`, `sample.er.c`, and `sample.h`.

Control flow: includes config/LWP make fragments, uses hard-coded `/usr/andy` paths and custom `CFLAGS`, runs `rxgen sample.xg`, and links sample binaries.

State/persistence: generated rxgen stubs/header and sample binaries.

Dependencies/integration: Rx/LWP libraries, rxgen, and sample sources.

Risks: hard-coded paths make it non-portable; generated-file dependencies must match `sample.xg`; lacks cleanup in shown content. Test signals are successful build in a compatible environment and sample client/server RPC execution.
