# sources/distributed-fs/ceph-client/drivers/platform/mips/ls2k-reset.c

Purpose: Early Loongson-2K1000 reset and poweroff support. It maps the platform PM register block from device tree and installs machine restart and power-off hooks.

Important APIs, types, and functions: `ls2k_restart()` writes `0x1` to `RST_CNT`; `ls2k_poweroff()` clears PM status then writes sleep type and sleep enable bits to `PM1_CNT`; `ls2k_reset_init()` finds the `loongson,ls2k-pm` node, maps its first resource with `of_iomap()`, assigns `_machine_restart` and `pm_power_off`, and is registered with `arch_initcall()`.

Control flow: during arch init, the driver locates the PM node. Missing node yields `-ENODEV`; mapping failure yields `-ENOMEM`. On success, future restart/poweroff flows enter the static callbacks and directly program the PM registers.

State and persistence: only static `base` persists for the mapped PM register region. No cleanup path is present because the code is built as early platform support. Hardware register writes are one-shot and do not persist beyond platform power state.

Dependencies and integration points: depends on Open Firmware address mapping, `asm/reboot.h` for `_machine_restart`, and Linux PM global `pm_power_off`. It integrates through device-tree compatible `loongson,ls2k-pm`.

Risks: hooks are installed globally and overwrite any prior restart/poweroff implementation without arbitration. There is no unmap or owner tracking, appropriate for arch init but risky if platform probing order changes. `ls2k_poweroff()` writes a broad status clear and sleep control value, so register definitions must match the exact SoC.

Test signals: boot with a DT node for `loongson,ls2k-pm`, confirm mapping succeeds, and test `reboot` and `poweroff` on LS2K hardware or an emulator with observable PM writes. Negative tests should omit the node and verify no hooks are installed.
