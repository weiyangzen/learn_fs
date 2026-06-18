# sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace-mem-types.h

## Purpose
Defines memory-accounting identifiers for the `debug/trace` translator.

## Important APIs, types, and functions
The `gf_trace_mem_types_` enum starts at `gf_common_mt_end + 1`, defines `gf_trace_mt_trace_conf_t` for the trace configuration object, and ends with `gf_trace_mt_end`.

## Control flow
The trace implementation uses this enum when initializing memory accounting and allocating private trace configuration state.

## State and persistence behavior
No runtime state is held in the header. The enum affects memory-accounting diagnostics only.

## Dependencies and integration points
Includes `glusterfs/mem-types.h` and is listed as a private header in `trace/src/Makefile.am`. It is expected to be consumed by `trace.c` and possibly `trace.h`.

## Risks and test signals
If trace gains more allocation categories, this enum must stay synchronized with `mem_acct_init()` and allocation call sites. Test signals include successful trace memory-accounting initialization and leak reports tagged with the trace type.
