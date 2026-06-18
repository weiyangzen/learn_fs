# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_probe.c

Purpose: provides low-level CPU PRID detection helper for Loongson diagnostics and potential host-specific behavior.

Important APIs/types/functions: PRID masks/shifts/constants and `loongson_cpu_get_prid`.

Control flow: depending on architecture, inline assembly reads LoongArch `cpucfg` PRID or MIPS CP0 PRID, extracts implementation and revision bytes if output pointers are provided, and returns raw PRID.

State and persistence: no persistent state. Debugfs uses the returned values for display.

Dependencies and integration points: used by `lsdc_debugfs.c` `chips` file. Compile-time architecture guards select assembly path.

Risks and test signals: on unsupported architectures under `COMPILE_TEST`, PRID remains zero. Test LoongArch and MIPS builds/runs, plus compile-test on other architectures.
