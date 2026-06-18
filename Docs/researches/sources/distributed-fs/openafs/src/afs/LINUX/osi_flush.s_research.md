# sources/distributed-fs/openafs/src/afs/LINUX/osi_flush.s

## Purpose
This PowerPC64 assembly file exports `flush_cache(addr, len)`, a low-level helper that flushes data cache and invalidates instruction cache over an address range.

## Important APIs, types, and functions
- `flush_cache` is an ELFv1-style function descriptor in `.opd` pointing to `.flush_cache`.
- `.flush_cache` iterates cache-line-sized chunks, performing `dcbf` and `icbi`, then issues `sync` and `isync`.

## Control flow and behavior
The function rounds the requested length up by adding `0x1f`, shifts to count 32-byte cache lines, exits immediately when the count is zero, and loops over each line flushing data cache and invalidating instruction cache at the current address. It advances by `0x20` bytes and finishes with synchronization barriers.

## State and persistence
It mutates processor cache state only. There is no OpenAFS memory or disk state.

## Dependencies and integration points
The code is architecture-specific PowerPC64 assembly borrowed from Linux boot code. It is expected by Linux/PPC64 AFS code paths that need explicit instruction/data cache coherency.

## Risks
The code assumes 32-byte cache-line granularity and old PPC64 ABI/function descriptor conventions. Incorrect use on kernels/architectures with different ABI or cache geometry would be unsafe. There is no runtime validation.

## Test signals
Build/link tests on the intended PPC64 ABI are the main signal. Runtime validation should exercise any caller that writes executable or code-like data and then invokes this flush before execution or probing.
