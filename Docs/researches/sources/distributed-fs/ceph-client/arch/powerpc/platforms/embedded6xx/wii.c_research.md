# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/wii.c

Purpose: Nintendo Wii machine descriptor and board control for Hollywood MMIO, reset, poweroff, interrupt controller composition, and platform-device population.

Important APIs and control flow: `wii_setup_arch` maps Hollywood control and GPIO blocks and turns off slot LED and sensor bar. `wii_restart` clears the system reset bit in the control reset register; `wii_power_off` assigns the shutdown GPIO to the ARM side, makes it output, drives it high, and spins. `wii_pic_probe` initializes both Flipper and Hollywood PICs, while `define_machine(wii)` uses Flipper as top-level `get_irq`. Device probing populates `nintendo,hollywood` children.

State, dependencies, and risks: state is `hw_ctrl`, `hw_gpio`, `pm_power_off`, and Flipper/Hollywood PIC globals. Dependencies include OF Hollywood control/GPIO/PIC nodes, GPIO ownership semantics shared with Starlet, udbg, and OF platform population. Risks include missing MMIO nodes causing reset/power commands to degrade to spin-only, GPIO ownership assumptions, and separate PIC quiesce ordering at shutdown. Test signals are Wii machine match, LED/sensor-bar state, interrupt delivery through both PICs, platform devices, and reset/poweroff hardware behavior.
