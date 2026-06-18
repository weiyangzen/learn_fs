# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec.h

Purpose: Defines PowerPC kexec and crash-kexec limits, architecture image metadata, file-load hooks, crash shutdown callbacks, and reset helpers.

Important APIs, types, and functions: Defines kexec source/control memory limits, page size, `KEXEC_ARCH`, state constants, `crash_shutdown_t`, `kimage_arch`, `kexec_copy_flush()`, file-loader ops/probes, FDT setup helpers, crash reserve APIs, `crash_setup_regs()`, crash hotplug hooks, `crashing_cpu`, crash IPI callbacks, shutdown register/unregister, `kdump_in_progress()`, `is_kdump_kernel()`, `update_cpus_node()`, and `reset_sprs()`.

Control flow: Normal kexec loads an image, prepares architecture metadata/FDT, copies/flushes control pages, shuts down devices/CPUs, and jumps to the new kernel. Crash kexec records registers, notifies crash handlers, stops secondary CPUs, and boots the capture kernel.

State and persistence: State includes loaded `kimage`, arch metadata, crash reservation, registered shutdown handlers, and global crash flags. It is runtime-only until a crash dump kernel writes data elsewhere.

Dependencies and integration points: Integrates generic kexec, crash dump, FDT, RTAS, Book3S 64 reset logic, CPU hotplug, and SMP crash IPI.

Risks: Address limits differ for 32-bit and 64-bit. Crash paths cannot rely on normal locking/device state. Handler registration order can affect shutdown. FDT memory ranges must exclude crash/reserved regions correctly.

Test signals: `kexec -l/-e`, `kexec_file_load`, panic crash dump, CPU/memory hotplug metadata, handler register/unregister, 32-bit and 64-bit builds, and Book3S reset SPR coverage.
