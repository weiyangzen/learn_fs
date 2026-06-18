# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.c

## Purpose
`timerlat_bpf.c` is the userspace libbpf wrapper for RTLA timerlat's BPF collection path. It opens, configures, loads, attaches, reads, restarts, and destroys the generated BPF skeleton, and can load an optional user-provided BPF action program.

## Important APIs, Types, and Functions
When `HAVE_BPF_SKEL` is defined, public functions include `timerlat_bpf_init()`, `timerlat_bpf_attach()`, `timerlat_bpf_detach()`, `timerlat_bpf_destroy()`, `timerlat_bpf_wait()`, `timerlat_bpf_restart_tracing()`, `timerlat_bpf_get_hist_value()`, `timerlat_bpf_get_summary_value()`, and `timerlat_load_bpf_action_program()`. Static globals hold the skeleton `bpf`, optional action `bpf_object *obj`, and `bpf_program *prog`.

## Control Flow
Initialization opens the skeleton, writes rodata parameters from `timerlat_params`, sizes or disables histogram maps, disables summary maps for AA-only mode, and loads/verifies the object. Attach calls skeleton attach. Wait creates a ring buffer on `signal_stop_tracing`, polls for timeout seconds, then frees it. Restart writes zero to the `stop_tracing` map. Map read helpers lookup per-CPU arrays for IRQ/thread/user maps. Action loading opens a BPF object file, loads it, finds a program named `action_handler`, and stores its fd in the skeleton `bpf_action` map.

## State and Persistence
BPF objects, maps, links, and ring buffers are kernel resources owned until destroy/detach. Action program objects remain open while registered. Restart mutates the BPF stop flag.

## Dependencies and Integration Points
It depends on generated `timerlat.skel.h`, libbpf APIs, `timerlat_params`, global `nr_cpus`, and the BPF program maps declared in `timerlat.bpf.c`. Header stubs provide no-op/failure behavior when skeleton support is absent.

## Risks and Edge Cases
`timerlat_bpf_destroy()` calls `timerlat_bpf__destroy(bpf)` without checking `bpf`, so callers should only destroy after successful or partially successful init paths that set it. Ring-buffer creation in `timerlat_bpf_wait()` is not checked before polling. Action program loading requires the exact `action_handler` function name. Per-CPU map lookups expect caller buffers sized for `nr_cpus` `long long` values.

## Test Signals
Test skeleton-enabled and disabled builds, rodata propagation, map sizing/disabling, attach/detach, threshold ring-buffer wakeup, restart map update, histogram/summary reads across CPUs, invalid action object, missing `action_handler`, and destroy after partial failures.
