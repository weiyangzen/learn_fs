# sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_dump.c

Purpose: Provides old-memory page copying for RISC-V crash dump kernels.

Important APIs/types/functions: Implements `copy_oldmem_page()` using `memremap()`, `copy_to_iter()`, and `memunmap()`.

Control flow: Kdump readers request a physical page frame, offset, and byte count. The function maps the old kernel page as write-back memory, copies the requested range into an iterator, unmaps, and returns copied bytes or an error.

State and persistence: No persistent state; it transiently maps old physical memory.

Dependencies and integration points: Integrated with generic crash dump/proc vmcore code, `iov_iter`, and memory remapping.

Risks and test signals: Incorrect bounds or remap attributes can read wrong crash memory or fail vmcore extraction. Test kdump boot, `/proc/vmcore` reads at page offsets, zero-length reads, and invalid PFN error paths.
