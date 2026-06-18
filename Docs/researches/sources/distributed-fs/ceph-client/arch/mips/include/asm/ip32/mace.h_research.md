# sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/mace.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/mace.h` Platform hardware register, IRQ, and device-layout contract for Jazz or SGI IP32 CRIME/MACE systems. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 365 lines / 10742 bytes. macros/constants: `__ASM_MACE_H__`, `MACE_BASE`, `MACEPCI_ERROR_MASTER_ABORT`, `MACEPCI_ERROR_TARGET_ABORT`, `MACEPCI_ERROR_DATA_PARITY_ERR`, `MACEPCI_ERROR_RETRY_ERR`, `MACEPCI_ERROR_ILLEGAL_CMD`, `MACEPCI_ERROR_SYSTEM_ERR`, `MACEPCI_ERROR_INTERRUPT_TEST`, `MACEPCI_ERROR_PARITY_ERR`, `MACEPCI_ERROR_OVERRUN`, `MACEPCI_ERROR_RSVD`, `MACEPCI_ERROR_MEMORY_ADDR`, `MACEPCI_ERROR_CONFIG_ADDR`, `MACEPCI_ERROR_MASTER_ABORT_ADDR_VALID`, `MACEPCI_ERROR_TARGET_ABORT_ADDR_VALID`, `MACEPCI_ERROR_DATA_PARITY_ADDR_VALID`, `MACEPCI_ERROR_RETRY_ADDR_VALID`; types/functions/declarations: `struct mace_pci {`, `struct mace_video {`, `struct mace_ethernet {`, `struct mace_audio {`, `struct {`, `struct mace_parport {`, `struct mace_isactrl {`, `struct mace_parport parport;`, `struct mace_ps2port {`, `struct mace_ps2 {`, `struct mace_ps2port keyb;`, `struct mace_ps2port mouse;`, `struct mace_i2c {`, `typedef union {`, `struct reg {`, `struct mace_timers {`, `struct mace_perif {`, `struct mace_audio audio;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by platform setup, PCI/ISA, Ethernet, SCSI, audio, serial, keyboard, timers, DMA, and error handling. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Struct layout and fixed address/IRQ mistakes can misprogram hardware or clear wrong error bits. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
