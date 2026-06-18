# sources/distributed-fs/ceph-client/arch/mips/dec/kn01-berr.c

Purpose: handles parity and timeout bus errors on KN01 DECstation 2100/3100 systems.

Important APIs: `dec_kn01_be_handler()` handles synchronous bus-error exceptions; `dec_kn01_be_interrupt()` handles bus-error IRQs; `dec_kn01_be_init()` initializes the cached CSR and enables parity detection. `cached_kn01_csr` is global because CSR low bits are write-only and must be preserved by software.

Control flow: the backend acknowledges errors early, determines whether the error came from exception or interrupt context, reconstructs the failing physical address for reads by inspecting the faulting instruction and TLB entry, classifies memory parity versus I/O timeout, and returns fixup or fatal. Interrupt context ignores video-shared false positives and dies for fatal errors.

State and integration: `cached_kn01_csr` plus a raw spinlock protect write-only CSR updates. The handler integrates with `dec/setup.c` bus-error selection and shares the bus interrupt on KN01.

Risks and test signals: address reconstruction is delicate for branch-delay and TLB state. Shared video/bus interrupt filtering is required. Test parity/timeout events, `get_dbe()` fixups, and video interrupt coexistence.
