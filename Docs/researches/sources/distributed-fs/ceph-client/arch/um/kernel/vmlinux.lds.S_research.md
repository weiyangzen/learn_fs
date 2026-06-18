# sources/distributed-fs/ceph-client/arch/um/kernel/vmlinux.lds.S

## Purpose
Selects the UML top-level linker script variant and defines kernel stack size for the link.

## Important APIs, Types, and Functions
Defines `RUNTIME_DISCARD_EXIT` and `KERNEL_STACK_SIZE = 4096 * (1 << CONFIG_KERNEL_STACK_ORDER)`. Includes `uml.lds.S` when `CONFIG_LD_SCRIPT_STATIC` is set, otherwise includes `dyn.lds.S`.

## Control Flow, State, and Persistence
No runtime control flow. Its output affects the final vmlinux layout and stack-size-dependent linker symbols.

## Dependencies and Integration Points
Integrated by Kbuild as the architecture linker script. It selects between static and dynamic UML link layouts.

## Risks and Test Signals
Risks are stack-size mismatch and wrong static/dynamic script selection. Test static and dynamic UML builds with different `CONFIG_KERNEL_STACK_ORDER` values.
