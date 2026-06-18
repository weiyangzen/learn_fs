<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.h

Purpose: Defines private IPIC constants, source metadata, and the controller object used by `ipic.c`.

Important APIs/types/functions: Defines `NR_IPIC_INTS`, external IRQ numbers, default priority value, SICFR/SEMSR/SERCR bit masks, `struct ipic`, and `struct ipic_info`.

Control flow: No runtime flow; the structures drive lookup logic in `ipic.c` for mask, priority, force, ack, and bit position.

State and persistence: `struct ipic` persists the MMIO register base and irqdomain. `struct ipic_info` describes immutable per-source register metadata.

Dependencies and integration points: Includes `asm/ipic.h` and is private to the IPIC sysdev implementation.

Risks: Metadata fields are tightly tied to the silicon register map. Any wrong bit or register offset would break mask/ack/sense behavior for that hardware source.

Test signals: Compile coverage and runtime validation that each documented IPIC source can be masked/unmasked/acked with the expected register bit.

Source read size: 56 lines, 1369 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.h -->
