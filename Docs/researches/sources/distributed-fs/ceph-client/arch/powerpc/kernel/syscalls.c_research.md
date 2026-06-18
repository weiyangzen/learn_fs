# sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls.c

## Purpose
Contains miscellaneous PowerPC syscall implementations with nonstandard ABI behavior: mmap variants, PPC64 personality translation, 64-bit fadvise splitting, and endian switching.

## Important APIs, Types, and Functions
- `do_mmap2()` validates protection with `arch_validate_prot()`, checks offset alignment, and calls `ksys_mmap_pgoff()`.
- `mmap2`, compat `mmap2`, and `mmap` translate 4 KiB or page-size offsets.
- `ppc64_personality` preserves/normalizes `PER_LINUX32` behavior for 32-bit tasks on PPC64.
- `ppc_fadvise64_64` merges split offset/length arguments.
- `switch_endian` toggles the return MSR little-endian bit and sets `_TIF_RESTOREALL`.

## Control Flow and State
Most functions validate ABI-specific arguments and delegate to generic kernel helpers. `switch_endian` directly edits the saved user MSR in `current->thread.regs`, then forces a full register restore so r3/nonvolatile registers are preserved on return.

## State and Persistence Behavior
Persistent effects are from mmap/personality/fadvise syscalls. `switch_endian` persists an endian-mode change in the user return frame and thread flags.

## Dependencies and Integration Points
Depends on syscall table generation, generic `ksys_*` helpers, PowerPC memory protection validation, and MSR return helpers.

## Risks
Offset alignment shifts must match ABI expectations. Endian switching is unusual and can break if return path clobbers registers or fails to restore full state.

## Test Signals
Test `mmap`, `mmap2`, compat `mmap2`, protection-key validation, PPC64 32-bit personality behavior, `ppc_fadvise64_64` with large offsets/lengths, and userspace `switch_endian` round trips.
