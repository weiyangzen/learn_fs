<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.h

Purpose: Internal AMS Delta FIQ header that connects board setup with the assembly handler. It declares handler symbol bounds and the FIQ initialization entry point.

Important APIs/types/functions: Visible declarations are `qwerty_fiqin_start`, `qwerty_fiqin_end`, and `ams_delta_init_fiq(struct gpio_chip *, struct platform_device *)`.

Control flow, state, and persistence: There is no state in the header; it describes interfaces to C and assembly state managed elsewhere.

Dependencies and integration points: Visible declarations are `qwerty_fiqin_start`, `qwerty_fiqin_end`, and `ams_delta_init_fiq(struct gpio_chip *, struct platform_device *)`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are declaration mismatch with assembly labels or platform device expectations. Test build/link of AMS Delta with FIQ enabled.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 42 lines, 1101 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.h -->
