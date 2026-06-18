# sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/prom.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/prom.h` DECstation platform hardware contract for prom.h: board slot offsets, interrupt input numbering, CSR/error/status bits, and where present bus-error or IRQ setup declarations. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 164 lines / 5207 bytes. macros/constants: `_ASM_DEC_PROM_H`, `VEC_RESET`, `PMAX_PROM_ENTRY`, `PMAX_PROM_HALT`, `PMAX_PROM_AUTOBOOT`, `PMAX_PROM_OPEN`, `PMAX_PROM_READ`, `PMAX_PROM_CLOSE`, `PMAX_PROM_LSEEK`, `PMAX_PROM_GETCHAR`, `PMAX_PROM_PUTCHAR`, `PMAX_PROM_GETS`, `PMAX_PROM_PRINTF`, `PMAX_PROM_GETENV`, `REX_PROM_MAGIC`, `REX_PROM_GETBITMAP`, `REX_PROM_GETCHAR`, `REX_PROM_GETENV`; types/functions/declarations: `static inline bool prom_is_rex(u32 magic)`, `typedef struct {`, `extern int (*__rex_bootinit)(void);`, `extern int (*__rex_bootread)(void);`, `extern int (*__rex_getbitmap)(memmap *);`, `extern unsigned long *(*__rex_slot_address)(int);`, `extern void *(*__rex_gettcinfo)(void);`, `extern int (*__rex_getsysid)(void);`, `extern void (*__rex_clear_cache)(void);`, `extern int (*__prom_getchar)(void);`, `extern char *(*__prom_getenv)(char *);`, `extern int (*__prom_printf)(char *, ...);`, `extern int (*__pmax_open)(char*, int);`, `extern int (*__pmax_lseek)(int, long, int);`, `extern int (*__pmax_read)(int, void *, int);`, `extern int (*__pmax_close)(int);`, `extern void prom_meminit(u32);`, `extern void prom_identify_arch(u32);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/types.h>`, `<asm/addrspace.h>`.

### Integration Points
DEC board setup, TURBOchannel/IOASIC probing, RTC, serial, Ethernet, SCSI, framebuffer, HALT, LED, and bus-error paths use these values to map hardware and dispatch interrupts. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Primary risks are fixed hardware ABI drift, misrouted cascaded interrupts, stale cached CSR shadows, and incorrect acknowledgement of memory or I/O bus errors. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
