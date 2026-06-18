<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/setup.h

## Purpose
Declares the architecture setup hook used to process the boot-time device tree before the generic kernel setup path needs platform data.

## Important APIs, Types, And Functions
Exports `void __init or1k_early_setup(void *fdt);` for C code and includes `asm-generic/setup.h`. The declaration is hidden from assembly.

## Control Flow
`head.S` calls `or1k_early_setup()` after enabling the MMU and validating the FDT magic. The implementation selects the passed FDT or the built-in DTB and calls early device-tree scanning.

## State And Persistence
The header stores no state. It introduces the function that seeds global OF/FDT and memblock reservation state.

## Dependencies And Integration Points
Depends on Linux init annotations and the generic setup interface. It links the assembly boot path with `kernel/setup.c`.

## Risks
The signature is part of the assembly/C boot contract. Changing it without updating `head.S` breaks early boot.

## Test Signals
OpenRISC boot with external and built-in DTBs should report the selected FDT and reach `setup_arch()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/setup.h -->
