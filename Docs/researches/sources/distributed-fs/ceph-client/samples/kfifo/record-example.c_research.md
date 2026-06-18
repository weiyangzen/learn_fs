# sources/distributed-fs/ceph-client/samples/kfifo/record-example.c

Purpose: demonstrates record-oriented kfifo usage with variable-length records and procfs integration.

Important APIs/functions: `struct kfifo_rec_ptr_1` or `STRUCT_KFIFO_REC_1`, `kfifo_in`, `kfifo_out`, `kfifo_peek_len`, `kfifo_skip`, `kfifo_from_user`, `kfifo_to_user`, and procfs operations.

Control flow: init allocates/initializes the record fifo, inserts several strings, exercises record peek/skip/out behavior against expected values, then creates `/proc/record-fifo`. Reads return complete records up to buffer limits; writes enqueue user-provided records. Exit removes proc entry and frees allocation.

State and persistence: record fifo contents in kernel memory while loaded.

Dependencies and integration: kfifo record API and procfs.

Risks: record size header is one byte in this sample, limiting record length. Procfs users must handle record boundaries. Error paths are sample-grade.

Test signals: module load should pass the built-in expected-result test; procfs reads should preserve record boundaries.
