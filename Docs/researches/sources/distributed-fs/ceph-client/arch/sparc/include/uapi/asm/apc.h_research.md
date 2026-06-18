<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/apc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/apc.h

Purpose: User ABI for the Aurora Personality Chip power-management driver on SPARCstation-4/5 style systems.

Important APIs and control flow: defines APC ioctl base `'A'`, get/set commands for fan control, convenience-power outlet, and bit ports, plus register offsets and bit values consumed by `arch/sparc/kernel/apc.c`. The ioctl payloads are integer-sized from the UAPI perspective, while the driver masks values to APC register-width bits.

State, dependencies, and risks: persistent state is in hardware APC registers, not the header. Dependencies include Linux ioctl encoding and the APC misc driver. Risks are ABI value changes, exposing platform-dependent bit ports to userspace, and confusion between active-low values such as `APC_CPOWER_ON`/`OFF`. Test signals are ioctl compatibility tests against `/dev/apc`, fan and outlet state reads/writes, and invalid-command rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/apc.h -->
