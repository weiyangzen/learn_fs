# sources/distributed-fs/ceph-client/samples/kfifo/Makefile

Purpose: builds four kfifo sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_KFIFO` to `bytestream-example.o`, `dma-example.o`, `inttype-example.o`, and `record-example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: kfifo APIs and procfs/scatterlist APIs used by modules.

Risks: all samples are selected together.

Test signals: enabling `CONFIG_SAMPLE_KFIFO` builds all four objects.
