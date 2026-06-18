## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump.h

Purpose: exposes the public PowerPC Firmware-Assisted Dump interface and stubs when FADump is disabled.

Important APIs/types/functions: `crashing_cpu`, `is_fadump_memory_area()`, `setup_fadump()`, `is_fadump_active()`, `should_fadump_crash()`, `crash_fadump()`, `fadump_cleanup()`, `fadump_setup_param_area()`, `fadump_append_bootargs()`, `early_init_dt_scan_fw_dump()`, `fadump_reserve_mem()`, and `fadump_cma_init()`.

Control flow: enabled builds reserve memory, parse firmware dump device-tree data, set up parameter areas, append boot arguments for capture kernels, and trigger firmware-assisted crash dumps. Disabled builds compile no-op or false-returning inline stubs.

State and persistence: enabled FADump state includes reserved memory, active dump flags, crash CPU, bootargs, and optional CMA reservation state. The header itself stores no state.

Dependencies and integration: integrates with panic/crash paths, early device-tree scanning, memory reservation, CMA, and FADump internals.

Risks and test signals: stubs must preserve caller behavior when disabled. Enabled paths must not reserve overlapping memory or trigger unwanted dumps. Test signals include builds with `CONFIG_FA_DUMP`, `CONFIG_PRESERVE_FA_DUMP`, CMA combinations, `fadump=on/off`, crash capture boot, and cleanup after processed dumps.
