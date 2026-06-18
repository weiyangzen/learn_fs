# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/setup.c

Purpose: Defines the PS3 machine setup and lifecycle hooks. It initializes firmware version state, SPU/SMP hooks, early memory and hash page table setup, preallocated PS3 framebuffer/flash buffers, firmware sysfs reporting, power management, restart/poweroff/halt/panic behavior, and kexec CPU teardown.

Important APIs/types/functions: Exports `ps3_gpu_mutex`, `ps3_get_firmware_version()`, `ps3_compare_firmware_version()`, `ps3fb_videomemory`, and `ps3flash_bounce_buffer`. Key local functions are `ps3_power_save()`, `ps3_restart()`, `ps3_power_off()`, `ps3_halt()`, `ps3_panic()`, `prealloc()`, early params `ps3fb` and `ps3flash`, `ps3_set_dabr()`, `ps3_setup_sysfs()`, `ps3_setup_arch()`, `ps3_early_mm_init()`, `ps3_probe()`, and `ps3_kexec_cpu_down()`.

Control flow: `define_machine(ps3)` binds platform callbacks. Probe saves OS-area parameters and installs `pm_power_off`; setup reads LV1 version info, formats `fw-version`, installs SPU and SMP support, preallocates optional buffers, sets `ppc_md.power_save`, and initializes the OS area. Early MM setup initializes PS3 memory, VAS, and HPTE state. Shutdown paths stop secondary CPUs and call PS3 system manager operations that do not return.

State and persistence: Persistent state includes the exported GPU mutex, firmware version union/string, preallocation descriptors whose addresses are assigned through memblock, and machine callback table entries. Sysfs exposes firmware version under the firmware kobject. Panic loops in LV1 pause after flushing kernel messages.

Dependencies and integration points: Integrates with LV1 calls, PS3 OS-area code, PS3 MM/HPTE setup, PS3 IRQ code, PS3 SPU code, SMP setup, framebuffer and flash drivers, firmware sysfs, PowerPC `ppc_md`, and kexec hooks.

Risks: The preallocation sizes are parsed very early and consume memblock memory permanently. `ps3_set_dabr()` silently masks unsupported DABRX bits. Lifecycle hooks assume system-manager calls never return. Kexec teardown must clean per-CPU IPIs and IRQ state without racing with remaining CPUs.

Test signals: PS3 boot to userspace, `/sys/firmware/ps3/fw-version`, framebuffer/flash module load using preallocated buffers, DABR/debug watchpoint tests, panic/restart/poweroff behavior, SMP boot, and kexec/crash shutdown are primary signals.

Source read size: 302 lines, 6737 bytes.
