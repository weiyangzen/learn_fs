<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/secure_cntvoff.S -->
# sources/distributed-fs/ceph-client/arch/arm/common/secure_cntvoff.S

## Purpose
Secure-mode helper that initializes the ARM architectural timer virtual offset register `CNTVOFF` to zero.

## Important APIs/types/functions
- Entry symbol `secure_cntvoff_init`.
- Uses Monitor mode, SCR non-secure bit, `mcrr p15, 4, ..., c14` to write `CNTVOFF`, and returns to SVC mode.

## Control flow
The routine switches to Monitor mode, reads Secure Configuration Register, sets SCR.NS, writes zero to `CNTVOFF`, restores the original secure configuration, switches back to SVC mode, and returns.

## State and persistence behavior
It mutates secure architectural CPU state: SCR transiently and CNTVOFF persistently for the CPU until reset or later firmware/kernel writes.

## Dependencies and integration points
Requires ARMv7 virtualization extensions and execution privilege that permits Monitor-mode SCR/CNTVOFF access. Built for `CONFIG_CPU_V7` and used by platforms that need kernel-side virtual timer offset initialization.

## Risks and edge cases
Running this when TrustZone firmware owns secure state can be unsafe. CPUs lacking virtualization extensions or Monitor access will fault. SMP systems need per-CPU consideration if each CPU has separate timer offset state.

## Test signals
Boot affected ARMv7 platforms and verify virtual counter behavior, timer interrupts, and absence of undefined-instruction or monitor-mode faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/secure_cntvoff.S -->
