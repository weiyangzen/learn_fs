# sources/distributed-fs/ceph-client/arch/x86/lib/kaslr.c

Purpose: provides early x86 entropy mixing for KASLR base and memory randomization, usable both in the compressed boot environment and regular kernel.

Important APIs/functions: defines `kaslr_get_random_long(const char *purpose)`. Internal `i8254()` reads the PIT counter as fallback entropy. Non-compressed builds map debug and feature helpers to regular kernel equivalents and use `kaslr_offset()` as boot seed.

Control flow: starts with a boot seed, optionally prints the purpose and entropy sources, mixes in RDRAND if available and successful, mixes in RDTSC if available, otherwise falls back to i8254 PIT reads. It then multiplies by an architecture-width diffusion constant, adds the high product half, prints completion if requested, and returns the mixed value.

State and persistence behavior: no persistent local state. Reads CPU random/TSC/PIT sources and boot seed. Writes debug output through early printing when requested.

Dependencies/integration points: used by compressed kernel and early normal kernel KASLR code. Depends on archrandom, TSC, E820/setup, shared IO port access, CPU feature checks, and early debug output.

Risks: early boot environment restricts available APIs. Entropy quality can be weak without RDRAND/TSC; PIT fallback is last resort. IO port reads must wait until status is ready. The function is not a cryptographic RNG; it is entropy mixing for address randomization.

Test signals: compressed and regular kernel builds, boot logs showing selected sources, CPU-feature matrix tests, i8254 fallback on minimal emulation, and KASLR offset variability checks.
