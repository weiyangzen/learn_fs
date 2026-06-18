# sources/distributed-fs/ceph-client/arch/alpha/lib/copy_user.S

## Purpose
Generic Alpha `__copy_user` implementation for copying between kernel and user address spaces with precise residual count on faults. The source was read as part of `subset-b-000628` and contains 121 lines.

## Important APIs, Types, and Functions
Exports `__copy_user`; defines separate input and output exception macros `EXI` and `EXO`.

## Control Flow
The routine handles destination byte alignment, then chooses aligned-source quadword copies or unaligned rotating loads, finishes with byte/tail copies, and returns `$0` as bytes remaining. Input faults branch to `$exitin`; output faults branch to `$exitout`, preserving the residual count maintained after successful transfers.

## State and Persistence Behavior
Mutates destination memory, reads source memory, returns residual count, and emits exception-table entries.

## Dependencies
Depends on Alpha uaccess exception machinery, unaligned load/store/extract instructions, calling convention, and Linux usercopy API.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Input and output fault paths must preserve caller-visible counts. Masked tail stores must not overwrite adjacent destination bytes. Alignment paths are dense and easy to break with scheduling changes.

## Test Signals
Run hardened/usercopy tests across every source/destination alignment, inject page faults mid-copy, compare residual bytes and memory contents, and build modules that import `__copy_user`.
