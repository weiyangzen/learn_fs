# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/octeon.h

Purpose: exposes higher-level OCTEON platform declarations for boot memory allocation, board/bootloader queries, clock setup, delays, boot descriptor layout, and selected CPU control-register bitfields.

Important APIs/types/functions: bootmem APIs include physical/range/named allocation and named free plus lock/unlock declarations. Platform query declarations include simulation, PCI host mode, USB ref clock, clock rates, board type string, PCI interrupts, southbridge interrupt, boot coremask, boot arguments, and user I/O initialization. Timing declarations include CVM count initialization, delay setup, and I/O clock delay. `struct octeon_boot_descriptor` mirrors the bootloader descriptor with endian-specific field ordering, boot flags, core mask, DRAM/clock/board/chip/MAC/serial fields, and descriptor addresses. `union octeon_cvmemctl` models the CvmMemCtl register.

Control flow: this header is mostly declarations and data layout. Boot/board code elsewhere consumes the boot descriptor, performs bootmem allocations, initializes delays/clocks, and configures control-register behavior through the defined bitfields.

State and persistence: boot descriptor data is bootloader-provided and persists in memory for boot-time consumers. Bootmem allocation state is managed externally and can reserve or free named physical memory regions. Control-register fields are live CPU state.

Dependencies and integration points: includes `cvmx.h` and `asm/bitfield.h`. It connects Linux OCTEON platform code with CVMX low-level helpers, bootloader ABI, PCI/USB setup, board identification, and early memory management.

Risks: `struct octeon_boot_descriptor` has fields referenced by assembly and explicitly warns not to reorder early fields. Endian-specific layouts must match the bootloader ABI. Raw physical allocation APIs need alignment/range correctness and locking discipline. Control-register fields affect cache, TLB, sync, and write-buffer behavior.

Test signals: boot tests should validate descriptor parsing, board string/clock/MAC extraction, named bootmem allocation/free, PCI-host query behavior, USB reference-clock detection, and delay calibration.
