# sources/distributed-fs/ceph-client/arch/loongarch/lib/unaligned.S

Purpose: provides byte-wise unaligned memory read/write helpers used by the unaligned access emulator.

Important APIs, types, and functions: `unaligned_read(void *addr, void *value, unsigned long n, bool sign)` and `unaligned_write(void *addr, unsigned long value, unsigned long n)` plus shared fault label `.L_fixup_handle_unaligned`.

Control flow: read starts at the last byte, uses signed or unsigned byte load for the highest-order byte based on `sign`, shifts bytes into an integer, stores the result to `value`, and returns zero. Write shifts the source value by 8-bit increments and stores each byte in ascending address order. Zero length returns `-EFAULT`; exception-table entries also return `-EFAULT`.

State and persistence: no global state; writes output value or target bytes.

Dependencies and integration points: called by `kernel/unaligned.c`; depends on LoongArch exception tables and register-size macros for 32/64-bit builds.

Risks: sign extension is implemented by signed loading the final byte; byte order and shifts must match little-endian LoongArch expectations. Faults during output-value store are treated as helper failure.

Test signals: unaligned access emulation tests for sizes 2/4/8, signed and unsigned loads, write byte order, and faulting source/destination addresses.
