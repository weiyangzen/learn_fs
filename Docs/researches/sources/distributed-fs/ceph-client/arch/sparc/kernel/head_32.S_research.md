# sources/distributed-fs/ceph-client/arch/sparc/kernel/head_32.S

## Purpose
`head_32.S` is the 32-bit SPARC boot entry. It validates supported machines, remaps the kernel to high virtual memory when needed, initializes early CPU/platform state, patches register-window routines, installs the trap table, and calls `sparc32_start_kernel()`.

## Important APIs, Types, and Functions
Important global data includes boot header fields `root_flags`, `root_dev`, `ram_flags`, `sparc_ramdisk_image`, `sparc_ramdisk_size`, `prom_vector_p`, `nwindows`, `nwindowsm1`, `linux_dbvec`, and `lvl14_save`. Key labels are `gokernel`, `execute_in_high_mem`, `leon_init`, `sun4d_init`, `sun4m_init`, `continue_boot`, and unsupported-machine paths.

## Control Flow and State
The entry saves ROM/debug vectors, detects whether the kernel is already mapped, copies the PROM level-14 handler, verifies SRMMU/LEON support, and creates a KERNBASE mapping by editing SRMMU page tables. Once high-mapped, it queries PROM `compatible`, chooses LEON/sun4m/sun4d initialization, sets boot CPU ID, clears stale MMU fault registers, enables supervisor/FPU/PIL state, initializes the stack, zeroes BSS, initializes `current_set`, computes the number of register windows, patches 7-window variants, installs `trapbase` in TBR, enables traps, and calls C startup.

## Persistence and Dependencies
Persistent boot state includes PROM pointers, CPU type string, register-window counts, boot CPU ID, trap table base, and boot header fields consumed by bootloaders. Dependencies include PROM node ops, SRMMU/LEON ASIs, trap table include `ttable_32.S`, patch labels in window/trap/return files, and platform-specific IRQ/SMP code.

## Integration Points, Risks, and Test Signals
Integration points are bootloader ABI, PROM, trap setup, CPU probing, SMP platform code, and early memory mapping. Risks include unsupported machine detection, incorrect physical/virtual relocation, 7-window patch mismatch, stale PROM timer/trap state, and bootloader header compatibility. Test signals are successful boot on sun4m, sun4d, and LEON configurations, correct unsupported sun4u message for 32-bit kernel, stable timer interrupts after trap-table switch, and correct `nwindows` reporting.
