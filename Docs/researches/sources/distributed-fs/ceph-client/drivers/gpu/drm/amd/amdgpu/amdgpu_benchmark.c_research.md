# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_benchmark.c

## Purpose
`amdgpu_benchmark.c` provides an internal BO-move benchmark for AMDGPU. It allocates kernel BOs in selected memory domains, repeatedly copies between GPU addresses with the buffer copy engine, waits for fences, and logs throughput for predefined test modes.

## Important APIs, types, and functions
The public entry point is `amdgpu_benchmark(struct amdgpu_device *adev, int test_number)`. Internal helpers are `amdgpu_benchmark_move()`, `amdgpu_benchmark_do_move()`, and `amdgpu_benchmark_log_results()`. Constants define 1024 iterations and a table of 17 common framebuffer-like sizes.

## Control flow
`amdgpu_benchmark()` serializes tests with `adev->benchmark_mutex`, selects one of eight test modes, and calls `amdgpu_benchmark_move()` for fixed 1 MiB copies, powers-of-two GPU page sweeps, or common display-mode-size sweeps across GTT-to-VRAM, VRAM-to-GTT, and VRAM-to-VRAM directions. Each move creates source and destination kernel BOs, obtains GPU addresses, locks the default memory-management entity, loops over `amdgpu_copy_buffer()`, waits each returned fence, measures elapsed time with `ktime_get()`, logs throughput, and frees both BOs.

## State and persistence behavior
The file allocates temporary kernel BOs and fences only for the duration of each benchmark. It writes no persistent state; output is kernel log messages. `adev->benchmark_mutex` is the only long-lived state it uses.

## Dependencies and integration points
It depends on AMDGPU BO allocation/free helpers, the default VM/memory-management entity, `amdgpu_copy_buffer()`, DMA fences, domain constants, GPU page size, and kernel timing/logging. It is typically driven by AMDGPU debug/module benchmark plumbing rather than normal rendering paths.

## Risks and edge cases
Throughput divides by elapsed milliseconds; extremely fast runs could risk division by zero, although 1024 iterations normally avoids that. Benchmark results include fence wait overhead and serialization through the default entity, so they are diagnostic rather than pure bandwidth. If `adev->mman.buffer_funcs` is unavailable, BOs are created but no copy/log result is produced. Cleanup can overwrite error values, so the code logs the error before freeing.

## Test signals
Signals include running all benchmark IDs 1-8, invalid test-number `-EINVAL`, BO allocation failure injection, copy/fence wait failure handling, domains with and without VRAM, availability of buffer functions, and checking that repeated benchmarks free BOs and fences cleanly.
