# sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/crime.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ip32/crime.h` Platform hardware register, IRQ, and device-layout contract for Jazz or SGI IP32 CRIME/MACE systems. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 158 lines / 5261 bytes. macros/constants: `__ASM_CRIME_H__`, `CRIME_BASE`, `CRIME_ID_MASK`, `CRIME_ID_IDBITS`, `CRIME_ID_IDVALUE`, `CRIME_ID_REV`, `CRIME_REV_PETTY`, `CRIME_REV_11`, `CRIME_REV_13`, `CRIME_REV_14`, `CRIME_CONTROL_MASK`, `CRIME_CONTROL_TRITON_SYSADC`, `CRIME_CONTROL_CRIME_SYSADC`, `CRIME_CONTROL_HARD_RESET`, `CRIME_CONTROL_SOFT_RESET`, `CRIME_CONTROL_DOG_ENA`, `CRIME_CONTROL_ENDIANESS`, `CRIME_CONTROL_ENDIAN_BIG`; types/functions/declarations: `struct sgi_crime {`, `extern struct sgi_crime __iomem *crime;`.

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
