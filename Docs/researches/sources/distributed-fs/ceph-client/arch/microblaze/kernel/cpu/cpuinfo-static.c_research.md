# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cpuinfo-static.c

Purpose: builds `struct cpuinfo` from device-tree properties and Kconfig constants when PVR is missing or as the baseline before full-PVR correction.

Important APIs and state: `set_cpuinfo_static()` consumes `xlnx,*` CPU properties through `fcpu()`, compares selected values with `CONFIG_XILINX_MICROBLAZE0_*`, and maps version/family strings through `cpu_ver_lookup` and `family_string_lookup`.

Control flow: instruction, multiply, FPU, exception, cache, bus, FSL, IRQ, debug, user PVR, MMU, and endian fields are filled from DTS. Missing cache line properties are defaulted using legacy FSL-cache hints. Version and FPGA-family codes are derived from compile-time strings, and a MicroBlaze 3/non-Spartan2 fixup forces hardware multiplier information.

State and persistence: only the supplied `cpuinfo` is updated; there is no allocation. The populated values persist as the architecture-wide hardware contract for cache, exception, clock, and procfs code.

Dependencies and integration: called by `setup_cpuinfo()` for no-PVR and unsupported-PVR cases, and before `set_cpuinfo_pvr_full()` for full-PVR systems. Depends on DTS property naming and Kconfig matching the bitstream.

Risks and test signals: stale DTS or kernel config can select invalid cache/TLB behavior. Missing cache-line properties fall back heuristically. Test with DTBs for old and new MicroBlaze IP, verifying mismatch logs and `/proc/cpuinfo`.
