# sources/distributed-fs/ceph-client/scripts/gdb/linux/dmesg.py

Purpose: Adds `lx-dmesg`, a GDB command that prints the kernel printk ring buffer from target memory.

Important APIs/classes: `LxDmesg` command. Cached types for `struct printk_info`, `struct prb_data_blk_lpos`, `struct prb_desc`, `struct prb_desc_ring`, `struct prb_data_ring`, and `struct printk_ringbuffer`.

Control flow: The command locates the static `prb` symbol in `printk.c`, reads ring metadata, computes descriptor/data ring sizes and addresses from type field offsets, reads tail/head ids, iterates committed/finalized descriptors, handles data-less and wrapping records, decodes UTF-8 text with replacement, and prints timestamped lines.

State/persistence: Registers command at import. Reads target memory but does not modify it.

Dependencies/integration: GDB Python API, `linux.utils` memory and integer readers, printk ringbuffer layout and symbols.

Risks: Very sensitive to printk ringbuffer internal layout and symbol names. Concurrent target logging can race with memory reads. Wrapped/truncated records are approximated. Python 2 compatibility path remains for unicode output.

Test signals: Ring buffers with committed/finalized/noncommitted records, wrapped text data, data-less records, UTF-8 replacement, live target mutation, and kernels with changed printk internals.
