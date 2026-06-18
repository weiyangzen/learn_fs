# sources/distributed-fs/ceph-client/arch/mips/dec/kn02xa-berr.c

Purpose: handles parity and timeout bus errors on KN02-BA/KN04-BA and KN02-CA/KN04-CA DECstation systems.

Important APIs: `dec_kn02xa_be_handler()`, `dec_kn02xa_be_interrupt()`, and `dec_kn02xa_be_init()`. The backend reads memory error register and error address register, classifies memory parity versus TurboChannel timeout, logs byte-lane status, and returns fixup or fatal.

Control flow: ack writes MER and memory-interrupt registers immediately. If the address is below 256 MB it is treated as memory parity; otherwise I/O/TurboChannel timeout. Fixup is honored for synchronous exception handling only; interrupt fatal paths call `die()`.

State and integration: no long-lived local state other than hardware registers. Init enables error reporting for R4000SC variants through the KN4K memory board CSR and clears leftover firmware errors.

Risks and test signals: byte-lane reporting depends on MER bits; fixing or suppressing the wrong error can hide data corruption. Test with protected bus probes, memory parity injection where possible, and asynchronous bus IRQ handling.
