<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/kexec.h

## Purpose
`kexec.h` defines minimal m68k architecture limits and identifiers for the generic kexec core.

## Important APIs, Types, and Functions
When `CONFIG_KEXEC_CORE` is enabled it defines unrestricted source, destination, and control memory limits as `-1UL`, `KEXEC_CONTROL_PAGE_SIZE` as 4096, `KEXEC_ARCH` as `KEXEC_ARCH_68K`, and a stub `crash_setup_regs()`.

## Control Flow, State, and Persistence
There is no real control flow in the stub; crash register capture is not implemented in this header.

## Dependencies and Integration Points
Generic kexec code includes these constants to validate image placement and architecture matching.

## Risks
The unrestricted memory limits are broad and rely on higher-level validation. The dummy crash register setup means crash dump register fidelity is missing or incomplete.

## Test Signals
Build with `CONFIG_KEXEC_CORE`, load a kexec image, and verify reboot into the new kernel. Crash-kexec users need explicit validation that register state expectations are either absent or acceptable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kexec.h -->
