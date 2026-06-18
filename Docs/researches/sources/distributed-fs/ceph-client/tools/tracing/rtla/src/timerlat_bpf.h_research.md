# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_bpf.h

## Purpose
`timerlat_bpf.h` defines the shared summary-map indexes for timerlat BPF collection and provides the userspace BPF API, with real prototypes when BPF skeleton support is compiled in and inline failure stubs otherwise.

## Important APIs, Types, and Functions
`enum summary_field` indexes current, min, max, count, sum, overflow, and field count. Under `HAVE_BPF_SKEL`, the header declares init/attach/detach/destroy/wait/restart/map-read/action-load functions and `have_libbpf_support()`. Without skeleton support, it defines inline stubs returning failure or no-op values so the rest of RTLA can compile and fall back to tracefs.

## Control Flow and Integration
`timerlat.c` probes BPF availability by calling `timerlat_bpf_init()` and falls back when it fails. Timerlat top/hist modes use the map-read APIs when operating in BPF mode.

## State and Persistence
The header owns no state, but its APIs manage BPF skeleton kernel resources and summary/histogram maps in the implementation.

## Dependencies and Integration Points
The userspace declarations are hidden from BPF compilation with `#ifndef __bpf__`, while the enum remains available to `timerlat.bpf.c`. This keeps map indexes consistent across kernel BPF and userspace.

## Risks and Edge Cases
Consumers must tolerate stub failures and not assume libbpf support. Summary enum ordering is ABI-like between BPF program and userspace readers; reordering would corrupt interpretation of map values.

## Test Signals
Build with and without `HAVE_BPF_SKEL`, verify fallback behavior, and confirm BPF/userspace agree on every summary field index.
