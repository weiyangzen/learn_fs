# sources/distributed-fs/ceph-client/arch/m68k/kernel/sun3-head.S

## Purpose

`sun3-head.S` is the Sun-3-specific bootstrap for the older Sun3 MMU/page-size model. It replaces the standard 4 KiB page-table startup with Sun3 context/segment-map initialization and then enters the common kernel path.

## Important APIs, Types, and Functions

The file exports `_stext`, `_start`, `kernel_pg_dir`, `swapper_pg_dir`, `pg0`, `kernel_pmd_table`, `availmem`, `m68k_pgtable_cachemode`, `bootup_user_stack`, `bootup_kernel_stack`, and `kpt`. It uses constants from `<asm/contregs.h>` and `<asm/sun3-head.h>` such as context registers, segment map entries, and control-space function codes.

## Control Flow

Startup disables interrupts, sets source/destination function codes to control space, forces context zero, disables caches, builds the early Sun3 mapping structures, initializes kernel/user boot stacks, records initial available memory, and transfers to common C setup after the Sun3 MMU state is usable. The assembly uses 8 KiB page constants and Sun3 invalid PMEG handling rather than the normal 4 KiB 68030/040 table walkers.

## State and Persistence Behavior

It statically reserves early tables in the image and persists `availmem`, page-directory/table symbols, stack symbols, and cache-mode state. It programs Sun3 control registers and segment mappings that remain active into C setup.

## Dependencies and Integration Points

It depends on Sun3-specific MMU/control-register headers, entry offsets, linker placement, and common setup code that expects `kernel_pg_dir`/`availmem` symbols. It is selected by the Sun3 build instead of the generic `head.S` path.

## Risks and Edge Cases

Sun3 uses 8 KiB pages and PMEG/context hardware, so generic MMU assumptions cannot be applied blindly. Static table reservations marked with comments as BSS candidates must remain correctly linked and aligned. Incorrect control function-code setup can make early MMU register accesses hit normal memory or fault.

## Test Signals

Sun3 boot should reach C setup, show valid memory and MMU type in `/proc/cpuinfo`, and survive early page faults. Emulator traces should show context zero and segment maps programmed before enabling normal execution.
