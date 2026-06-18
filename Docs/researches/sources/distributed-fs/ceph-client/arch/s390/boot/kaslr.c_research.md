<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kaslr.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/kaslr.c

Purpose: Provides early entropy and placement selection helpers for s390 kernel address space layout randomization. It chooses a CPACF-backed random source and computes a valid randomized physical placement within usable memory while avoiding reserved ranges and dynamic boot allocations.

Important APIs/types/functions: Defines PRNG mode constants for TDES, SHA512, and TRNG, local `struct prno_parm` and `struct prng_parm`, `get_random()`, and `randomize_within_range()`. Internal helpers include `check_prng()`, `sort_reserved_ranges()`, and `iterate_valid_positions()`.

Control flow: `get_random()` probes CPACF support. It prefers true random (`cpacf_trng`), then SHA512 DRNG via PRNO seed/generate, then the older TDES PRNG via KMC after mixing TOD-clock entropy. `randomize_within_range()` snapshots `physmem_info.reserved`, sorts reservations, clamps the maximum to `get_physmem_alloc_pos()`, counts all aligned valid positions across usable physical ranges, draws one random position, and iterates again to return the selected address.

State and persistence: The file keeps no persistent global state. It reads current physical memory ranges, reservation arrays, and `physmem_alloc_pos`; all random parameters are stack-local and discarded after use.

Dependencies and integration points: Integrated by `startup.c` for physical vmlinux and amode31 placement and for virtual kernel placement entropy. It depends on CPACF query and instruction wrappers, TOD clock access, `physmem_info`, reservation types, and the boot logging path.

Risks: A zero or unsupported PRNG disables randomization by returning failure. Modulo reduction in `get_random()` can bias slot selection, though the placement domain is boot-only. Reservation handling must match `physmem_info.c` allocation semantics; missing a static reservation can cause overlap with initrd, IPL report certificates, decompressor storage, or relocated kernel image.

Test signals: Boots with `kaslr` enabled across machines with TRNG, SHA512 DRNG, and TDES-only CPACF support; forced allocation pressure; randomized vmlinux placement avoiding initrd/IPL report ranges; and fault-injection where CPACF support is absent or `get_random()` fails.

Source read size: 198 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kaslr.c -->
