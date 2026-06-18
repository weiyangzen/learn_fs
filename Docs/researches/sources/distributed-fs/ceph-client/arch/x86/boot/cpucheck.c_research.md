# sources/distributed-fs/ceph-client/arch/x86/boot/cpucheck.c

Purpose: performs low-level early CPU capability validation for setup code without normal kernel services.

Important APIs and state: exports `check_cpu()` and `check_knl_erratum()`. Static data includes `err_flags[]`, required family `req_level`, and `req_flags[]` assembled from `REQUIRED_MASK*` macros. Vendor helpers compare raw CPUID vendor words.

Control flow: `check_cpu()` clears `cpu.flags`, assumes 386, probes AC flag for 486+, loads CPUID flags, computes missing flags, treats LM as level 64, and applies vendor-specific fixups: enabling AMD SSE/SSE2 through K7 HWCR, enabling VIA CX8, unmasking Transmeta flags, and optional `forcepae` for affected Pentium M models. It then checks the Xeon Phi KNL non-PAE 32-bit erratum and returns failure on insufficient level or missing flags.

Dependencies and integration: used by `cpu.c`, depends on boot `cpuflags.c`, command-line parsing, raw MSR access, and generated cpufeature masks.

Risks and test signals: raw MSR writes can be hazardous if vendor/model detection is wrong; `loaded_flags` behavior in `cpuflags.c` means repeated probes after attempted feature enabling need careful coordination. Test with QEMU CPU models for AMD, VIA/Centaur, Transmeta-like paths if available, Pentium M `forcepae`, and 32-bit KNL erratum guard.
