# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/core.h

Purpose: shared declarations for Rockchip secondary CPU trampoline code.

Important APIs/types/functions: declares `rockchip_secondary_trampoline`, `rockchip_secondary_trampoline_end`, and mutable `rockchip_boot_fn`.

Control flow: no code; `platsmp.c` copies the trampoline range to SRAM and writes `rockchip_boot_fn` with the physical `secondary_startup` address.

State and persistence: `rockchip_boot_fn` is a word embedded in assembly and patched before copying to SRAM.

Dependencies and integration points: bridges `headsmp.S` and `platsmp.c`.

Risks: symbol range arithmetic and physical address patching must match assembly layout exactly.

Test signals: SMP boot on A9 Rockchip, objdump symbol order, and SRAM copy size validation.
