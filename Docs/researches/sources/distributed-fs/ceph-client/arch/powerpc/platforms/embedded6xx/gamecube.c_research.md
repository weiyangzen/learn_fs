# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/gamecube.c

Purpose: Nintendo GameCube machine descriptor and board-level reset, power, interrupt, debug, and OF platform-device population hooks.

Important APIs and control flow: `gamecube_probe` installs `pm_power_off` and initializes optional USB Gecko udbg. Restart disables interrupts, calls `flipper_platform_reset`, and spins; power-off only spins until external action. `define_machine(gamecube)` uses Flipper PIC init/get_irq and `udbg_progress`. A `machine_device_initcall` probes OF platform buses compatible with `nintendo,flipper`.

State, dependencies, and risks: state is `pm_power_off` plus Flipper and USB Gecko global state. Dependencies include the `nintendo,gamecube` compatible string, Flipper PIC, OF platform bus, and udbg hooks. Risks are intentional infinite spins for poweroff/halt, reliance on reset MMIO being mapped, and no fallback interrupt controller. Test signals are machine match, early debug output, device population, interrupt handling, and reset behavior.
