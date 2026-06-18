# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch.h

## Purpose
This header defines the Renesas Ethernet Switch driver's register map, descriptor formats, queue constants, per-port and global state structures, forwarding/L2 offload register bits, MMIO helpers, and cross-file prototypes shared by `rswitch_main.c` and `rswitch_l2.c`.

## Important APIs, Types, And Functions
- Global constants and iteration helpers: `RSWITCH_NUM_PORTS`, `RSWITCH_NUM_AGENTS`, `RSWITCH_MAX_NUM_QUEUES`, ring sizes, MTU/buffer sizing, `rswitch_for_all_ports()`, and enabled-port iteration macros.
- Register ABI: `enum rswitch_reg` covers forwarding engine, TOP, COMA, ETHA/RMAC, and GWCA register offsets.
- Register field macros: ETHA modes, GWCA modes, MDIO fields, interrupt register calculators, forwarding fields (`FWPC0/1/2`, `FWPBFC`, `FWMACAG*`), descriptor info fields, and timestamp descriptor extractors.
- Descriptor types: `struct rswitch_desc`, `struct rswitch_ts_desc`, `struct rswitch_ext_desc`, and `struct rswitch_ext_ts_desc`.
- Hardware state: `struct rswitch_etha`, `struct rswitch_gwca_queue`, `struct rswitch_gwca`, `struct rswitch_device`, `struct rswitch_mfwd`, and `struct rswitch_private`.
- Cross-file APIs: `is_rdev()` identifies R-Switch netdevs, and `rswitch_modify()` updates MMIO registers with clear/set masks.

## Control Flow
The header is declarative, but it shapes the R-Switch driver flow. `rswitch_main.c` allocates `rswitch_private`, initializes `rswitch_etha` ports and `rswitch_gwca` queues, registers one netdev per enabled port, uses descriptor types for Tx/Rx/timestamp rings, and exports `is_rdev()`/`rswitch_modify()` for `rswitch_l2.c`. `rswitch_l2.c` uses the port list, bridge/offload fields in `rswitch_device`, and forwarding register macros to turn bridge STP state into hardware learning and forwarding configuration.

## State And Persistence
All structures are runtime state. `rswitch_private` stores the platform device, MMIO base, shared Gen4 PTP provider, per-port pointers, opened-port bitmap, GWCA/ETHA state, forwarding table metadata, port list, interrupt lock, clock, halt/runtime-change flags, selected offload bridge, and hwtstamp settings. `rswitch_device` stores one netdev's queue pointers, NAPI, timestamp skb slots, port number, PHY/serdes state, bridge master, and L2 learning/forwarding requested/offloaded flags. Hardware register state persists only until reset/reconfiguration.

## Dependencies And Integration Points
The header depends on platform device, PHY, netdevice/NAPI types through includers, and `rcar_gen4_ptp.h`. It is the primary coupling point between main R-Switch data-path code, shared PTP support, and switchdev L2 offload code. Kbuild links `rswitch_main.o` and `rswitch_l2.o` into one `rswitch.o` object, so prototypes here define the internal boundary.

## Risks And Edge Cases
- The register enum is a large hardware ABI; typos or wrong offsets can program unrelated forwarding, interrupt, or MAC registers.
- Iteration macros depend on `priv->rdev[i]` being valid before checking `disabled`; initialization order must guarantee that.
- `struct rswitch_mfwd` refers to `struct rswitch_mac_table_entry *`, while this header defines `struct rswitch_mfwd_mac_table_entry`; that naming mismatch deserves build/context verification.
- Bridge offload fields are bitfields updated by notifier/open/stop paths without obvious locking in `rswitch_l2.c`; concurrency assumptions rely on netdevice/switchdev notifier serialization.
- Descriptor pointer fields split high and low DMA address bits, so DMA mask and descriptor packing must match hardware expectations.

## Test Signals
Compile R-Switch under `COMPILE_TEST`, validate register offsets against hardware documentation, bring up all enabled ports, exercise Tx/Rx and timestamp rings, verify PTP registration through `rcar_gen4_ptp`, test bridge join/leave and STP transitions, inspect L2 forwarding register writes, run suspend/resume/remove, and check that disabled-port iteration avoids null or uninitialized `rdev` access.
