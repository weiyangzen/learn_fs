# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.h

Purpose: local declarations for Hollywood PIC initialization, IRQ lookup, and quiesce operations used by Wii board code.

Important APIs and control flow: declares `hlwd_pic_get_irq`, `hlwd_pic_probe`, and `hlwd_quiesce`. There is no inline behavior.

State, dependencies, and risks: state is owned by `hlwd-pic.c`. Dependencies are `__init` annotations and Wii object inclusion. Risks are link failures if Wii board code is compiled without `hlwd-pic.o`. Test signals are compile/link coverage and successful Wii interrupt setup.
