# sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.h

## Purpose
`printk_ringbuffer.h` defines the public and internal data contract for the printk ringbuffer. It describes metadata records, descriptor and data rings, descriptor states, bootstrap constants, static-definition macros, and reader/writer helper APIs used by printk and KUnit.

## Important APIs, types, and functions
`struct printk_info` carries sequence number, timestamp, text length, facility, flags, level, caller ID, optional execution context data, and device-printk metadata. `struct printk_record` is the reader/writer buffer descriptor. `struct prb_desc`, `struct prb_data_ring`, `struct prb_desc_ring`, `struct printk_ringbuffer`, and `struct prb_reserved_entry` define storage and reservation state. `enum desc_state` encodes `reserved`, `committed`, `finalized`, `reusable`, plus the pseudo-state `desc_miss`.

The header declares all public `prb_*` APIs and provides `prb_rec_init_wr()`, `prb_rec_init_rd()`, `prb_for_each_record()`, and `prb_for_each_info()`. `DEFINE_PRINTKRB()` and `_DEFINE_PRINTKRB()` allocate and initialize a ready-to-use static ringbuffer.

## Control flow
Writers initialize a `printk_record` with requested text size, reserve through the C implementation, fill returned buffers, and commit or final-commit through the declared APIs. Readers initialize output buffers and use either one-shot reads or iteration macros. Sequence helpers expose the oldest valid sequence, oldest descriptor sequence, next finalized sequence, and next reserve sequence.

## State and persistence behavior
The header fixes the in-memory format for ringbuffer persistence across runtime operations. It encodes descriptor ID and state in one atomic word using high bits for state and low bits for ID. It defines `FAILED_LPOS` and `EMPTY_LINE_LPOS` as impossible aligned logical positions for records without data blocks. Bootstrap comments explain why the initial tail/head descriptor is the last descriptor and why sequence values are seeded to make record 0 possible while initial readers still see an empty ring.

## Dependencies and integration points
The definitions depend on Linux atomic, bit, type, and dev_printk interfaces. Optional fields depend on `CONFIG_PRINTK_EXECUTION_CTX`. The static-definition macros are used by printk core instances and tests; the `__u64seq_to_ulseq()` conversion helpers bridge 64-bit sequence logic with 32-bit atomic storage.

## Risks and invariants
Any layout or macro change must preserve descriptor-state packing, bootstrap sequence assumptions, power-of-two buffer sizing, and alignment requirements. The 32-bit sequence conversion assumes readers cannot lag by more than 2^31 records. `text_len` is `u16`, so users must not advertise payload lengths beyond representable or allocated data. The header is shared by low-level printk paths, so ABI-like source compatibility matters.

## Test signals
Build coverage across 32-bit/64-bit, `CONFIG_PRINTK_EXECUTION_CTX`, and KUnit export configurations is important. Runtime signals come from the KUnit ringbuffer stress test, normal printk output under load, sequence iteration from consoles, and warnings from implementation-side validation of descriptor and logical-position invariants.
