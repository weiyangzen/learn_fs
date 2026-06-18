# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1.c

### Purpose
Core CPM1 management for MPC8xx systems: reset, microcode loading, CPM command execution, baud-rate generator setup, pin muxing, clock routing, and optional GPIO chip registration.

### Important APIs, Types, And Functions
Exports `cpmp`, `mpc8xx_immr`, `cpm_reset()`, `cpm_command()`, `cpm_setbrg()`, `cpm1_set_pin()`, `cpm1_clk_setup()`, and optional `cpm1_gpiochip_add16()` / `cpm1_gpiochip_add32()`. Internal types model 16-bit and 32-bit CPM I/O ports and GPIO chip state with shadowed data registers and locks.

### Control Flow
`cpm_reset()` initializes CPM base pointers, resets the CPM unless early debug forbids it, optionally loads microcode, and programs SDMA priority. `cpm_command()` serializes commands with a spinlock and polls completion. Pin and clock helpers directly program CPM registers. Optional GPIO registration maps port registers, initializes chip callbacks, and maps per-pin IRQs from DT.

### State, Persistence, And Dependencies
State includes global MMIO pointers, CPM register settings, BRG settings, pin muxes, clock routing, GPIO shadow data, spinlocks, and IRQ maps. No durable persistence. Dependencies include CPM/8xx register definitions, OF IRQ, GPIO library, DMA/MM headers, and optional microcode patching.

### Integration Points
Used by 8xx board setup and CPM drivers for serial, Ethernet, and GPIO. Provides exported CPM command/BRG APIs to other kernel code.

### Risks
High hardware risk: direct MMIO, lock ordering, command polling timeout, pin numbering, and GPIO shadow writes can break multiple peripherals. There is no deallocator for CPM DP RAM by design.

### Test Signals
Exercise CPM reset, command timeout/error paths, serial baud generation, SCC/SMC/FEC pin muxes, GPIO direction/get/set/to_irq, and builds with `CONFIG_8xx_GPIO` and `CONFIG_UCODE_PATCH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1.c -->
