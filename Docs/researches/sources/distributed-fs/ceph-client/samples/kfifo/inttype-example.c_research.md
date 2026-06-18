# sources/distributed-fs/ceph-client/samples/kfifo/inttype-example.c

Purpose: demonstrates typed `kfifo` storing `int` elements and exposing it through procfs.

Important APIs/functions: `DEFINE_KFIFO` or `DECLARE_KFIFO_PTR`, typed `kfifo_put/get/in/out/peek/skip`, `kfifo_from_user`, `kfifo_to_user`, procfs operations, and mutexes.

Control flow: init initializes the FIFO, runs a wraparound correctness test using expected integer values, and creates `/proc/int-fifo`. Proc operations copy raw integer-sized FIFO data to/from user buffers. Exit removes the proc entry and frees dynamic allocation if used.

State and persistence: FIFO contents remain in kernel memory while module is loaded.

Dependencies and integration: kfifo typed API and procfs.

Risks: user-space reads/writes raw integer bytes, so ABI is host-endian and not self-describing. Separate read/write mutexes do not fully serialize producers and consumers.

Test signals: load and check "test passed"; write binary integer data to `/proc/int-fifo` and read it back.
