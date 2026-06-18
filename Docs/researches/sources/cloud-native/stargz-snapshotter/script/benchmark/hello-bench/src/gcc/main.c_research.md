# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/gcc/main.c

Purpose: Tiny C workload used by the GCC benchmark image.
Important APIs/types/functions: `main` prints `hello` with `printf`.
Control flow: compiled and run inside the `gcc:11.2.0` container by `hello.py` stdin commands.
State and persistence: no persistent state.
Dependencies and integration points: depends on a C compiler in the benchmark image and bind-mounted source directory.
Risks: only validates startup and simple compilation, not meaningful application behavior.
Test signals: benchmark succeeds when compile/run exits zero and prints output.
