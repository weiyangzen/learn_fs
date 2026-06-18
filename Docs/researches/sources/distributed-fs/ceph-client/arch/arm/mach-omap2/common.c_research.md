# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.c

Purpose: Provides small common OMAP2+ machine helpers for early memory reservation.

Important APIs/types/functions: Defines weak `omap_secure_ram_reserve_memblock()` returning 0 by default and `omap_reserve()` calling secure RAM and interconnect barrier reservation helpers.

Control flow: Platform early boot calls `omap_reserve()`, which first reserves secure RAM if a SoC-specific override exists, then reserves interconnect barrier memory when configured.

State and persistence: No local persistent state. Effects are memblock reservations made by called helpers.

Dependencies: Includes `common.h` and `omap-secure.h`; relies on `omap_barrier_reserve_memblock()` declaration and optional override of the weak secure reservation function.

Integration points: Part of OMAP2+ early boot memory reservation path.

Risks: Weak default hides missing secure reservation unless SoC code overrides it. Reservation order can matter for low-level secure firmware/barrier memory needs.

Test signals: Boot logs and memblock layout on secure-enabled OMAP platforms; builds with and without interconnect barrier support.
