
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_32.S

Purpose: 32-bit PowerPC assembly support for early GOT relocation, CPU setup dispatch, PMac CPU-frequency register switching, optimized page copying, compiler helper routines for 64-bit arithmetic, byte swap, and secondary CPU resume.

Important APIs/types/functions: `reloc_got2`; `call_setup_cpu`; `low_choose_750fx_pll`; `low_choose_7447a_dfs`; `copy_page`; `__ashrdi3`; `__ashldi3`; `__lshrdi3`; `__cmpdi2`; `__ucmpdi2`; `__bswapdi2`; `start_secondary_resume`.

Control flow: `reloc_got2` walks the `.got2` range and adds a relocation offset to each word. `call_setup_cpu` finds `cur_cpu_spec->cpu_setup` using the data offset and branches through CTR when present. PMac frequency helpers disable interrupts, update HID registers and saved HID images, then restore MSR. `copy_page` warns on unaligned destinations, prefetches, uses `dcbz` on destination lines, and unrolls cache-line-sized copies. Arithmetic helpers implement compiler runtime operations on 64-bit values represented in register pairs. SMP resume resets the stack, zeroes the frame pointer, calls `start_secondary`, and spins if it returns.

State and persistence: mutates early GOT entries, CPU HID/HID1 registers, `nap_save_hid1`, destination page memory, and secondary CPU stack/register state.

Dependencies and integration: depends on boot relocation symbols, CPU spec layout, cache-line constants, PMac cpufreq code, compiler-generated helper calls, SMP startup, and feature-fixup headers.

Risks: page copy assumes cacheable aligned destination and correct `L1_CACHE_BYTES`; HID programming is CPU-specific and runs with interrupts disabled; GOT relocation must run before virtual addressing expectations; arithmetic helpers are ABI-visible and must preserve exact return conventions.

Test signals: boot PPC32 relocatable kernels, run memory/page-copy stress, exercise PMac cpufreq transitions, build code that emits 64-bit helper calls, and online secondary CPUs after resume.
