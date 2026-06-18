# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/sysctrl.c

Purpose: maps Falcon system-control register blocks, initializes core clocks, enables the GPE/ONU core, and registers clkdev gates for platform devices.

Important APIs/functions: `ltq_soc_init`, `sysctl_activate`, `sysctl_deactivate`, `sysctl_clken`, `sysctl_clkdis`, `sysctl_reboot`, `falcon_gpe_enable`, and `clkdev_add_sys`. Global MMIO bases include `ltq_sys1_membase` and `ltq_ebu_membase`.

Control flow: `ltq_soc_init()` locates required DT nodes (`status`, `ebu`, `sys1`, `syseth`, `sysgpe`), requests/remaps resources, enables the GPE frequency path based on fuses, registers static CPU/FPI/IO clocks based on CPU divider, and adds device-specific clock gates for GPIO, pad, serial, and other modules.

State and persistence: stores ioremapped base pointers and early-allocated `struct clk` objects in clkdev. Register writes persist in SoC clock/reset hardware until reset.

Dependencies and integration: called by `plat_time_init()`; depends on OF resources, Lantiq MMIO helpers, `clkdev`, and Falcon DT compatible strings.

Risks: missing DT core nodes or failed remaps panic. Activation wait loops are fixed-count busy waits. Allocated clock structures are intentionally never freed.

Test signals: Falcon boot reaches timer init, clk lookups for registered device names succeed, GPE clock comes up, and system-control operations do not timeout.
