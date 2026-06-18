<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/Kconfig -->
# sources/distributed-fs/ceph-client/arch/alpha/Kconfig

## Purpose
Alpha architecture Kconfig. It declares Alpha as a 64-bit MMU architecture, selects generic kernel capabilities and legacy ABI traits, and exposes machine-family, chipset, firmware, SMP, timing, memory, and SRM environment configuration.

## Important APIs, Types, And Functions
- `config ALPHA` selects architecture-wide capabilities such as PCI support, perf events, audit/seccomp, module RELA, sparsemem behavior, DMA state, and Alpha-specific ABI quirks.
- System-type `choice` selects machine families including generic, Alcor, DP264, LX164, Miata, Marvel, Mikasa, Noritake, PC164, Rawhide, Ruffian, RX164, SX164, Sable, Shark, Takara, Titan, and Wildfire.
- Derived symbols identify chipsets/CPU families: `ALPHA_CIA`, `ALPHA_EV56`, `ALPHA_T2`, `ALPHA_PYXIS`, `ALPHA_EV6`, `ALPHA_TSUNAMI`, `ALPHA_EV67`, `ALPHA_MCPCIA`, `ALPHA_POLARIS`, and `ALPHA_IRONGATE`.
- User-visible options include `ALPHA_QEMU`, `ALPHA_SRM`, `SMP`, `NR_CPUS`, sparse memory, `ALPHA_WTINT`, verbose machine checks, HZ selection, and `SRM_ENV`.

## Control Flow
Kconfig first enables architecture-level defaults and selected generic symbols. The user chooses a machine type, which drives chipset and CPU-family defaults. Firmware and SMP options depend on supported machine families and TTY availability. Timer frequency is selected through a choice with QEMU and Rawhide-specific defaults. `SRM_ENV` is offered as a tristate procfs interface when `PROC_FS` is available.

## State And Persistence
Selected Alpha symbols persist in `.config` and generate `CONFIG_ALPHA*`, timing, SMP, page-table, firmware, and module-format defines. These control Alpha architecture source compilation, boot behavior, scheduler/timer assumptions, and optional procfs driver availability.

## Dependencies And Integration Points
Integrates with generic `arch/Kconfig` capability symbols, PCI/EISA/ISA infrastructure, Alpha platform code, firmware/bootloader paths, SMP support, sparse memory, procfs, module loader, seccomp/audit, perf, and Kbuild conditional directories such as `math-emu`.

## Risks And Edge Cases
Machine-family defaults trade runtime autodetection against smaller/faster platform kernels; wrong selections can produce kernels that do not boot on target hardware. `ALPHA_WTINT` affects cycle counter reliability. Legacy firmware choices such as SRM versus MILO/ARC affect bootability. Some help text describes old hardware and assumptions that require regression testing on emulators or rare systems.

## Test Signals
Run `make ARCH=alpha olddefconfig`, machine-specific defconfigs if available, QEMU boot tests for generic and QEMU-specific settings, SMP and non-SMP builds, SRM_ENV module/built-in builds, and compile coverage for each selected chipset family where toolchains permit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/Kconfig -->
