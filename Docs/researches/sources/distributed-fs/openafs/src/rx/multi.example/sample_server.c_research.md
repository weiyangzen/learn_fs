# sources/distributed-fs/openafs/src/rx/multi.example/sample_server.c

Purpose: simple Rx server backing the `multi_Rx` sample with add/subtract RPCs.

Important APIs/types/functions: `main`, `TEST_Add`, `TEST_Sub`, and `Quit`.

Control flow: initializes Rx on `SAMPLE_SERVER_PORT`, creates null server security, registers the `sample` service using generated `TEST__ExecuteRequest`, donates the process to the server pool, and implements arithmetic handlers that write results to output pointers.

State/persistence: no durable state; only Rx service state and per-call arithmetic output.

Dependencies/integration: generated `sample.h`, Rx service/security APIs, and standard I/O.

Risks: unauthenticated example service is harmless but not production-grade; `Quit` treats message as a format string; old-style prototypes can hide type mismatches. Test signals are sample client calls for add/subtract, verbose handler output, and server startup on expected port.
