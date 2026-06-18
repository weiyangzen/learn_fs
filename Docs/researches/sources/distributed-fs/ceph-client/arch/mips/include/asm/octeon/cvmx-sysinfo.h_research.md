# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sysinfo.h

Purpose: defines the CVMX system-information structure populated from the OCTEON bootloader descriptor and declares the accessor for that information.

Important APIs/types/functions: `struct cvmx_sysinfo` contains installed DRAM size, bootmem descriptor physical address, stack/heap locations and sizes, running core mask, deprecated init core, exception base, CPU clock, DRAM data rate, board type/revision, MAC base/count, board serial number, compact-flash physical base addresses, LED display base, DFA reference clock, bootloader config flags, and console UART. `cvmx_sysinfo_get()` returns the global structure pointer.

Control flow: the header has no inline logic. Initialization code elsewhere populates the structure from bootloader data or via minimal initialization for Linux/u-boot/simple executive consumers; callers retrieve it with `cvmx_sysinfo_get`.

State and persistence: the structure is process/kernel memory state reflecting bootloader-provided platform facts. It persists for the boot lifetime and is read by timing, board, memory, and device code. It is not durable beyond boot.

Dependencies and integration points: includes `cvmx-coremask.h`. `cvmx.h` uses `cvmx_sysinfo_get()->cpu_clock_hz` in timeout calculations, and board/device code uses MAC, board, compact flash, LED, and console fields.

Risks: many CVMX helpers assume `cpu_clock_hz` and other required fields are initialized. `init_core` is deprecated and can be wrong for complex core masks. Physical addresses in optional board fields require correct address-space conversion by callers.

Test signals: boot tests should verify sysinfo population from descriptors, sane clock rates, valid core mask, MAC count/base, and correct timeout behavior in `CVMX_WAIT_FOR_FIELD64`.
