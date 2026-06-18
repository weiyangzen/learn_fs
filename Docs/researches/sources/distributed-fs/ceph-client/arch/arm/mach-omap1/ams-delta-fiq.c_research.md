<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.c

Purpose: C setup and deferred interrupt handling for the Amstrad Delta FIQ keyboard path. It claims the FIQ vector, installs assembly code, initializes the shared buffer, reserves keyboard GPIOs, and forwards FIQ-counted GPIO events into normal IRQ handlers.

Important APIs/types/functions: Important APIs are `ams_delta_init_fiq` and the internal `deferred_fiq` ISR. It uses `claim_fiq`, `set_fiq_handler`, `set_fiq_regs`, `request_irq`, GPIO descriptors, and generic IRQ dispatch.

Control flow, state, and persistence: Persistent state includes `fiq_buffer`, cached GPIO IRQ data, the FIQ handler registration, and per-GPIO IRQ counters. The serio platform device is patched with the keyboard IRQ and buffer pointer.

Dependencies and integration points: Important APIs are `ams_delta_init_fiq` and the internal `deferred_fiq` ISR. It uses `claim_fiq`, `set_fiq_handler`, `set_fiq_regs`, `request_irq`, GPIO descriptors, and generic IRQ dispatch. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include gpio-omap default edge handler behavior, OMAP interrupt registers, the assembly symbols, and AMS Delta board code. Risks are leaked own-desc GPIOs by design, fragile IRQ type programming, and missed event replay if counters wrap. Test keyboard serio probe, GPIO IRQ replay, FIQ claim failure paths, and suspend/resume.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 227 lines, 6704 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.c -->
