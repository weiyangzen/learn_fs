# sources/distributed-fs/ceph-client/arch/sparc/lib/bzero.S

Purpose: SPARC64 baseline `memset`, `__bzero`, and `__clear_user`.

Important APIs/functions: Exports `memset`, `__bzero`, and `__clear_user`.

Control flow: `memset` replicates the byte pattern and enters `__bzero`-style fill loops. `__bzero` handles leading bytes, aligned large xword stores with prefetch, medium chunks, and byte tails. `__clear_user` mirrors zeroing through user ASI stores protected by exception-table entries and returns remaining bytes on fault.

State and persistence: Mutates target memory; user clear temporarily uses `%asi` and exception metadata.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; may be patched by CPU-specific bzero patchers.

Risks/test signals: Tail logic and clear-user residuals are sensitive. Test all small sizes, unaligned addresses, nonzero memset patterns, user faults, and CPU patch replacement.
