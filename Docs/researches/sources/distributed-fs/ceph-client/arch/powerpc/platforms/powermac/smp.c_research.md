
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/smp.c

Purpose: implements SMP bring-up, IPI delivery, timebase synchronization, cache handoff, and CPU hotplug behavior for legacy PowerMac systems. It supports the older PowerSurge multiprocessing hardware and the Core99/G4/G5 generation selected by `pmac_setup_smp()`.

Important APIs/types/functions: exports the platform `smp_ops_t` implementations `psurge_smp_ops` and `core99_smp_ops`. PowerSurge paths include `smp_psurge_probe()`, `smp_psurge_kick_cpu()`, `psurge_secondary_ipi_init()`, `psurge_set_ipi()`, and software timebase exchange via `tb_req`/`timebase`. Core99 paths include `smp_core99_probe()`, `smp_core99_kick_cpu()`, `smp_core99_setup_cpu()`, `smp_core99_give_timebase()`, `smp_core99_take_timebase()`, and several hardware timebase-freeze backends: GPIO on 32-bit G4, I2C Cypress/Pulsar on some G5s, and platform-function `cpu-timebase` on newer machines.

Control flow: `pmac_setup_smp()` detects Core99 by `uni-n`, `u3`, or `u4` device-tree nodes and otherwise falls back to PowerSurge when configured. Probe counts or fabricates CPU presence, installs MPIC or custom IPI handling, initializes I2C/platform-function support, and disables 32-bit NAP where unsafe. CPU kick paths patch or write low-level reset/start vectors, briefly hold interrupts, release the target CPU, then restore the vector. Timebase synchronization freezes hardware timebase when possible and falls back to generic software sync.

State and persistence: state is early-boot global kernel state: mapped hardware registers, `smp_ops`, CPU possible/present masks, `pmac_tb_freeze`, I2C host references, `timebase`, `tb_req`, and hotplug callbacks. No persistent storage is written.

Dependencies and integration points: depends on Open Firmware device tree, MPIC, PowerMac feature calls, low-level text patching, early MMIO mappings, KeyLargo GPIO, PMac low I2C, platform functions, CPU feature flags, and generic PowerPC SMP/hotplug helpers. It integrates directly with `ppc_md`, `smp_ops`, MPIC IPI setup, and CPU hotplug state registration.

Risks: very hardware-specific sequencing around reset vectors, IPI registers, and timebase freeze can hang machines if timing or memory ordering changes. PowerSurge paths rely on undocumented physical registers and fabricated CPU topology. Core99 CPU kick temporarily patches the reset vector at `PAGE_OFFSET+0x100`; correctness depends on interrupt exclusion and restoration. Hotplug offline loops deliberately run with unusual interrupt and MMU assumptions.

Test signals: no unit tests are expected. Useful validation is booting SMP-capable PowerMac variants, secondary CPU call-in, synchronized timebase, MPIC IPI delivery, CPU offline/online, cache register consistency on G4, and negative testing on single-CPU or unsupported boards.
