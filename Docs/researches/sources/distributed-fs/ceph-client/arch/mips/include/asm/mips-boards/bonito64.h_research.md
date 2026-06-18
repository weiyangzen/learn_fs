# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/bonito64.h

Purpose: Bonito64 system-controller register map for MIPS evaluation boards. It provides physical address ranges, PCI config and memory windows, GPIO/interrupt control, DMA/copier registers, and bit encodings.

Important APIs/types/functions: In C, `BONITO(x)` dereferences `_pcictrl_bonito + x` as volatile `u32`; assembly gets offsets. Externs `_pcictrl_bonito` and `_pcictrl_bonito_pcicfg` supply mapped bases. Major groups include boot/flash/socket/PCI address ranges, `BONITO_PCI*` config registers, `BONITO_BONPONCFG`, `BONITO_BONGENCFG`, `BONITO_IODEVCFG`, `BONITO_SDCFG`, `BONITO_PCIMAP`, interrupt registers, mailbox registers, LDMA/copier registers, GPIO helpers, ICU bits, PCI map helpers, and `BONITO_PCITOPHYS()`.

Control flow, state, and persistence: The header has no functions but its lvalue macros perform volatile MMIO reads/writes. Hardware state persists in Bonito registers controlling PCI address translation, cache behavior, interrupts, GPIO, DMA, and DRAM config.

Dependencies and integration: Consumed by MIPS board setup, PCI host bridge code, interrupt controllers, and early platform initialization. It relies on correct initialization of `_pcictrl_bonito`.

Risks and test signals: Volatile lvalue macros make accidental multiple evaluation or read-modify-write bugs likely. Some address translation macros require exact bitfield use. Test with Bonito64 PCI enumeration, interrupt delivery, GPIO access, and DMA/copy engine paths.
