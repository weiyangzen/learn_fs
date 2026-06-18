# sources/distributed-fs/ceph-client/arch/alpha/lib/clear_user.S

## Purpose
Generic Alpha `__clear_user` implementation that zeroes userspace memory while returning the number of bytes not cleared on fault. The source was read as part of `subset-b-000628` and contains 102 lines.

## Important APIs, Types, and Functions
Exports `__clear_user`; defines `EX` exception-table macro and local loop/tail/exception labels.

## Control Flow
The entry computes destination misalignment, handles a partial head with masked unaligned stores, clears aligned quadwords in groups, writes a masked tail, and updates `$0` only after successful stores. Exception-table entries branch to the return path with `$0` containing bytes left.

## State and Persistence Behavior
Mutates user memory and returns residual byte count in `$0`. Persistent state is exception-table metadata emitted into `__ex_table`.

## Dependencies
Depends on Alpha unaligned load/store instructions, exception-table fixups, uaccess ABI, and exported user-copy helpers.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Residual count must be exact for uaccess callers. Head/tail masking must not zero bytes outside the requested range. Exception annotations must cover every faulting user access.

## Test Signals
Run usercopy tests with aligned, unaligned, zero-length, short, and page-faulting ranges; verify return counts and surrounding bytes; build generic Alpha library path.
