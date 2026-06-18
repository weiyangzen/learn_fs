# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/emergency-restart.h

This header delegates emergency restart support to `asm-generic/emergency-restart.h`. It has no Alpha-specific implementation.

Integration is with panic/reboot paths. Risks are only that generic restart may not capture platform-specific PAL/SRM restart needs; platform-specific shutdown hooks live elsewhere. Test signal is build coverage and reboot/panic behavior on supported Alpha systems.
