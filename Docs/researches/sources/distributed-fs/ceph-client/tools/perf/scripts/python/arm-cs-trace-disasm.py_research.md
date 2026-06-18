<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/arm-cs-trace-disasm.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/arm-cs-trace-disasm.py
Purpose: Perf script handler for ARM CoreSight traces that prints source lines and optional disassembly for traced instruction ranges. It supports filtering by sample/time ranges and kernel/user DSO resolution.

Important APIs/types/functions: CLI parsing configures vmlinux path, objdump command, verbosity, start/stop time, and start/stop sample. Helpers include `default_objdump`, `find_vmlinux`, `get_dso_file_path`, `read_disam`, `print_disam`, `print_sample`, `common_start_str`, `print_srccode`, and `process_event`. It imports `perf_sample_srccode` and `perf_config_get` from `perf_trace_context`.

Control flow: Perf calls `trace_begin`, `process_event` for each sample, and `trace_end`. `process_event` increments a global sample index, applies filters, stores previous branch target by CPU, ignores non-branch/non-instruction samples as appropriate, computes an address range from consecutive branch samples, validates DSO map bounds, optionally runs objdump for that range, and prints source/symbol context.

State and persistence: Global caches include `disasm_cache`, `cpu_data`, sample index, and last printed source/DSO fields to suppress repeated output. No persistent output; it reads vmlinux/build-id files and invokes external objdump.

Dependencies and integration points: Depends on perf Python script context, `PERF_BUILDID_DIR`, vmlinux/debug files, objdump/llvm-objdump, and CoreSight branch/instruction sample fields. Integrates with perf script `-s`.

Risks: Assumes `PERF_BUILDID_DIR` exists for non-kernel DSOs. Disassembly cache can be cleared wholesale after 64K entries. Address calculations depend on DSO start and map offset conventions. Missing kcore/debug info affects accuracy and source availability.

Test signals: Replay CoreSight perf.data with and without `-d`; verify sample filtering, source output, DSO resolution, and objdump ranges for kernel and user DSOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/arm-cs-trace-disasm.py -->
