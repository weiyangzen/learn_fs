# sources/distributed-fs/ceph-client/kernel/profile.c

## Purpose
`profile.c` implements legacy kernel profiling. It parses boot-time `profile=` configuration, allocates a direct-mapped atomic counter buffer for kernel text samples, records CPU/scheduler/KVM profiling hits, and exposes binary data through `/proc/profile` when procfs is enabled.

## Important APIs, types, and functions
Global state includes exported `prof_on`, `prof_buffer`, `prof_len`, and `prof_shift`. `profile_setup()` parses numeric, `schedule`, and `kvm` modes. `profile_init()` sizes and allocates the buffer. `profile_hits()` and `profile_tick()` update counters. Procfs support is implemented by `read_profile()`, weak `setup_profiling_timer()`, `write_profile()`, `profile_proc_ops`, and `create_proc_profile()`.

## Control flow
At boot, `profile_setup()` selects profiling mode and sample shift. `profile_init()` computes the number of buckets over `_stext.._etext`, tries `kzalloc()`, `alloc_pages_exact()`, then `vzalloc()`, and disables profiling if the shift leaves no buckets. At runtime, `profile_tick()` samples the interrupt register PC for kernel-mode ticks, while other code can call `profile_hits()`. Proc reads return the sample step followed by raw atomic counters; writes reset counters and optionally set an architecture-specific profiling timer multiplier.

## State and persistence behavior
Profile counters persist in memory for the running boot until reset through `/proc/profile`. Data is binary and direct-mapped by `(pc - _stext) >> prof_shift`; collisions are expected at coarse shifts. No on-disk state is maintained.

## Dependencies and integration points
The file integrates boot parameters, kernel text section symbols, IRQ register access, architecture `profile_pc()`, scheduler stats, procfs, user copy helpers, memory allocators, and weak architecture override of `setup_profiling_timer()`.

## Risks and invariants
The buffer must cover only kernel text and must not be used before allocation. `prof_shift` must be clamped to avoid undefined shifts. Proc read offsets mix an `unsigned int` header with `atomic_t` counters, so size calculations must remain consistent with the historical readprofile ABI. Writes reset all counters and can alter profiling timer frequency only where supported.

## Test signals
Boot with `profile=N`, `profile=schedule,N`, and `profile=kvm,N`; verify allocation success/failure paths, `/proc/profile` size and binary header, counter increments on kernel workload, write reset behavior, and architecture timer multiplier error handling.
