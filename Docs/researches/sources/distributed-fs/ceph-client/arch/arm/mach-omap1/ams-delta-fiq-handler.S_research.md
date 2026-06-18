<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq-handler.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq-handler.S

Purpose: Fast interrupt handler for the Amstrad E3 QWERTY keyboard and selected GPIO interrupts. It runs in FIQ context, samples keyboard clock/data edges, pushes key bits into a shared circular buffer, counts GPIO events, and triggers a deferred IRQ.

Important APIs/types/functions: Symbols are `qwerty_fiqin_start` and `qwerty_fiqin_end`; offsets come from `ams-delta-fiq.h` and platform data headers.

Control flow, state, and persistence: State is the shared `fiq_buffer` addressed through FIQ register r9, GPIO/IRQ controller registers, key state, circular head/tail offsets, counters, and missed-key fields.

Dependencies and integration points: Symbols are `qwerty_fiqin_start` and `qwerty_fiqin_end`; offsets come from `ams-delta-fiq.h` and platform data headers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP1510 GPIO register layout, interrupt-controller virtual addresses, FIQ size limit at vector copy address, and the C initializer. Risks are extremely tight assembly/register coupling, buffer corruption, and edge-count desynchronization. Test keyboard input under load, modem IRQ deferral, buffer overflow counters, and FIQ handler size.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 275 lines, 8813 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq-handler.S -->
