# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/storcenter.c

Purpose: Iomega StorCenter board descriptor for MPC8241-based systems.

Important APIs and control flow: `storcenter_device_probe` publishes `soc` devices. `storcenter_setup_pci` scans `mpc10x-pci` nodes and `storcenter_add_bridge` creates an indirect PCI hose using MPC10x Map B config addresses. `storcenter_init_IRQ` allocates an OpenPIC/MPIC with serial and internal interrupt ISUs. `storcenter_restart` disables interrupts, sets MSR_IP to return toward firmware exception space, and spins.

State, dependencies, and risks: state is limited to machine callbacks and MPIC configuration. Dependencies include OF compatible `iomega,storcenter`, MPC10x bridge constants, indirect PCI, and MPIC. Risks include no real reset assertion beyond high exception prefix/spin, hard-coded Map B config access, and sparse error handling. Test signals are PCI enumeration, OF `soc` device creation, MPIC interrupt delivery, and expected restart behavior on hardware.
