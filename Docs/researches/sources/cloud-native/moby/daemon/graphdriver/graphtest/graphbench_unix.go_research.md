# sources/cloud-native/moby/daemon/graphdriver/graphtest/graphbench_unix.go

Purpose: reusable Unix benchmarks for graphdriver implementations.

Important APIs and control flow: benchmark helpers create a temp driver with `GetDriver`, build layers with deterministic helper functions, reset timers around setup, and measure hot operations. They cover `Exists`, `Get`/`Put` on empty layers, base-layer diff streaming, diff on configurable lower/upper file counts, diff/apply loops, deep-layer diff, and deep-layer file reads. Each diff benchmark drains archives to `io.Discard` so backend archive generation work is included.

State, dependencies, and risks: state is the shared graphtest driver and temporary layer trees. Dependencies include test helpers, `stringid`, file IO, and graphdriver APIs. Benchmarks sometimes pass `parent=""` to diff paths, exercising full or fallback diff behavior rather than strictly direct-parent native diff. The diff/apply size comparison is intentionally not enforced, leaving a documented TODO. Signals are comparative performance and basic correctness during benchmark setup.
