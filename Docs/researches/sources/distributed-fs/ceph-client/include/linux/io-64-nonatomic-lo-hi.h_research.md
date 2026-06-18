# sources/distributed-fs/ceph-client/include/linux/io-64-nonatomic-lo-hi.h

Purpose: This header supplies fallback non-atomic 64-bit MMIO accessors for hardware that requires the low 32-bit half to be accessed before the high half.

Important APIs, types, and functions: It defines `lo_hi_readq`, `lo_hi_writeq`, relaxed variants, `ioread64_lo_hi`, `iowrite64_lo_hi`, big-endian variants, and conditional aliases for standard 64-bit I/O accessors when the architecture lacks native definitions.

Control flow: Reads load the low half first, then high, and combine into a 64-bit value. Writes emit low then high. Big-endian helpers map the logical halves to the correct addresses. Generic iomap plus 64-bit builds route aliases through `__ioread64_lo_hi` and related symbols.

State and persistence: No runtime state is stored. The header only establishes inline access sequences and preprocessor aliases.

Dependencies and integration points: Depends on `linux/io.h` and `asm-generic/int-ll64.h`. Drivers include it to match device register latch semantics where low access must precede high access.

Risks: Reads and writes are not atomic. Choosing this header for high-low devices can break register latching or command sequencing. Relaxed helpers reduce ordering constraints, and split writes to command registers may expose transient values to hardware.

Test signals: Test by compiling with and without arch-defined `readq`/`ioread64`, validating generated aliases, exercising endian-specific helpers, and checking device manuals or simulations for half-order side effects.
