# subset-b-000701 Research

Grouped source research for the requested m68k architecture files. Each file section is bounded by the reconciliation markers required for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/entry.S -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/entry.S

Purpose: non-MMU 68000 exception, syscall, interrupt, return-to-user, and task-switch assembly glue. It bridges CPU trap frames to generic kernel services.

Important entry points are `system_call`, `ret_from_exception`, `bad_interrupt`, `resume`, and the fixed autovector wrappers `inthandler1` through `inthandler7`. `system_call` saves registers with `SAVE_ALL_SYS`, calls `set_esp0`, bounds-checks `ORIG_D0` against `NR_syscalls`, dispatches through `sys_call_table`, and stores the return value in the saved pt_regs slot. If `TIF_SYSCALL_TRACE` is set, `do_trace` wraps dispatch with `syscall_trace_enter()` and `syscall_trace_leave()`.

Interrupt flow uses `SAVE_ALL_INT`, pushes a vector number and the pt_regs pointer, calls `process_int()`, then returns through `ret_from_exception`. The numbered handlers synthesize vectors 65-71 because this 68000 path cannot rely on richer exception-frame vector information. `bad_interrupt` increments `irq_err_count` and returns with `rte`.

State is almost entirely CPU register and stack state. `resume` persists task context by saving `sr`, kernel stack, and USP into `prev->thread`, restoring the same fields from `next->thread`, and returning to the scheduler caller. User return handling samples `thread_info->flags`, allows interrupts only near final restore, calls `do_notify_resume()` for signals, and branches to `reschedule` when requested.

Dependencies include `asm/entry.h` frame offsets, `thread_info` layout, `asm-offsets.h`, syscall table symbols, `process_int()`, `set_esp0()`, signal/reschedule hooks, and generic m68k trap code. Integration is direct: vector setup in `ints.c` installs these handlers, scheduler code calls `resume`, and syscall ABI correctness depends on the exact saved-register layout.

Risks and test signals: any pt_regs offset, stack adjustment, or interrupt-enable timing change can corrupt syscall arguments, lose signals, or overflow kernel stacks under interrupt load. Useful checks are m68k defconfig builds, syscall trace/strace behavior, forced invalid syscall returning `-ENOSYS`, timer interrupt delivery, signal delivery on return to user mode, and context-switch stress on non-MMU 68000 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/head.S -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/head.S

Purpose: common early boot entry for 68000-core non-MMU systems, including DragonBall/68x328 boards. It establishes CPU state, optional board/LCD registers, RAM descriptors, BSS, stack, and then enters `start_kernel`.

Key exported symbols are `_start`, `_rambase`, `_ramvec`, `_ramstart`, and `_ramend`; `bootlogo_bits` is also exported for LCD-enabled builds. The file computes `RAMEND`, honoring `CONFIG_MEMORY_RESERVE`, and places RAM metadata in writable data for later architecture setup.

Control flow starts by disabling interrupts, optionally emitting the Palm/Pilot ROM signature, disabling watchdogs, and programming 68x328 PLL registers. Under `CONFIG_ROMKERNEL`, it applies uCsimm register setup, optional LCD setup, and copies init data from ROM to RAM. Under RAM-kernel plus ROMFS, it moves the embedded romfs above BSS and advances `_ramstart`. It then clears BSS, sets the initial kernel stack to the top of `init_thread_union`, and calls `start_kernel`.

State/persistence is early global boot state: RAM ranges, vector base, copied data, zeroed BSS, hardware chip-select/LCD/watchdog registers, and the final boot stack. The assembly does not return after `start_kernel`; the `_exit` loop is only a fail-safe.

Dependencies include linker symbols such as `_etext`, `_sdata`, `__bss_start`, `__bss_stop`, `init_thread_union`, Kconfig memory constants, DragonBall hardware addresses, and optional generated logo headers. It integrates with board setup in `m68328.c`, ROM vector setup in `romvec.S`, and generic setup code that consumes `_rambase` and related symbols.

Risks and test signals: incorrect memory ranges can destroy romfs, BSS, or reserved RAM; incorrect PLL/LCD writes can hang early boot with no console. Validate by building representative `CONFIG_ROMKERNEL`, `CONFIG_RAMKERNEL`, `CONFIG_UCSIMM`, `CONFIG_PILOT`, and `CONFIG_INIT_LCD` combinations, checking map symbols, and booting or emulating with early serial/debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/ints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/ints.c

Purpose: generic interrupt controller and vector setup for 68x328/68000 non-MMU systems where the CPU provides limited interrupt source information.

Important APIs are `process_int(int vec, struct pt_regs *fp)`, `trap_init()`, and `init_IRQ()`. The file declares the assembly trap and interrupt entry points installed into `_ramvec`. `process_int()` reads the DragonBall interrupt status register `ISR`, finds pending set bits with a nested coarse-to-fine search, calls `do_IRQ(irq, fp)` for each pending IRQ, and clears the bit from its local snapshot.

The IRQ chip is `intc_irq_chip`; `intc_irq_mask()` sets the corresponding bit in `IMR`, while `intc_irq_unmask()` clears it. `init_IRQ()` programs `IVR = 0x40`, masks all interrupts with `IMR = ~0`, then assigns the chip and `handle_level_irq` to every IRQ. `trap_init()` installs syscall vector 32 and autovector handlers 65-71, while vectors 72-255 default to `bad_interrupt`.

State is held in memory-mapped DragonBall registers (`ISR`, `IMR`, `IVR`) and the RAM vector table. There is no persistent software queue; pending interrupt state is consumed directly from hardware each entry.

Dependencies include `asm/MC68328.h` or the EZ/VZ variants, `_ramvec`, assembly handlers in `entry.S`, `do_IRQ()`, and generic irq core functions. Integration is early architecture startup and machine timer/driver IRQ registration.

Risks and test signals: the software bit search assumes ISR bit-to-IRQ numbering is stable and that pending bits remain meaningful while dispatching. Validate by booting with timer IRQs, masking/unmasking devices, checking spurious interrupt counts, and ensuring all `NR_IRQS` receive a chip/handler. A specific regression signal is a timer storm or no timer ticks after `init_IRQ()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/ints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/ints.h

Purpose: tiny local declaration header connecting 68000 assembly interrupt entry code with the C interrupt dispatcher.

The only API is `asmlinkage void process_int(int vec, struct pt_regs *fp);`, with a forward declaration for `struct pt_regs`. The `asmlinkage` marker preserves the calling convention expected by `entry.S`, where vector and frame pointer are pushed on the stack before `jbsr process_int`.

State and persistence: none. The header does not define data, macros, or inline functions.

Dependencies are `linux/linkage.h` for `asmlinkage` and the architecture `pt_regs` type supplied elsewhere. Integration is local to `68000/ints.c` and `68000/entry.S`.

Risks and test signals: changing the prototype or dropping `asmlinkage` would silently break the assembly/C ABI. Compile coverage of `entry.S` and `ints.c` together is the primary test; runtime evidence is successful interrupt dispatch into `process_int()` with a valid register frame.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/ints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/m68328.c -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/m68328.c

Purpose: DragonBall 68328/68EZ328/68VZ328 board support registration. It binds machine-dependent hooks for timers, RTC, and reset, then calls board-specific initializers.

Important functions are `config_BSP(char *command, int len)` and the private `m68328_reset()`. `config_BSP()` installs `mach_sched_init = hw_timer_init`, `mach_hwclk = m68328_hwclk`, and `mach_reset = m68328_reset`. It suppresses the scheduler timer for `CONFIG_PILOT && CONFIG_M68328`, and delegates command-line/device setup to `init_ucsimm()` or `init_dragen2()` depending on board Kconfig.

`m68328_reset()` disables interrupts and jumps through a fixed flash reset image at `0x10c00000`: it clears `0xFFFFF300`, loads the initial SP and PC from flash, and jumps. This is hardware-specific reset behavior rather than a generic Linux reboot path.

State is machine hook registration plus hardware reset side effects. Optional logo headers are included when LCD initialization requires `bootlogo_bits`.

Dependencies include `machdep.h`, `m68328.h`, `timers.c` for `hw_timer_init()`/`m68328_hwclk()`, and board files `ucsimm.c` or `dragen2.c`. Integration is through the m68knommu architecture setup path invoking `config_BSP`.

Risks and test signals: wrong hooks mean no timer ticks or RTC; wrong reset address can lock reset. Build combinations for Pilot, uCsimm/uCdimm, and Dragen2 should compile, and runtime smoke tests should confirm `jiffies` advances, `hwclock` reads, boot command line is populated, and reboot enters firmware/flash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/m68328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/m68328.h -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/m68328.h

Purpose: local prototypes for 68328 board helpers and RTC support.

APIs declared are `init_dragen2(char *command, int size)`, `init_ucsimm(char *command, int size)`, and `m68328_hwclk(int set, struct rtc_time *t)`. The header forward-declares `struct rtc_time` to avoid requiring full RTC includes in every user.

State: none. The declarations describe initialization functions that mutate the command line and machine hooks elsewhere.

Dependencies and integration: consumed by `m68328.c`, `timers.c`, and board-specific source files. It is part of the local `68000/` board-support contract rather than a public uapi.

Risks and test signals: mismatched prototypes would be caught by compiler warnings/errors when building board variants. Runtime relevance is indirect: board command-line setup and RTC read/write paths should still work on selected 68328 machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/m68328.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/romvec.S -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/romvec.S

Purpose: ROM vector table for 68000 CPU startup. It supplies the initial stack pointer, reset PC, default exception handlers, and syscall trap vector in a dedicated `.romvec` section.

The table `e_vectors` begins with `CONFIG_RAMBASE + CONFIG_RAMSIZE - 4` as the initial SP and `_start` as the reset vector. Bus errors go to `buserr`, most processor exceptions and traps go to `trap`, and TRAP #0 is wired to `system_call`. Later entries are zero-filled placeholders.

State/persistence: this is static ROM image content used before C initialization and before the RAM vector table is fully initialized. It does not execute by itself but controls first CPU dispatch after reset.

Dependencies include `_start` from `head.S`, `buserr`/`trap`/`system_call` trap handlers, linker placement for `.romvec`, and Kconfig RAM sizing. Integration is with ROM/XIP boot images and CPU reset expectations.

Risks and test signals: a wrong initial SP or reset vector prevents boot; an incorrect syscall trap vector breaks the user ABI. Validate linker map placement, objdump of `.romvec`, and a boot smoke test that reaches `_start` and later accepts system calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/romvec.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/screen.h -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/screen.h

Purpose: compile-time monochrome bitmap asset used by 68000 DragonBall LCD initialization when `CONFIG_INIT_LCD` is enabled.

The header defines `screen_width` as 320, `screen_height` as 240, and `static unsigned char screen_bits[]` containing the image bytes generated by GIMP. It has no functions, types, or executable control flow. The `#ifdef CONFIG_INIT_LCD` guard keeps the asset out of non-LCD builds.

State/persistence: the bitmap is static data linked into the kernel image. Consumers treat `screen_bits` as a framebuffer source or LCD start address. It increases image size only when included and enabled.

Dependencies and integration: `dragen2.c` includes this header and assigns `LSSA = (long)screen_bits` while setting LCD geometry. `head.S` separately uses `bootlogo_bits` for other LCD boot paths; this file is the Dragen2-style screen asset, not a generic framebuffer driver.

Risks and test signals: the array size must match 320x240 one-bit assumptions, alignment must be acceptable for the LCD controller, and static linkage means each including translation unit gets its own copy. Validate by building with `CONFIG_INIT_LCD`, checking image size, and booting on LCD-enabled hardware or emulator to confirm the expected splash appears without memory faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/screen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/timers.c -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/timers.c

Purpose: hardware timer and simple RTC support for 68328-family non-MMU systems.

Important functions are `hw_timer_init()`, `hw_tick()`, `m68328_read_clk()`, and `m68328_hwclk()`. Compile-time board choices select clock source, prescaler, and `TICKS_PER_JIFFY`: Dragen2 uses SYSCLK with a large count, Xcopilot has a workaround path, and the default uses the 32 kHz clock.

Control flow: `hw_timer_init()` disables timer 1, requests `TMR_IRQ_NUM` with `IRQF_TIMER`, programs `TCTL`, `TPRER`, and `TCMP`, enables the timer, and registers the `m68328_clk` clocksource. `hw_tick()` acknowledges timer status by clearing `TSTAT`, advances `m68328_tick_cnt`, and calls `legacy_timer_tick(1)`. `m68328_read_clk()` returns the accumulated tick count plus current `TCN` under local IRQ protection.

State is the hardware timer register set and the software accumulator `m68328_tick_cnt`. `m68328_hwclk()` reads `RTCTIME` into a fixed date of 1901-01-01 plus hour/min/sec; setting is ignored.

Dependencies include DragonBall timer/RTC register macros from `MC68VZ328.h`, generic clocksource and IRQ APIs, and machine hooks installed by `m68328.c`. Integration is the architecture `mach_sched_init` and `mach_hwclk` contract.

Risks and test signals: inaccurate prescaler/compare constants distort timekeeping, and failure to request the timer IRQ leaves the system without scheduler ticks. Test with boot logs for timer IRQ request errors, monotonic clocksource reads, `jiffies` advancement, and board-specific HZ timing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/timers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/ucsimm.c -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/ucsimm.c

Purpose: uCsimm/uCdimm board initialization helper for retrieving boot monitor information and command-line append data.

The main API is `init_ucsimm(char *command, int size)`. It uses `bootstd` call macros to define monitor calls `getserialnum()`, `gethwaddr(int)`, and `getbenv(char *)`. The function logs the board serial string and hardware MAC address, reads the `APPEND` environment variable, and copies it into the kernel command buffer with `strscpy()`; if absent, it clears the command line.

State and persistence: it does not own persistent kernel state beyond mutating the boot command buffer. Hardware/firmware state is read from boot monitor services through the `_bsc*` wrappers. The file has a local `errno` symbol expected by the bootstd call convention.

Dependencies include `asm/bootstd.h`, DragonBall board register headers, and `m68328.c` calling this function for `CONFIG_UCSIMM` or `CONFIG_UCDIMM`. Integration is early command-line construction before generic parameter parsing.

Risks and test signals: firmware service ABI mismatches can return invalid pointers, and the source code appears to call `strscpy(p, command, size)` after `p = getbenv("APPEND")`, which should be reviewed because normal command population would copy from firmware string to `command`. Test by booting with an `APPEND` value, checking `/proc/cmdline`, and verifying MAC/serial logging does not fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/ucsimm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/Kbuild -->
# sources/distributed-fs/ceph-client/arch/m68k/Kbuild

Purpose: top-level m68k Kbuild object directory selection.

The file always builds `kernel/` and `mm/`, then conditionally includes machine, bus, emulator, FPU, math-emulation, CPU-core, and virtual-machine subdirectories according to Kconfig symbols. Examples include `amiga/` for `CONFIG_AMIGA`, `atari/` for `CONFIG_ATARI`, `68000/` for `CONFIG_M68000`, and `coldfire/` for `CONFIG_COLDFIRE`.

Control flow is Kbuild evaluation rather than runtime code. Object directory inclusion determines which board support code can define machine hooks, interrupt controllers, platform devices, and startup objects.

State/persistence: no runtime state; the persistent effect is the build graph and the resulting linked kernel image.

Dependencies are the Kconfig symbols defined under `arch/m68k/Kconfig*` and subdirectory Makefiles. Integration is with the global kernel build system through `obj-y` and `obj-$(CONFIG_*)`.

Risks and test signals: missing or overly broad directory inclusion can cause unresolved symbols, duplicate platform code, or omitted boot support. Validate with `make ARCH=m68k` for representative classic, Sun3, 68000 non-MMU, and ColdFire configs, and inspect that selected objects match enabled machine symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/Kconfig -->
# sources/distributed-fs/ceph-client/arch/m68k/Kconfig

Purpose: root configuration model for the Linux m68k architecture.

The top-level `config M68K` selects architecture capabilities such as flat binaries, DMA/cache behavior, syscall/modversion support, atomic helpers, old signal ABI options, and `ZONE_DMA`. Additional symbols define big-endian CPU behavior, ilog2/hweight support, default low-resolution time, `HZ`, page-table levels, MMU variants, and kexec/bootinfo support. It sources CPU, machine, bus, and device Kconfig files.

Control flow is configuration-time. `MMU`, `MMU_MOTOROLA`, `MMU_COLDFIRE`, and `MMU_SUN3` partition memory-management support; the `!MMU` branch exposes power management options. `HZ` defaults to 100 except for `CLEOPATRA`.

State/persistence: no runtime state directly, but selected symbols shape compiler flags, object inclusion, ABI assumptions, and machine hook availability throughout the architecture.

Dependencies include other `arch/m68k/Kconfig.*` files and generic kernel Kconfig symbols. Integration is broad: `Kbuild`, `Makefile`, board subdirectories, and headers all consume these symbols.

Risks and test signals: incorrect `select` statements can enable unsupported generic features or hide required dependencies. Test with `allyesconfig`, `allnoconfig` plus target machines, `randconfig`, and compile checks for MMU/non-MMU and ColdFire/classic splits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/Makefile

Purpose: architecture-specific build flags, cross-compiler defaults, compression targets, and install hooks for m68k.

It sets `KBUILD_DEFCONFIG := multi_defconfig`, chooses a default `CROSS_COMPILE` prefix when cross compiling, computes CPU compiler flags in priority order, and appends those flags to assembly and C builds. Non-MMU builds add `UTS_SYSNAME="uClinux"` and `__uClinux__`; MMU builds reserve register `a2` with `-ffixed-a2`. It sets the linker emulation to `-m m68kelf`.

Build targets include `all: zImage`, `lilo`, `zImage compressed: vmlinux.gz`, `bzImage: vmlinux.bz2`, `archheaders`, and `install`. Compression strips temporary `vmlinux.tmp` unless `CONFIG_KGDB` is enabled, where debug information and frame pointers are preserved.

State/persistence: no runtime state; persistent outputs are compressed images, installed files, and generated syscall headers.

Dependencies include the global Kbuild variables, toolchain support for selected `-m68000`/`-m68040`/ColdFire flags, gzip/bzip2 helpers, and `arch/m68k/lib/`. Integration controls every architecture object compiled in this source tree.

Risks and test signals: CPU flag ordering matters because 68040/68060 flags must not override lower baseline targets. Validate by building representative CPU configs, confirming toolchain fallback behavior, checking `CHECKFLAGS`, and verifying compressed images are generated and cleaned correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/Makefile

Purpose: Amiga platform object list.

It always builds `config.o`, `amiints.o`, `cia.o`, `chipram.o`, `amisound.o`, and `platform.o` for `CONFIG_AMIGA` directory inclusion. It adds `pcmcia.o` only when `CONFIG_AMIGA_PCMCIA` is enabled.

Control flow is Kbuild-only: this determines which machine setup, interrupt, CIA, Chip RAM, beeper, platform-device, and optional PCMCIA support enters the kernel image.

State/persistence: no runtime state in the Makefile; the persistent effect is linked object selection.

Dependencies include top-level `arch/m68k/Kbuild` selecting `amiga/` and Kconfig symbols for Amiga PCMCIA. Integration is with board setup in `config.c` and device drivers that depend on exported Amiga helpers.

Risks and test signals: omitting `cia.o` or `chipram.o` breaks timer/interrupt or audio allocations, while including `pcmcia.o` without hardware config would add unnecessary Gayle support. Validate Amiga builds with and without `CONFIG_AMIGA_PCMCIA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/amiga.h -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/amiga.h

Purpose: local Amiga prototypes shared across platform files.

The header declares `amiga_init_sound()` and `amiga_mksound(unsigned int hz, unsigned int ticks)` from `amisound.c`. These are consumed by `config.c` when initializing built-in audio and wiring `mach_beep`.

State/persistence: none in the header. The declared functions manipulate Chip RAM allocations, Paula audio DMA, and timers in their implementation.

Dependencies and integration: used inside the `arch/m68k/amiga` directory. It keeps sound prototypes out of broader architecture headers.

Risks and test signals: prototype drift would be compile-time visible. Runtime validation is Amiga boot with audio present and `CONFIG_INPUT_M68K_BEEP` enabled, confirming `mach_beep` can call `amiga_mksound()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/amiga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/amiints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/amiints.c

Purpose: Amiga custom-chip interrupt fan-out and IRQ chip setup.

Important functions are `amiga_init_IRQ()` and chained handlers `ami_int1`, `ami_int3`, `ami_int4`, and `ami_int5`. The `amiga_irq_chip` enables/disables machine IRQ sources by writing `amiga_custom.intena` based on `IRQ_USER` offset. Chained handlers read `intreqr & intenar`, acknowledge individual custom-chip bits, and call `generic_handle_irq()` for logical Amiga IRQs.

Control flow initializes a range of Amiga IRQs with `m68k_setup_irq_controller()`, installs chained handlers on autovectors 1, 3, 4, and 5, disables PCMCIA interrupts except IDE when Gayle is present, clears pending interrupts, enables the master interrupt bit, and delegates CIA setup to `cia_init_IRQ()` for CIAA/CIAB.

State is hardware interrupt enable/request registers plus IRQ-core chip/handler assignment. No persistent software queue is maintained.

Dependencies include `asm/amigahw.h`, `asm/amigaints.h`, `asm/amipcmcia.h`, `cia.c`, and generic irq APIs. Integration connects Paula/custom-chip hardware to Linux logical IRQs and downstream serial, floppy, audio, blitter, copper, vblank, and disk-sync drivers.

Risks and test signals: incorrect acknowledgement can lose or storm interrupts; IF_RBF is intentionally not acknowledged here because serial handles it. Test with vblank timer users, serial receive, audio IRQ users, floppy, and `/proc/interrupts` counts on Amiga hardware or emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/amiints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/amisound.c -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/amisound.c

Purpose: simple Amiga system beeper using Paula audio channel 2 and Chip RAM waveform data.

Important APIs are `amiga_init_sound()` and `amiga_mksound(hz, ticks)`. Exported variables `amiga_audio_min_period` and `amiga_audio_period` coordinate with framebuffer and DMA sound code. Initialization allocates Chip RAM for a 20-sample sine waveform via `amiga_chip_alloc_res()`, copies `sine_data`, computes a color-clock-based period constant, and may turn video off if no Amiga framebuffer is configured.

Control flow for `amiga_mksound()` deletes any pending stop timer, clamps requested frequency into Paula period limits, programs audio location/length/period/volume, optionally schedules `sound_timer`, and enables audio DMA. Invalid or zero frequencies call `nosound()`, which disables channel 2 DMA and restores the prior audio period.

State includes the Chip RAM waveform pointer, exported period values, `clock_constant`, Paula audio registers, DMA control, and a timer. Local IRQ disable protects register/timer updates.

Dependencies include `amiga_chip_alloc_res()`, `amiga_colorclock`, `amiga_custom`, jiffies/timers, and optional framebuffer hooks. Integration is through `mach_beep` in `config.c` and possible audio/fb driver cooperation.

Risks and test signals: failure to allocate Chip RAM disables beep; competing audio users can see period/DMA interference; incorrect min-period clamping can produce bad tones. Test by enabling `CONFIG_INPUT_M68K_BEEP`, calling console bell, and checking that audio DMA stops after `ticks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/amisound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/chipram.c -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/chipram.c

Purpose: resource-managed allocator for Amiga Chip RAM, the DMA-visible memory required by custom chips.

Important APIs are `amiga_chip_init()`, `amiga_chip_alloc()`, `amiga_chip_alloc_res()`, `amiga_chip_free()`, and `amiga_chip_avail()`. `amiga_chip_init()` creates a `chipram_res` range from `CHIP_PHYSADDR` through `amiga_chip_size`, attaches it to `iomem_resource`, and initializes the atomic available count. Allocations are page-aligned and use `allocate_resource()`; returns are converted through `ZTWO_VADDR()`.

State is `amiga_chip_size`, the `chipram_res` resource tree, and atomic `chipavail`. Allocations made with caller-owned resources may be permanent during early boot; `amiga_chip_alloc()` allocates a `struct resource` that can later be freed.

Dependencies include `amigahw` presence bits, `iomem_resource`, Zorro II address translation macros, resource management, and slab allocation. Integration supports audio waveform memory, framebuffer/video, and drivers requiring Chip RAM before or after normal allocation is available.

Risks and test signals: freeing an untracked pointer is reported and ignored; early permanent allocations intentionally cannot always be freed. Off-by-one resource ranges or wrong physical/virtual translation would break DMA. Test with Amiga boot hardware list, repeated allocate/free calls from a driver, and `amiga_chip_avail()` accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/chipram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/cia.c -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/cia.c

Purpose: IRQ control and fan-out for the Amiga CIAA and CIAB complex interface adapter chips.

Important types and APIs include `struct ciabase`, global `ciaa_base`/`ciab_base`, `cia_set_irq()`, `cia_able_irq()`, and `cia_init_IRQ()`. `cia_set_irq()` updates cached CIA interrupt data and can raise the matching Amiga custom interrupt request. `cia_able_irq()` updates interrupt masks in both software and CIA hardware.

Control flow: `cia_handler()` reads and clears pending CIA causes, acknowledges the parent custom interrupt, dispatches the timer source under local IRQ protection, then dispatches remaining CIA sub-IRQs. `cia_irq_chip` maps logical CIA IRQ enable/disable to CIA masks. `auto_irq_chip` overrides autovectors 2 and 6 so external CIA parent interrupts can be controlled through the generic IRQ layer. `cia_init_IRQ()` initializes the child IRQ range, clears/masks hardware, starts the parent IRQ, and requests the shared parent handler.

State is cached `icr_mask`/`icr_data`, CIA hardware registers, and irq-core chip assignments.

Dependencies include Amiga custom registers, CIA hardware structs, `m68k_setup_irq_controller()`, `m68k_irq_startup_irq()`, and request_irq. Integration is essential for CIAB Timer A scheduler ticks in `config.c`, external ports, and CIA child device interrupts.

Risks and test signals: CIA ICR reads are destructive, so cached state and locking order matter. Validate timer ticks, CIA child IRQ enable/disable, shared parent request success, and no lost timer interrupts under heavy interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/cia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/config.c

Purpose: central Amiga machine setup: bootinfo parsing, hardware detection, machine hook registration, timer/clocksource setup, reset, debug console, heartbeat, and `/proc` hardware reporting.

Important APIs are `amiga_parse_bootinfo()`, `config_amiga()`, private `amiga_identify()`, `amiga_sched_init()`, `amiga_read_clk()`, `amiga_reset()`, `amiga_get_model()`, and `amiga_get_hardware_list()`. It exports key platform state such as `amiga_eclock`, `amiga_colorclock`, `amiga_chipset`, `amiga_vblank`, and `amiga_hw_present`.

Control flow parses bootinfo records for model, clocks, chipset, Chip RAM, vblank, power-supply frequency, and Zorro autoconfig devices, including a Warp 1260 interrupt-storm workaround. `amiga_identify()` derives hardware presence bits from model, chipset registers, and custom chip IDs. `config_amiga()` registers motherboard resources, machine hooks, DMA master state, filters Zorro II memory on Zorro III systems, registers RAM resources, initializes Chip RAM, sound, and magic rekick state.

Timer flow programs CIAB Timer A using `amiga_eclock/HZ`, requests `IRQ_AMIGA_CIAB_TA`, starts the timer, and registers a continuous clocksource. `amiga_read_clk()` carefully reads CIAB timer high/low bytes and accounts for pending interrupts through `cia_set_irq()`.

State includes model name, hardware presence bitmap, resource trees, clock accumulators, savekmsg buffer, debug console write callback, and hardware registers. Reset disables MMU/translation as needed and jumps through Kickstart ROM reset vectors.

Dependencies include bootinfo formats, Amiga custom/CIA/Zorro headers, `chipram.c`, `amisound.c`, `amiints.c`, `cia.c`, generic machdep hooks, and optional heartbeat/input/debug features.

Risks and test signals: hardware probing and model inference are legacy and register-sensitive; timer code depends on CIA semantics; debug memory console steals Chip RAM early. Test with multiple Amiga models, Zorro devices, `debug=mem`/`debug=ser`, `/proc/hardware`, clocksource monotonicity, reboot, and audio/Chip RAM initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/pcmcia.c -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/pcmcia.c

Purpose: low-level Amiga Gayle PCMCIA helper functions exported to card/IDE/PCMCIA users.

Important APIs are `pcmcia_reset()`, `pcmcia_copy_tuple()`, `pcmcia_program_voltage()`, `pcmcia_access_speed()`, `pcmcia_write_enable()`, and `pcmcia_write_disable()`. `pcmcia_reset()` pulses `gayle_reset` and waits roughly 10 ms. `pcmcia_copy_tuple()` walks attribute memory tuples up to 64 KiB, copying the matching tuple including header while accounting for Gayle attribute byte spacing.

State is the static `cfg_byte`, which preserves program-voltage and access-speed bits across calls, and Gayle hardware registers/attribute memory. Write-enable state is set through `gayle.cardstatus`.

Dependencies include `asm/amigayle.h`, `asm/amipcmcia.h`, jiffies timing, and module exports. Integration is conditional through the Amiga Makefile and used by PCMCIA-capable Amiga drivers.

Risks and test signals: tuple walking can trigger write-related interrupts as noted in comments; voltage selection must be correct to avoid hardware damage; busy waits depend on jiffies being live. Test with tuple reads for known cards, voltage/speed transitions, reset behavior, and interrupt behavior around `GAYLE_IRQ_WR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/platform.c -->
# sources/distributed-fs/ceph-client/arch/m68k/amiga/platform.c

Purpose: Amiga platform-device registration for buses and onboard devices discovered by earlier hardware detection.

Important initcalls are `amiga_init_bus()` under `CONFIG_ZORRO` and `amiga_init_devices()`. It defines Zorro II/III memory resources, SCSI/IDE/RTC resources, and Gayle IDE platform data for A1200 and A4000 styles. Helper `z_dev_present()` scans Zorro autoconfig ROMs for board IDs.

Control flow: the Zorro bus is registered as `amiga-zorro` at `subsys_initcall` if the machine is Amiga and Zorro exists. Device init registers platform devices for video, audio, floppy, A3000/A4000 SCSI, Gayle IDE variants, keyboard, mouse, serial, parallel, and RTC chips depending on `AMIGAHW_PRESENT()` bits and Zorro card presence.

State is not long-lived in this file beyond registered `platform_device` objects and their attached resources/platform data. Resource arrays are `__initconst` where possible.

Dependencies include hardware presence state from `config.c`, Zorro autoconfig data, platform bus APIs, Gayle IDE data types, and downstream platform drivers. Integration exposes legacy Amiga hardware to normal Linux driver binding instead of direct arch probing.

Risks and test signals: resource base/size errors bind drivers to wrong registers; early return on one failed registration can suppress later devices. Test with Amiga configs covering A1200 IDE, A4000 IDE, SCSI, Zorro II/III, and RTC, checking platform devices under sysfs and driver probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/amiga/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/apollo/Makefile

Purpose: Apollo platform object selection.

It builds `config.o` and `dn_ints.o` for the Apollo machine directory. These provide machine setup, timer/RTC/reset/model hooks, and PIC interrupt control.

Control flow is Kbuild-only and depends on the top-level m68k Kbuild including `apollo/` when `CONFIG_APOLLO` is enabled.

State/persistence: no runtime state; object selection determines linked Apollo support.

Risks and test signals: omitting either object leaves unresolved `config_apollo()` dependencies or no IRQ controller. Validate a `CONFIG_APOLLO` build and boot far enough to initialize model setup and IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/apollo.h -->
# sources/distributed-fs/ceph-client/arch/m68k/apollo/apollo.h

Purpose: local Apollo interrupt initialization declaration.

The sole API is `void dn_init_IRQ(void);`, implemented in `dn_ints.c` and called by `config_apollo()` through `mach_init_IRQ`.

State: none. The declared function installs IRQ controller state elsewhere.

Dependencies and integration are local to the Apollo machine directory and m68k machdep hook setup.

Risks and test signals: prototype mismatch is compile-time visible. Runtime validation is successful Apollo IRQ setup and timer interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/apollo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/apollo/config.c

Purpose: Apollo Domain workstation machine setup.

Important state includes physical address globals for serial, RTC, PIC A/B, CPU control, timer, and `apollo_model`. `apollo_parse_bootinfo()` reads `BI_APOLLO_MODEL`; `dn_setup_model()` maps supported model IDs to SAU7/SAU8 hardware address constants and rejects unsupported/unknown models. `config_apollo()` installs `mach_sched_init`, `mach_init_IRQ`, `mach_hwclk`, `mach_reset`, optional heartbeat, and model callbacks, then clears the DMA translation table.

Timer flow programs Apollo timer registers, unmasks a PIC B IRQ bit, requests `IRQ_APOLLO`, and `dn_timer_int()` calls `legacy_timer_tick(1)`, `timer_heartbeat()`, and reads timer bytes to clear/settle the interrupt. `dn_dummy_hwclk()` reads/writes RTC fields directly with a 1970/2000 adjustment for short years.

State/persistence is board address selection, `cpuctrl`, timer/RTC hardware registers, and the DMA address translation map. Reset is a stub that prints through serial and spins forever.

Dependencies include Apollo bootinfo, `asm/apollohw.h` mapped register macros, `dn_ints.c`, generic machdep hooks, and legacy timer APIs.

Risks and test signals: model array indexing assumes valid model range before printing; unsupported DN4500 panics; reset is not a real reboot. Test bootinfo parsing for each supported model, timer tick delivery, RTC read/write, heartbeat bit toggling, and DMA translation map clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/dn_ints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/apollo/dn_ints.c

Purpose: Apollo PIC-backed IRQ controller setup.

Important functions are `dn_init_IRQ()`, `apollo_irq_startup()`, `apollo_irq_shutdown()`, and `apollo_irq_eoi()`. IRQs below 8 are controlled through PIC A mask register `pica+1`; IRQs 8-15 use PIC B `picb+1`. EOI writes `0x20` to both PIC command ports.

Control flow in `dn_init_IRQ()` reserves 16 user interrupt vectors starting at `VEC_USER + 96` and installs `apollo_irq_chip` with `handle_fasteoi_irq` for `IRQ_APOLLO` through the 16-source range.

State is hardware PIC mask/command registers and generic IRQ-core chip assignments. There is no additional software status cache.

Dependencies include `asm/apollohw.h`, `asm/traps.h`, `m68k_setup_user_interrupt()`, and `m68k_setup_irq_controller()`. Integration is through `config_apollo()` assigning `mach_init_IRQ`.

Risks and test signals: incorrect PIC split or EOI can wedge interrupts. Validate by booting Apollo config, confirming timer IRQ runs, and observing IRQ mask/unmask behavior for devices on both PICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/apollo/dn_ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/Makefile

Purpose: Atari platform object selection.

It always builds `config.o`, `time.o`, `debug.o`, `ataints.o`, `stdma.o`, `atasound.o`, and `stram.o`. It adds `atakeyb.o` for `CONFIG_ATARI_KBD_CORE` and `nvram.o` when `CONFIG_NVRAM` is modular-enabled through the substitution expression.

Control flow is Kbuild-only, selecting machine setup, clock/RTC, debug console, interrupt controller, shared DMA arbitration, sound, ST-RAM allocation, keyboard, and NVRAM support.

State/persistence: no runtime state in the Makefile; object inclusion shapes available hooks and exported symbols.

Dependencies include top-level `Kbuild` and Atari-related Kconfig symbols. Integration ensures `config_atari()` can reference functions such as `atari_sched_init()`, `atari_init_IRQ()`, and `atari_mksound()`.

Risks and test signals: the `CONFIG_NVRAM:m=y` expression is subtle and should be validated for built-in vs modular builds. Test Atari configs with and without keyboard core and NVRAM support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/ataints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/ataints.c

Purpose: Atari interrupt-controller setup and special IRQ allocation for autovectors, MFPs, SCC, VME, EtherNAT, and shared timer-D poll interrupts.

Important APIs are `atari_init_IRQ()`, `atari_register_vme_int()`, and `atari_unregister_vme_int()`. The primary `atari_irq_chip` starts/shuts/enables/disables machine IRQs by calling `m68k_irq_startup()`, `atari_turnon_irq()`, `atari_enable_irq()`, and matching shutdown calls. It also restores Falcon HBL handlers for `IRQ_AUTO_4` shutdown.

Control flow initializes user vectors for all Atari sources, configures ST-MFP and optional TT-MFP vector bases/masks, resets SCC when needed, programs SCU masks or HBL fallback handlers, initializes PSG and shared ST-DMA, and installs a Timer D fan-out handler for polled sub-IRQs. EtherNAT IRQs 139-140 get a CPLD-backed IRQ chip that maps/unmaps the CPLD register and avoids enabling USB at startup to prevent storms.

State includes `free_vme_vec_bitmap`, `stmfp_base.int_mask`, optional `enat_cpld` mapping, MFP/SCU/SCC hardware registers, and IRQ-core configuration. VME IRQ allocation persists through the bitmap until unregistered.

Dependencies include Atari hardware headers, `stdma_init()`, `atari_microwire_cmd()`, generic IRQ APIs, and vector table symbols. Integration is set through `mach_init_IRQ` in `config.c` and used by Atari storage, network, USB, SCC, and VME drivers.

Risks and test signals: shared MFP and EtherNAT control are prone to storms or lost interrupts; dynamic VME allocation has a bitmap bound mismatch risk because the loop scans 32 bits but checks `i == 16`. Test `/proc/interrupts`, VME register/unregister, Timer D polled IRQs, EtherNAT/NetUSBee behavior, and Falcon HBL suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/ataints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/atakeyb.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/atakeyb.c

Purpose: Atari IKBD/ACIA keyboard, mouse, joystick, and MIDI interrupt handling plus command helpers.

Important exports include `atari_input_keyboard_interrupt_hook`, `atari_input_mouse_interrupt_hook`, and `atari_keyb_init()`. Optional hook `atari_MIDI_interrupt_hook` lets MIDI serial code participate. The core parser uses `KEYBOARD_STATE` with states `KEYBOARD`, `AMOUSE`, `RMOUSE`, `JOYSTICK`, `CLOCK`, and `RESYNC`.

Interrupt flow repeatedly checks MIDI and keyboard ACIA status, handles overruns by resynchronizing packet state, decodes keyboard make/break scancodes, records broken keys during IKBD self-test, and dispatches keyboard or mouse packets to input hooks. Error bits log communication problems, and the handler loops to drain additional pending bytes.

Command APIs such as `ikbd_write()`, mouse mode/scale/threshold commands, joystick commands, and disable helpers poll ACIA transmit readiness and send fixed IKBD command bytes. `atari_keyb_init()` requests `IRQ_MFP_ACIA`, resets both ACIAs, configures baud/control based on `atari_switches`, enables the interrupt, performs the IKBD self-test, disables mouse/joystick, and marks initialization done.

State includes hook pointers, parser buffer/state, self-test flags/timestamps, `broken_keys`, ACIA hardware registers, and `atari_keyb_done`. Exports integrate with input drivers and optional joystick code.

Risks and test signals: overrun/resync mistakes can interpret mouse bytes as key events; polling writes can take milliseconds; self-test waits spin on jiffies. Test keyboard make/break, mouse relative packets, MIDI hook dispatch, ACIA overrun recovery, and reentrant init calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/atakeyb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/atari.h -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/atari.h

Purpose: local Atari machine support prototypes.

It declares `atari_init_IRQ()`, `atari_microwire_cmd()`, `atari_mksound()`, `atari_sched_init()`, `atari_mste_hwclk()`, and `atari_tt_hwclk()`. It forward-declares `struct rtc_time`.

State/persistence: none in the header. The functions it declares mutate IRQ controller, sound, timer, and RTC hardware state.

Dependencies and integration: used by Atari `config.c`, `ataints.c`, `atasound.c`, and `time.c` to avoid broader architecture header coupling.

Risks and test signals: prototype drift is caught by compilation. Runtime coverage comes from Atari boot with IRQ, beep, and RTC paths enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/atari.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/atasound.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/atasound.c

Purpose: low-level Atari PSG/MICROWIRE sound helpers used for system beep and LM1992 control.

Important APIs are `atari_microwire_cmd(int cmd)` and `atari_mksound(unsigned int hz, unsigned int ticks)`. `atari_microwire_cmd()` writes the LM1992 address plus command to `tt_microwire`, then busy-waits until the mask returns to idle. `atari_mksound()` programs YM2149 generator A frequency, mixer, volume, and optional envelope length.

Control flow disables generator A, clamps the PSG period to 12 bits, writes period low/high registers, chooses either envelope-driven duration or fixed max volume, then re-enables generator A. Local IRQs are disabled while YM registers are selected and written.

State is YM2149 register selection/data, MICROWIRE registers, and no software timer. For finite `ticks`, the PSG envelope hardware determines sound length.

Dependencies include `asm/atarihw.h`, `atari.h`, `HZ`, and machine hook assignment in `config_atari()` when `CONFIG_INPUT_M68K_BEEP` is enabled.

Risks and test signals: busy-waiting MICROWIRE can hang if hardware is absent/misdetected; YM register select/write sequences are not self-describing and require IRQ protection. Test console bell, zero-frequency silence, long tick clamping, and MICROWIRE PSG enable during IRQ initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/atasound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/config.c

Purpose: central Atari machine configuration, hardware probing, machine hook registration, reset, heartbeat, hardware reporting, and platform-device registration.

Important APIs are `atari_parse_bootinfo()`, `config_atari()`, `atari_switches_setup()`, `atari_get_model()`, `atari_get_hardware_list()`, and `atari_platform_init()`. It exports machine cookies, hardware presence, user switch flags, floppy-select guard, and RTC year offset.

Control flow parses bootinfo model cookies and early `switches=` options, installs machdep hooks for scheduler, IRQs, model/hardware list, reset, beep, and heartbeat, then probes hardware registers with `hwreg_present()`/`hwreg_write()`. It sets presence bits for shifters, MFPs, SCSI/DMA, PSG, PCM/CODEC, DSP, SCC/ESCC, SCU/VME, joystick, blitter, IDE, MICROWIRE, clocks, FDC speed, and ACSI fallback. It disables early transparent translation on 040/060 where safe and initializes ST-RAM allocation.

Reset flow handles Medusa/Afterburner quirks, optional ACIA reset for overscan switches, disables IRQs, resets VBR, adjusts 040/060 translation/cache/PCR state, and jumps to firmware reset address. Platform init conditionally registers EtherNAT, EtherNEC/NetUSBee, Atari SCSI, and Falcon IDE platform devices.

State includes hardware presence bitmap, switch flags, TOS-derived RTC year offset, platform resource/device structures, and hardware register side effects. Dependencies include Atari hardware headers, `stram.c`, `time.c`, `ataints.c`, `atasound.c`, debug code, and platform driver APIs.

Risks and test signals: probing can be unsafe on clones; model-specific reset is fragile; platform device detection uses direct `ioremap()`/`hwreg_present()`. Test on ST/STE/TT/Falcon/Medusa-like configs, `switches=` parsing, `/proc/hardware`, ST-RAM pool setup, reboot, and platform device probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/debug.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/debug.c

Purpose: early Atari debug console output over MFP serial, SCC serial, MIDI ACIA, or parallel printer.

Important APIs are early parameter handler `atari_debug_setup()` and initialization helpers `atari_init_mfp_port()`, `atari_init_scc_port()`, and `atari_init_midi_port()`. It exports `atari_SCC_reset_done` so kgdb or other code can prevent duplicate SCC reset.

Control flow: `debug=ser` maps to SCC on Falcon and MFP otherwise; explicit `ser1`, `ser2`, `midi`, and `par` choose output backends. Each backend supplies a `console.write` method that polls device transmit readiness and inserts carriage returns before newlines. Parallel output initializes PSG ports and disables BUSY interrupts, then times out if no printer responds.

State is the `atari_console_driver.write` callback, `atari_SCC_reset_done`, and hardware serial/parallel register configuration. SCC initialization writes many channel B registers with required delays and marks reset complete.

Dependencies include Atari hardware and interrupt headers, early console registration, termios baud constants, `loops_per_jiffy`, and `atari_switches`. Integration is through `early_param("debug", ...)`, allowing logs before full serial drivers bind.

Risks and test signals: polling can hang if readiness bits never change, so parallel has a timeout but serial paths do not. Validate `debug=ser1`, `ser2`, `midi`, and `par` output, Falcon default routing, and kgdb coexistence with `atari_SCC_reset_done`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/nvram.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/nvram.c

Purpose: Atari TT/Falcon-style NVRAM access and `/proc/driver/nvram` reporting.

Important APIs are `atari_nvram_read()`, `atari_nvram_write()`, `atari_nvram_get_size()`, `atari_nvram_initialize()`, and `atari_nvram_set_checksum()`. Internal helpers read/write bytes at `NVRAM_FIRST_BYTE` using CMOS RTC accessors and maintain the Atari checksum over bytes 0-47 with checksum bytes 48-49.

Control flow for reads and writes takes `rtc_lock`, verifies checksum, copies bytes within the fixed 50-byte NVRAM range, updates `*ppos`, and rewrites checksum after writes. Initialization zeroes all bytes and sets checksum. The proc reader snapshots contents under lock, reports checksum status, boot preference, SCSI arbitration/host ID, and Falcon language/date/video preferences.

State is persistent NVRAM/RTC CMOS storage, guarded by the global `rtc_lock` from `time.c`. No separate kernel cache is kept.

Dependencies include `mc146818rtc` CMOS macros, Atari hardware presence, procfs, seq_file, and RTC locking. Integration requires Atari with `TT_CLK`; the proc entry is registered at `device_initcall`.

Risks and test signals: all CMOS access must hold `rtc_lock`; checksum failure prevents reads/writes; proc display assumes a full valid snapshot. Test checksum initialize/set, bounded reads/writes with offsets, concurrent RTC/NVRAM access, and proc output on TT/Falcon configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/stdma.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/stdma.c

Purpose: shared arbitration layer for the Atari ST-DMA interrupt/chip used by floppy, ACSI, IDE interrupt routing, and Falcon SCSI.

Important APIs are `stdma_try_lock()`, `stdma_lock()`, `stdma_release()`, `stdma_is_locked_by()`, `stdma_islocked()`, and `stdma_init()`. A caller acquires the lock with an IRQ handler and data cookie; the common `stdma_int()` invokes that registered handler when `IRQ_MFP_FDC` fires.

State includes `stdma_locked`, `stdma_isr`, `stdma_isr_data`, and wait queue `stdma_wait`. Lock/unlock operations disable local IRQs around state changes. `stdma_lock()` sleeps uninterruptibly until `stdma_try_lock()` succeeds, because users can involve filesystem buffers.

Dependencies include Atari ST-DMA hardware context, `IRQ_MFP_FDC`, Linux wait queues, request_irq, and exported symbols for storage drivers. Integration is initialized from `atari_init_IRQ()`.

Risks and test signals: interrupt handlers must release through their mainline flow; calling `stdma_lock()` from IRQ context is forbidden; `stdma_islocked()` requires interrupts disabled for stable interpretation. Test concurrent floppy/SCSI/ACSI access, lock contention wakeups, handler dispatch, and release-on-error paths in client drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/stdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/stram.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/stram.c

Purpose: allocator for Atari ST-RAM, needed by hardware that can only DMA to the low ST-RAM region.

Important APIs are `atari_stram_init()`, `atari_stram_reserve_pages()`, `atari_stram_to_virt()`, `atari_stram_to_phys()`, `atari_stram_alloc()`, and `atari_stram_free()`. The early parameter `stram_pool=` sets the pool size, defaulting to 1 MiB.

Control flow determines whether the kernel is loaded in ST-RAM by checking the first memory block. If so, `atari_stram_reserve_pages()` uses `memblock_alloc_low()` early and requests the resource. If the kernel is not in ST-RAM, `atari_stram_map_pages()` later reserves a physical pool starting at page 1 and maps it with `ioremap()`, computing a virtual offset. Alloc/free use `allocate_resource()` and `lookup_resource()` inside `stram_pool`.

State includes `kernel_in_stram`, `stram_pool`, `pool_size`, and `stram_virt_offset`. Resource entries track individual allocations.

Dependencies include `m68k_memory`, memblock, ioremap, resource management, Atari hardware assumptions, and exported symbols for DMA-constrained drivers.

Risks and test signals: the non-kernel-in-ST-RAM path skips page 0 because early memory is supervisor-only; wrong offset translation breaks DMA. Test both boot placement modes, `stram_pool=` parsing, allocate/free accounting, and drivers requiring ST-RAM buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/stram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/time.c -->
# sources/distributed-fs/ceph-client/arch/m68k/atari/time.c

Purpose: Atari scheduler clocksource and RTC read/write support.

Important APIs are `atari_sched_init()`, `atari_mste_hwclk()`, `atari_tt_hwclk()`, and exported spinlock `rtc_lock`. Timer C on the ST-MFP supplies scheduler ticks and an `mfp` clocksource. `mfp_timer_c_handler()` updates `last_timer_count`, accumulates `clk_total`, calls `legacy_timer_tick(1)`, and drives heartbeat.

Clocksource flow starts MFP Timer C with `INT_TICKS`, requests `IRQ_MFP_TIMC`, and registers frequency `INT_CLK`. `atari_read_clk()` disables local IRQs, ensures a monotonically decreasing count using `min(st_mfp.tim_dt_c, last_timer_count)`, and returns accumulated ticks.

RTC flow supports MegaSTE RP5C15-style registers through `mste_read()`/`mste_write()` and TT MC146818-style CMOS through `RTC_READ/RTC_WRITE`. `atari_tt_hwclk()` handles UIP polling, `RTC_SET`, BCD/binary mode, 12/24-hour mode, weekday conversion, and `atari_rtc_year_offset`.

State includes `clk_total`, `last_timer_count`, RTC hardware registers, and `rtc_lock` used also by NVRAM. Dependencies include Atari MFP/RTC hardware, bcd helpers, clocksource APIs, and machdep hooks set by `config_atari()`.

Risks and test signals: Timer C wrap handling can momentarily stop but should not go backward; RTC access must avoid UIP windows and coordinate with NVRAM. Test clocksource monotonicity, scheduler ticks, MSTE and TT RTC read/write, 12/24-hour conversion, and concurrent NVRAM access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/atari/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/bvme6000/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/bvme6000/Makefile

Purpose: BVME6000 platform object selection.

It builds `config.o` and `rtc.o`, providing board setup, timer/clocksource, reset, hardware clock, and a misc RTC device driver.

Control flow is Kbuild-only and relies on top-level `Kbuild` selecting `bvme6000/` for `CONFIG_BVME6000`.

State/persistence: no runtime state in the Makefile.

Risks and test signals: omitting `rtc.o` removes `/dev/rtc` support while `config.o` still has `mach_hwclk`; omitting `config.o` breaks board boot. Validate BVME6000 builds and boot initcalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/bvme6000/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/bvme6000/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/bvme6000/config.c

Purpose: BVME4000/BVME6000 board setup, timer clocksource, reset, abort interrupt, and machine hardware clock support.

Important APIs are `bvme6000_parse_bootinfo()`, `config_bvme6000()`, `bvme6000_sched_init()`, `bvme6000_hwclk()`, and `bvme6000_reset()`. Bootinfo parsing recognizes `BI_VME_TYPE`. Board configuration infers `vme_brdtype` from CPU when absent, installs machdep hooks, configures PIT ports, reports system-controller state, and disables snooping for Ethernet/VME accesses.

Timer flow programs DP8570A RTC timer 1 in mode 2 with an 8 MHz clock, requests `BVME_IRQ_RTC`, registers a continuous clocksource, and requests `BVME_IRQ_ABORT`. `bvme6000_timer_int()` acknowledges RTC interrupts, advances `clk_total`, resets `clk_offset`, and calls `legacy_timer_tick(1)`. `bvme6000_read_clk()` repeatedly latches timer state until T1 interrupt/output readings are stable, avoiding rollover/chip fault windows.

State includes PIT/RTC hardware registers, `clk_total`, `clk_offset`, board type, config register state, and vector entries restored by abort handling. `bvme6000_reset()` enables watchdog through PIT port C and spins.

Dependencies include BVME hardware headers, VME bootinfo, generic clocksource/IRQ/machdep APIs, BCD helpers, and vector table symbols.

Risks and test signals: timer read has explicit invalid-read avoidance; changing it can break monotonic time. Abort handler copies vectors from BVMBug ROM addresses and is hardware-specific. Test timer tick/clocksource monotonicity, RTC read/write, abort button behavior, reset watchdog, and board type detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/bvme6000/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/bvme6000/rtc.c -->
# sources/distributed-fs/ceph-client/arch/m68k/bvme6000/rtc.c

Purpose: misc-device `/dev/rtc` interface for the BVME6000 DP8570A real-time clock.

Important functions are `rtc_ioctl()`, `rtc_open()`, `rtc_release()`, and `rtc_DP8570A_init()`. Supported ioctls are `RTC_RD_TIME` and `RTC_SET_TIME`. Reads snapshot BCD RTC fields while ensuring seconds are stable across the read. Writes require `CAP_SYS_ADMIN`, validate month/day/leap-year/hour/min/sec/year bounds, and program BCD fields plus leap-year state.

State is hardware RTC registers and `rtc_status`, an atomic single-open guard initialized to one. `rtc_open()` decrements and tests atomically, returning `-EBUSY` if already open; release increments it.

Dependencies include BVME hardware register definitions, miscdevice APIs, uaccess, BCD conversion, capability checks, and `MACH_IS_BVME6000`. Integration is separate from `mach_hwclk` in `config.c` but accesses the same hardware.

Risks and test signals: concurrent hardware clock and misc RTC access are only locally IRQ-protected, not globally locked with `mach_hwclk`; date validation rejects years >= 2070. Test open exclusivity, read stability, permission failure for unprivileged set, leap-day validation, and matching values between `/dev/rtc` and kernel hwclk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/bvme6000/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/Makefile

Purpose: ColdFire CPU, timer, board, PCI, GPIO, and startup object selection.

The file sets optional debug assembler flags, builds common ColdFire objects (`cache.o`, `clk.o`, `device.o`, `entry.o`, `vectors.o`) for `CONFIG_COLDFIRE`, and chooses CPU-family-specific setup, interrupt controller, and reset objects based on symbols such as `CONFIG_M520x`, `CONFIG_M527x`, `CONFIG_M53xx`, and `CONFIG_M5441x`. It also selects PIT/timer variants, board files such as `amcore.o`, `firebee.o`, and `stmark2.o`, optional PCI, plus always-built `gpio.o` and `head.o`.

Control flow is Kbuild-only. The build graph enforces that each selected ColdFire SOC gets a compatible interrupt controller and reset path.

State/persistence: no runtime state in the Makefile; linked object selection determines available platform devices and low-level CPU code.

Dependencies include ColdFire Kconfig symbols and the corresponding source files. Integration is through top-level `arch/m68k/Kbuild` when `CONFIG_COLDFIRE` is enabled.

Risks and test signals: wrong pairing of SOC file and interrupt controller can compile but fail at boot. Validate representative ColdFire defconfigs, especially combinations for timer choice, PCI, and board files such as AMCORE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/amcore.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/amcore.c

Purpose: Sysam AMCORE board platform-device registration.

Important objects include optional DM9000 Ethernet resources/platform data, NOR flash partitions and physmap platform data, an `rtc-ds1307` platform device, I2C board info for a DS1338 at address `0x68`, and `amcore_devices[]`. `dm9000_pre_init()` marks IRQ 25 as autovectored with `mcf_autovector()`.

Control flow in `init_amcore()` optionally pre-initializes DM9000 interrupt routing, registers I2C RTC board info on bus 0, and calls `platform_add_devices()` for selected devices. It runs as an `arch_initcall`.

State is registered platform devices, flash partition metadata, and autovector configuration. There is no runtime driver logic here after registration.

Dependencies include ColdFire SIM/autovector APIs, platform bus, DM9000, MTD physmap/partition support, I2C board info, and downstream drivers. Integration is selected by `CONFIG_AMCORE` in the ColdFire Makefile.

Risks and test signals: DM9000 resources assume a 32-bit data bus via address/data spacing; flash partition sizes must match board flash; the `rtc_device` is generic while I2C info supplies the actual chip. Test platform device creation, DM9000 IRQ delivery, MTD partition layout, and DS1338 RTC probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/amcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/cache.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/cache.c

Purpose: optional ColdFire data-cache push helper.

When `CACHE_PUSH` is defined, it provides `mcf_cache_push()`, an assembly loop that iterates over cache ways and set offsets and emits the raw opcode word for the ColdFire `cpushl` instruction. It uses `CACHE_LINE_SIZE`, `DCACHE_SIZE`, and `CACHE_WAYS` constants to cover the data cache.

Control flow is a nested assembly loop: clear `d0` for way index, iterate `a0` over lines within each way, execute `cpushl`, increment by cache line size, then advance way count until all ways are pushed.

State affected is CPU cache contents written back to memory. No software state persists.

Dependencies include ColdFire cache geometry macros and assembler compatibility; the raw `.word 0xf468` exists because older GAS versions may not know the mnemonic. Integration is available to low-level cache maintenance callers when `CACHE_PUSH` is configured.

Risks and test signals: wrong geometry constants can miss dirty lines or access invalid cache indices; clobber lists must match assembly use. Test by building with `CACHE_PUSH`, exercising DMA/cache coherency paths, and checking for data corruption around cache writeback-sensitive devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/clk.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/clk.c

Purpose: simple ColdFire clock framework glue for legacy platform clocks.

Important APIs are `clk_enable()`, `clk_disable()`, `clk_get_rate()`, dummy `clk_round_rate()`, `clk_set_rate()`, `clk_set_parent()`, `clk_get_parent()`, and optional power-management helpers `__clk_init_enabled()`/`__clk_init_disabled()` plus `clk_ops0`/`clk_ops1`. Clock enable/disable uses a spinlock and reference count in `struct clk`.

Control flow: `clk_enable()` returns success for NULL, otherwise increments `clk->enabled` and invokes `clk_ops->enable()` only on transition from 0 to 1. `clk_disable()` decrements and invokes disable only on transition to 0. On SoCs with `MCFPM_PPMCR0/1`, ops write the clock slot to power-management control/status registers.

State is per-clock `enabled` count, `rate`, optional `slot`, and power-management hardware registers. The global `clk_lock` serializes reference-count transitions.

Dependencies include `asm/mcfclk.h` clock structures, ColdFire power-management register macros, raw I/O writes, and Linux clk consumers. Integration is used by ColdFire SOC files that define clock lookup tables and operations.

Risks and test signals: underflow in `clk_disable()` is not guarded; dummy rate/parent setters warn if called with a clock, so consumers must not expect full common-clock semantics. Test balanced enable/disable pairs, peripheral probing that depends on clocks, and SoC variants with and without `MCFPM_PPMCR1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/clk.c -->
