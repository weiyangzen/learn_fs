# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-common.h

Purpose: shared IP32 declarations for CRIME initialization, error IRQ handlers, bus-error setup, and poweroff preparation.

Important APIs and control flow: it declares `crime_init()`, `crime_memerr_intr()`, `crime_cpuerr_intr()`, `ip32_be_init()`, and `ip32_prepare_poweroff()`.

State, persistence, and integration: no state; it links CRIME, IRQ, setup, reset, memory, and platform-device code. Dependencies include Linux interrupt types. Risks are close coupling through globals and externally registered platform callbacks. Test signals are compile-time consistency and successful use of these functions across IP32 objects.
