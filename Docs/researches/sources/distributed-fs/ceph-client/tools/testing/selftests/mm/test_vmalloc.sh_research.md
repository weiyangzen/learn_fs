# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_vmalloc.sh

Purpose: wrapper for the `test_vmalloc` kernel module, exposing smoke, performance, stress, and manual parameter modes for vmalloc allocator testing.

Important APIs and functions: presets include `PERF_PARAM`, `SMOKE_PARAM`, `STRESS_PARAM`, and `PCPU_OBJ_PARAM`; `check_memory_requirement()` caps per-CPU object count to 90 percent of available memory per CPU; `validate_passed_args()` verifies manual keys and positive values; run helpers call `modprobe`.

Control flow and state: requires root, `modprobe`, and `CONFIG_TEST_VMALLOC=m`, then dispatches by first argument. It loads `test_vmalloc` with parameters and relies on kernel logs for summaries; it does not explicitly unload the module.

Dependencies and risks: depends on root, module tools, CPU count, `getconf`, and exposed module parameters. Exit status mainly reflects setup, not parsed kernel pass/fail details.
