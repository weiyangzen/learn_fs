# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/Makefile

## Purpose
This Makefile maps Renesas Ethernet Kconfig symbols to kernel objects and declares the composite object membership for the AVB and R-Switch drivers.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_SH_ETH) += sh_eth.o` builds the SuperH Ethernet driver.
- `ravb-objs := ravb_main.o ravb_ptp.o` composes the `ravb.o` module/built-in object from the main AVB implementation and its PTP support file.
- `obj-$(CONFIG_RAVB) += ravb.o` links the composite AVB driver.
- `rswitch-objs := rswitch_main.o rswitch_l2.o` composes the R-Switch driver from its main implementation and switchdev L2 offload support.
- `obj-$(CONFIG_RENESAS_ETHER_SWITCH) += rswitch.o`, `obj-$(CONFIG_RENESAS_GEN4_PTP) += rcar_gen4_ptp.o`, and `obj-$(CONFIG_RTSN) += rtsn.o` map the remaining symbols to objects.

## Control Flow
Kbuild includes this file after Kconfig resolves symbols. For composite modules, Kbuild compiles each listed `*-objs` member and links them into the named object. `ravb_ptp.o` is always part of `ravb.o` when `CONFIG_RAVB` is enabled, while `rcar_gen4_ptp.o` is a separate shared object selected by R-Switch and RTSN.

## State And Persistence
The file has no runtime state. Its persistent effect is build graph structure: which translation units are linked together and which symbols are exported or local within each module/built-in object.

## Dependencies And Integration Points
It consumes symbols from `Kconfig` and integrates with the kernel top-level kbuild system. Source-level integrations include `ravb_main.c` calling functions from `ravb_ptp.c`, `rswitch_main.c` calling functions from `rswitch_l2.c`, and R-Switch/RTSN using exported symbols from `rcar_gen4_ptp.c`.

## Risks And Edge Cases
- Composite object membership means `ravb_ptp.c` must compile whenever `RAVB` compiles, even when PTP clock support is optional.
- `rswitch_l2.o` is always linked with `rswitch.o`; missing switchdev dependencies must be handled through Kconfig or includes.
- `rcar_gen4_ptp.o` is not automatically linked into `rswitch.o`; callers rely on Kconfig selecting a separate object/module and on exported GPL symbols.

## Test Signals
Build each symbol as `y` and `m`, inspect generated modules for `ravb`, `rswitch`, `rcar_gen4_ptp`, and `rtsn`, and confirm link errors do not occur for cross-file calls such as `ravb_ptp_init()`, `rswitch_register_notifiers()`, and `rcar_gen4_ptp_register()`.
