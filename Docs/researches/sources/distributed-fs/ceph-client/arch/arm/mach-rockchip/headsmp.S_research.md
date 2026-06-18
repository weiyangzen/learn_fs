# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/headsmp.S

Purpose: minimal secondary CPU trampoline copied into Rockchip SRAM.

Important APIs/types/functions: defines `rockchip_secondary_trampoline`, global `rockchip_boot_fn`, and `rockchip_secondary_trampoline_end`.

Control flow: the trampoline loads the PC from the embedded boot-function word, causing a released secondary CPU to branch to `secondary_startup`.

State and persistence: `rockchip_boot_fn` storage is patched by C before the code is copied to SRAM.

Dependencies and integration points: consumed by `rockchip_smp_prepare_sram()` in `platsmp.c`.

Risks: alignment and range boundaries matter because code is copied as raw bytes. A bad physical address prevents secondary CPU boot.

Test signals: secondary CPU online, trampoline size check against SRAM reservation, and cache clean after copy.
