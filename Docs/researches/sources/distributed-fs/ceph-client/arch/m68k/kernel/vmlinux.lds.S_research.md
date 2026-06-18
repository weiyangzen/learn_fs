# sources/distributed-fs/ceph-client/arch/m68k/kernel/vmlinux.lds.S

## Purpose

`vmlinux.lds.S` selects the m68k top-level linker script variant for the final kernel image.

## Important APIs, Types, and Functions

For MMU non-ColdFire builds it defines two loadable program headers, `text` and `data`, both with flags 7, then includes either `vmlinux-sun3.lds` or `vmlinux-std.lds`. For no-MMU or ColdFire builds it includes `vmlinux-nommu.lds`.

## Control Flow

There is no runtime flow. The preprocessor selects the linker script according to `CONFIG_MMU`, `CONFIG_COLDFIRE`, and `CONFIG_SUN3`.

## State and Persistence Behavior

It controls link-time section layout and ELF program headers. That layout determines boot symbol addresses used by `head.S`, setup code, and memory initialization.

## Dependencies and Integration Points

It depends on included linker scripts and Kconfig. `head.S` assumes symbols such as `_stext`, `_end`, and `kernel_pg_dir` are placed consistently with this selection.

## Risks and Edge Cases

Wrong script selection can place sections at addresses incompatible with early boot, especially Sun3 page-size and no-MMU flat-memory cases. PHDR flag changes can affect bootloader loading permissions.

## Test Signals

Inspect linked `vmlinux` map and program headers for MMU, Sun3, ColdFire, and no-MMU configs. Boot tests should confirm `_stext`, `_end`, and init sections match startup expectations.
