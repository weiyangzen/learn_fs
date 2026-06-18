# sources/distributed-fs/openafs/src/rx/bulk.example/Makefile.in

Purpose: builds the modernized bulk Rx example client/server from `bulk.xg`.

Important APIs/types/functions: targets `bulk_client`, `bulk_server`, generated `bulk.cs.c`, `bulk.ss.c`, `bulk.er.c`, `bulk.h`, object dependencies, and `clean`.

Control flow: includes OpenAFS config/LWP make fragments, links client/server against `librx`, `liblwp`, and `libafsutil`, runs `${RXGEN}` on `bulk.xg`, and removes generated artifacts on clean.

State/persistence: generated rxgen stubs/header and example binaries.

Dependencies/integration: top build libraries, LWP, Rx, rxgen, and `bulk_io.o`.

Risks: typo `@TOP_OBJDUR@` in an include line can break configuration if not substituted elsewhere; example build depends on generated files and local library layout. Test signals are successful `make` in the example directory and file transfer smoke tests.
