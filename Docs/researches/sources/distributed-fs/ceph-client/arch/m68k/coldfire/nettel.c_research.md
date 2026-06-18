# sources/distributed-fs/ceph-client/arch/m68k/coldfire/nettel.c

Purpose: NETtel board Ethernet setup for two SMC9196/SMC91x interfaces, including early address remap and flash MAC loading.

Important APIs and data: fixed `NETTEL_SMC0/1_ADDR` and IRQs, `nettel_smc91x_0/1_resources`, `nettel_smc91x[]`, `nettel_macdefault[]`, `nettel_smc91x_setmac()`, `nettel_smc91x_init()`, and `init_nettel()`.

Control flow and state: `init_nettel()` calls board hardware setup then registers two `smc91x` platform devices. Setup toggles `MCFSIM_PADDR` and board parallel port data to move one Ethernet chip away from the shared reset address, adjusts chip-select timing, enables autovectoring for both IRQs, and writes MAC addresses into SMC registers from flash or default bytes.

Dependencies and integration: legacy interrupt autovector support, board `mcf_setppdata()` helpers, SMC91x driver, flash layout at `0xf0006000`, and ColdFire SIM chip-select registers.

Risks and test signals: register writes assume exact NETtel hardware and two SMC chips initially aliasing. `nettel_smc91x_setmac()` writes bank select using `NETTEL_SMC0_ADDR` even when programming `ioaddr`, a detail to verify. Test both NICs enumerate with distinct resources/MACs, IRQs fire, and flash-erased MAC fallback works.
