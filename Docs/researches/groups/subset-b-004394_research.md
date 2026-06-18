# Research: subset-b-004394

Grouped research for Chelsio T1/T2 `cxgb` and T3 `cxgb3` Ethernet driver files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/sge.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/sge.h

## Purpose
`sge.h` is the public header for the first-generation Chelsio `cxgb` scatter-gather engine. It defines the minimal statistics structures and entry points that the adapter core, interrupt layer, NAPI poller, and netdev transmit path use to manage DMA queues.

## Important APIs, Types, And Functions
- `struct sge_intr_counts` exposes software-maintained interrupt/error counters: receive allocation drops, pure responses, spurious interrupts, response/free-list queue empty or overflow conditions, oversized packets, packet mismatches, and command queue full/restart counts for three command queues.
- `struct sge_port_stats` exposes per-port data-path offload counters: RX checksum successes, TX checksum and TSO requests, VLAN extraction/insertion, and SKBs requiring additional header room.
- Lifecycle/configuration APIs are `t1_sge_create`, `t1_sge_configure`, `t1_sge_set_coalesce_params`, and `t1_sge_destroy`.
- Interrupt and polling APIs are `t1_interrupt`, `t1_interrupt_thread`, `t1_poll`, `t1_sge_intr_enable`, `t1_sge_intr_disable`, `t1_sge_intr_clear`, and `t1_sge_intr_error_handler`.
- Data-path APIs are `t1_start_xmit`, `t1_vlan_mode`, `t1_sge_start`, `t1_sge_stop`, and `t1_sched_update_parms`.
- Readout APIs are `t1_sge_get_intr_counts` and `t1_sge_get_port_stats`.

## Control Flow And State
This header does not implement control flow; it defines the SGE contract consumed by `cxgb` board setup and interrupt code. `subr.c` calls SGE creation during software module initialization, calls `t1_sge_configure` during hardware initialization, clears/enables/disables SGE interrupts as part of global interrupt transitions, and asks `t1_sge_intr_error_handler` whether an SGE error needs threaded handling.

## Dependencies And Integration Points
The header depends on Linux interrupt, type, byte-order, NAPI, `sk_buff`, `net_device`, and `netdev_features_t` definitions. It is intentionally opaque around `struct sge`; callers hold only pointers. It integrates with the `adapter` object, netdev transmit path, VLAN feature toggling, interrupt threading, and per-port statistics collection.

## Risks And Edge Cases
SGE errors include fatal conditions such as response queue overflow and packets too large. The interrupt counters mix hardware IRQ events and host-side command queue backpressure, so callers must interpret them as operational diagnostics rather than pure hardware MIBs. The API assumes implementation-side locking around queues and register access; this header alone gives no ownership rules.

## Test Signals
Useful signals include successful adapter probe/remove without SGE allocation leaks, NAPI receive/transmit traffic, checksum/TSO/VLAN offload counters changing under matching workloads, command queue restart behavior under TX pressure, and fatal SGE error paths waking the threaded interrupt handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/sge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/subr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/subr.c

## Purpose
`subr.c` provides shared support routines for the Chelsio T1/T2 `cxgb` driver: TPI register access, MDIO access through Elmer0 MI1, board tables, EEPROM/VPD reads, link setup, slow interrupt dispatch, board initialization, and adapter software/hardware module bring-up and teardown.

## Important APIs, Types, And Functions
- `t1_wait_op_done` polls an MMIO register bit until a requested polarity appears, used for TPI transactions.
- `__t1_tpi_write`, `t1_tpi_write`, `__t1_tpi_read`, and `t1_tpi_read` implement unlocked and locked TPI access through `A_TPI_ADDR`, `A_TPI_WR_DATA`, `A_TPI_RD_DATA`, and `A_TPI_CSR`.
- `t1_link_changed` reads PHY link status, updates `struct link_config`, programs MAC speed/duplex/flow control when autonegotiation has settled, and calls the OS-specific `t1_link_negotiated`.
- `t1_pci_intr_handler`, `fpga_slow_intr`, `asic_slow_intr`, and `t1_slow_intr_handler` dispatch slow-path interrupt causes across SGE, TP, ESPI, external MAC/PHY, and PCI-X errors.
- `mi1_mdio_init`, `mi1_mdio_read/write`, and `mi1_mdio_ext_read/write` implement Clause 22 and indirect Clause 45 style MDIO over Elmer0.
- `t1_board` and `t1_pci_tbl` map PCI IDs to `board_info` entries for T110/N110/N210/T210 and optional 1G N204 boards.
- `t1_get_board_info`, `t1_seeprom_read`, `vpd_macaddress_get`, `t1_link_start`, `t1_elmer0_ext_intr_handler`, `t1_interrupts_enable/disable/clear`, `t1_get_board_rev`, `t1_init_hw_modules`, `t1_free_sw_modules`, and `t1_init_sw_modules` are the exported board/module services.

## Control Flow And State
Probe-time flow starts with board identification via `t1_pci_tbl` and `t1_get_board_info`, then `t1_init_sw_modules` stores board parameters, creates SGE/ESPI/TP state, runs `board_init`, initializes MDIO, optionally resets global PHY/MAC blocks, creates each port's `cphy` and `cmac`, obtains MAC addresses from VPD or the MAC, initializes link config, records PCI mode, and clears interrupts. Hardware module setup then runs `t1_init_hw_modules`, which prepares MC4/MC5 fallback state if no MC4 clock exists, initializes ESPI, resets/configures TP, and configures SGE.

Link start uses `t1_link_start`: if the PHY supports autonegotiation it computes pause advertisement, advertises it, then either forces speed/duplex/flow-control or enables autonegotiation. Non-autoneg PHYs are reset after MAC flow-control programming. Runtime link changes are delivered through PHY interrupt handlers into `t1_link_changed`.

Interrupt flow is split between fast SGE data interrupts elsewhere and slow causes in this file. ASIC slow interrupts are masked by `adapter->slow_intr_mask`, then fan out to SGE error handling, TP, ESPI, PCI-X, and external interrupts. External interrupts are moved to the threaded handler by setting `adapter->pending_thread_intr`, masking `F_PL_INTR_EXT`, and returning `IRQ_WAKE_THREAD`. FPGA builds use separate cause bits and quirks.

## State And Persistence Behavior
Persistent hardware state includes TPI-programmed external MAC/PHY registers, Elmer0 GPIO/TPI parameters, MDIO configuration, EEPROM/VPD contents, and PCI config interrupt/status registers. Software state includes `adapter->params`, per-port `phy`, `mac`, and `link_config`, `slow_intr_mask`, and `pending_thread_intr`. EEPROM reads are read-only and require 4-byte alignment within an 8 KiB space.

## Dependencies And Integration Points
The file depends on `common.h`, Elmer0 registers, Terminator registers, GMAC/PHY/SGE/TP/ESPI operation tables, Linux PCI config helpers, spinlocks, delays, and netdev address helpers. It integrates the board table with lower-level MAC and PHY drivers such as PM3393, VSC7326, Marvell PHYs, MY3126, SGE, TP, and ESPI. OS-specific callbacks include `t1_link_negotiated`.

## Risks And Edge Cases
TPI and MDIO operations can time out; failures are logged and sometimes returned as generic nonzero errors. PCI-X errors are treated as fatal and disable interrupts. External interrupt handling requires process context, so masking/re-enabling must remain paired. Board table values encode clocks, GPIOs, PHY base addresses, and MAC/PHY operation tables; wrong entries can misprogram hardware. VPD MAC derivation increments only the final byte, which assumes a contiguous base address range.

## Test Signals
Probe tests should cover each board ID mapping, VPD read failure handling, MAC/PHY allocation cleanup, and successful interrupt clear/enable/disable cycles. Runtime signals include MDIO reads/writes succeeding under `tpi_lock`, link up/down and autonegotiation changes reaching `t1_link_negotiated`, PCI-X error injection disabling interrupts, SGE error interrupts waking the thread, and ESPI/TP interrupt handlers being invoked only when present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/suni1x10gexp_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/suni1x10gexp_regs.h

## Purpose
`suni1x10gexp_regs.h` is a register and bit-mask map for the PMC/Sierra S/UNI-1x10GE-XP PM3393 MAC/PHY used by the Chelsio `cxgb` driver. It provides symbolic addresses and masks for global reset/status, MDIO, 10G RX/TX MAC blocks, XAUI, OAM, PL4/SPI4 interfaces, FIFO provisioning, performance counters, and interrupt/status bits.

## Important APIs, Types, And Functions
This file contains macros only. Key macro groups include:
- Offset helpers for exact match filters, VLAN filters, and MSTAT counters: `mSUNI1x10GEXP_MAC_FILTER_OFFSET`, `mSUNI1x10GEXP_MAC_VID_FILTER_OFFSET`, and `mSUNI1x10GEXP_MSTAT_COUNT_OFFSET`.
- Register address constants from top-level device registers (`IDENTIFICATION`, `CONFIG_AND_RESET_CONTROL`, `MASTER_INTERRUPT_STATUS`, `GLOBAL_INTERRUPT_ENABLE`) through SERDES, RXXG/XRF/RXOAM/MSTAT/IFLX/PL4/TXXG/XTEF/TXOAM/EFLX/PL4IDU blocks.
- Dynamic register address macros for exact match address/VID registers and MSTAT counters.
- Bit-mask helpers for fixed-width fields, clearing high bits, and testing bits.
- Detailed bit masks and bit offsets for reset, loopback, device status, MDIO command/address fields, master interrupt causes, XAUI/SERDES events, RX/TX MAC controls, OAM controls, PL4 lock/error conditions, FIFO limits, and counter control.

## Control Flow And State
There is no executable control flow. The file models PM3393 state by naming hardware registers and fields. Driver code using it typically reads/writes these addresses over TPI/MDIO-like external register paths, updates MSTAT snapshots, programs MAC address filters, enables/disables RX/TX paths, and handles block-specific interrupt causes.

## Dependencies And Integration Points
It is consumed by PM3393-related MAC support in the `cxgb` tree. The names align with the vendor datasheet and allow other driver code to avoid magic offsets. Register groups map to integration points with Elmer0/TPI access, the MAC receive/transmit path, address filtering, XAUI link detection, SPI4/PL4 datapath setup, and MSTAT statistics.

## Risks And Edge Cases
The file is dense and vendor-derived, so the primary risks are incorrect offsets, stale datasheet assumptions, or confusing similarly named interrupt enable/status/visibility registers. Some macros expose raw bit masks without typed helpers, so callers must apply shifts consistently. Dynamic macros assume valid filter/counter IDs; bounds are not enforced by the preprocessor.

## Test Signals
Validation comes indirectly from PM3393 driver behavior: reset/status reads returning expected IDs, MAC address filters accepting/rejecting traffic as configured, RX/TX enable and MTU changes taking effect, MSTAT counters matching traffic, and block interrupt status bits matching link/fault events. Static build coverage should catch missing macro names but not semantic address mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/suni1x10gexp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.c

## Purpose
`tp.c` implements the `cxgb` Terminator Protocol Engine wrapper. It owns a small `struct petp` backpointer to the adapter, programs TP input/output/global configuration, manages TP interrupts for ASIC and optional FPGA builds, toggles IP/TCP checksum offload bits, and resets the TP block.

## Important APIs, Types, And Functions
- `struct petp` stores the owning `adapter_t`.
- `tp_init` programs `A_TP_IN_CONFIG`, `A_TP_OUT_CONFIG`, and `A_TP_GLOBAL_CONFIG`, including checksum validation/generation, offload disable when protocol memory is absent, default TTL, path MTU behavior, five-tuple lookup, SYN cookie parameter, and T2 pause-deadlock drop controls.
- `t1_tp_create`/`t1_tp_destroy` allocate/free TP software state.
- `t1_tp_intr_enable`, `t1_tp_intr_disable`, `t1_tp_intr_clear`, and `t1_tp_intr_handler` manage TP interrupt enables/causes for both ASIC and `CONFIG_CHELSIO_T1_1G` FPGA cases.
- `set_csum_offload`, `t1_tp_set_ip_checksum_offload`, and `t1_tp_set_tcp_checksum_offload` update `A_TP_GLOBAL_CONFIG`.
- `t1_tp_reset` initializes configuration then writes `F_TP_RESET` to `A_TP_RESET`.

## Control Flow And State
`t1_tp_create` is called during `t1_init_sw_modules`, while `t1_tp_reset` is called during `t1_init_hw_modules`. The reset path calls `tp_init` first, then asserts TP reset. Interrupt enable/disable manipulates both TP-local registers and the top-level PL interrupt enable register. ASIC builds intentionally enable the PL TP interrupt while setting `A_TP_INT_ENABLE` to zero because no TP-specific interrupts are used. FPGA builds use FPGA-specific TP interrupt enable/cause addresses.

## State And Persistence Behavior
Software state is limited to the adapter pointer. Hardware state is persistent in TP MMIO registers until reset or reconfiguration. Checksum offload toggles mutate `A_TP_GLOBAL_CONFIG` in place. T2 multi-port boards get TX-drop/deadlock prevention parameters derived from `tp_clk`.

## Dependencies And Integration Points
The file depends on `common.h`, `regs.h`, `tp.h`, and optionally `fpga_defs.h`. It integrates with `subr.c` for TP lifecycle, global interrupt enable/disable/clear, slow interrupt dispatch, and adapter hardware initialization. It also depends on `tp_params` fields such as `pm_size` and `use_5tuple_mode` as defined in the first-generation driver common headers.

## Risks And Edge Cases
ASIC and FPGA interrupt behavior diverges sharply. `t1_tp_intr_handler` clears whatever TP cause is present but returns 0 on ASIC, so callers must not expect detailed cause decoding. Offload disable is derived from protocol memory size; a wrong parameter can disable TOE-related processing. Pause-deadlock avoidance only applies to T2 multi-port ASICs.

## Test Signals
Signals include successful TP reset during probe, expected `A_TP_*` register values after initialization, checksum offload bits toggling from feature changes, slow interrupt handling clearing TP causes, and T2 multi-port tests verifying drop-deadlock programming when pause is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.h

## Purpose
`tp.h` is the public interface for the first-generation Chelsio Terminator Protocol Engine. It defines TP MIB statistic layout, a receive coalescing maximum, opaque TP state, and the lifecycle/control APIs implemented by `tp.c`.

## Important APIs, Types, And Functions
- `TP_MAX_RX_COALESCING_SIZE` sets a 16224-byte TP receive coalescing limit.
- `struct tp_mib_statistics` mirrors hardware IP and TCP MIB counters, with high/low pairs for wide counters and scalar TCP state/timer counters.
- `struct petp` and `struct tp_params` are forward declarations.
- Public functions are `t1_tp_create`, `t1_tp_destroy`, `t1_tp_intr_disable`, `t1_tp_intr_enable`, `t1_tp_intr_clear`, `t1_tp_intr_handler`, `t1_tp_set_tcp_checksum_offload`, `t1_tp_set_ip_checksum_offload`, and `t1_tp_reset`.

## Control Flow And State
This header exposes no implementation, but its APIs describe TP control flow: allocate TP state, reset/program the hardware block, enable/clear/handle/disable TP interrupts as adapter state changes, toggle checksum offload bits, and destroy state on removal or failed initialization.

## Dependencies And Integration Points
The header includes `common.h` for `adapter_t`, `u32`, and TP parameter definitions. It is consumed by adapter initialization and interrupt code in `subr.c`, by TP implementation in `tp.c`, and by any diagnostics collecting TP MIB statistics.

## Risks And Edge Cases
The MIB structure must match hardware register layout exactly; reordering or type changes would corrupt stats reads. The API is opaque around locking and register access, so callers must rely on implementation-side synchronization. The coalescing limit is a hardware constraint and should not be raised without validating descriptor/data-path limits.

## Test Signals
Build tests should catch prototype drift between `tp.h` and `tp.c`. Runtime signals include stable TP initialization, checksum offload feature toggles, interrupt handling during slow interrupt tests, and correctly decoded IP/TCP MIB counters under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/tp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/vsc7326.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/vsc7326.c

## Purpose
`vsc7326.c` implements the Vitesse VSC7326/Schaumburg MAC support for first-generation Chelsio boards, exposed as `t1_vsc7326_ops`. It handles TPI-based MAC register access, full and per-port reset sequences, BIST, FIFO/SPI4/watermark setup, MAC address filters, RX mode, MTU, speed/duplex/flow-control programming, enable/disable, and RMON/statistics accumulation.

## Important APIs, Types, And Functions
- `struct init_table` stores register/value initialization scripts.
- `struct _cmac_instance` stores the port index and statistics tick count.
- `vsc_read`/`vsc_write` perform 32-bit VSC register access as paired 16-bit TPI transactions under `adapter->mac_lock`.
- `vsc7326_full_reset`, `vsc7326_reset`, and `vsc7326_portinit` encode global and per-port initialization sequences.
- `run_table` executes initialization scripts, with `INITBLOCK_SLEEP` support.
- `bist_rd`, `bist_wr`, `run_bist`, `check_bist`, `enable_mem`, and `run_bist_all` exercise and re-enable selected MAC memories.
- `mac_set_address`, `mac_get_address`, `mac_reset`, `mac_set_rx_mode`, `mac_set_mtu`, `mac_set_speed_duplex_fc`, `mac_enable`, `mac_disable`, `mac_update_statistics`, and `mac_destroy` implement `struct cmac_ops`.
- `vsc7326_mac_create` allocates `struct cmac` plus private instance state, and `vsc7326_mac_reset` performs full chip reset/BIST/global init.

## Control Flow And State
Board setup calls `t1_vsc7326_ops.reset`, which toggles Elmer0 GPIO reset, waits for `REG_SW_RESET` to clear, runs memory BIST, and writes global setup registers. Per-port creation allocates a `cmac`, assigns `vsc7326_ops`, and samples local status until the MAC is responsive. Per-port reset writes one of the four `vsc7326_portinit` tables. Link changes call `mac_set_speed_duplex_fc`, which validates speed/duplex, updates mode, device setup, debug, IFG, and pause registers. `mac_enable` changes egress watermarks from the disabled workaround value to the enabled value and sets RX/TX bits; `mac_disable` resets the port, clears RX/TX bits, clears hardware stats, and zeroes software stats.

## State And Persistence Behavior
Hardware state lives in VSC registers reached through TPI. Software state includes `cmac->stats` and the private tick counter. Statistics are accumulated from 32-bit RMON registers into 64-bit software counters; octet counters update on every tick and full counter sets update on full or major ticks. MAC address programming also updates ingress frame filter mask registers.

## Dependencies And Integration Points
The file depends on `gmac.h`, `elmer0.h`, and `vsc7326_reg.h`, and uses `t1_tpi_read/write` from `subr.c`. It plugs into board entries whose `gmac` is `&t1_vsc7326_ops`, particularly optional multi-port 1G boards. Its `cmac_ops` are used by generic `cxgb` link, RX mode, MTU, enable/disable, and statistics paths.

## Risks And Edge Cases
`vsc_read` waits up to 50 polls for local status and logs but still reads data if the loop times out. Initialization tables contain hardware-specific magic values and flow-control watermarks; wrong values can hang traffic or cause pause issues. BIST helper validation is mostly logging and returns success, so failures may not stop probe. The MAC interrupt hooks are no-ops, which is acceptable only if VSC interrupts are unused or handled elsewhere.

## Test Signals
Signals include successful global reset completion, BIST logs free of errors, port enable/disable changing traffic state, RX promiscuous mode changing filtering, MTU programming affecting max frame length, speed/duplex/flow-control changes matching link settings, and monotonically increasing 64-bit software counters under sustained traffic including wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/vsc7326.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/vsc7326_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/vsc7326_reg.h

## Purpose
`vsc7326_reg.h` defines the register address map for the Vitesse VSC7321/VSC7326 MAC used by the `vsc7326.c` driver. It provides the `CRA` encoder plus symbolic names for system, aggregator, BIST, FIFO, SPI4, 10GbE, tri-speed MAC, statistics, MIIM, and ingress filter registers.

## Important APIs, Types, And Functions
- `CRA(blk, sub, adr)` composes the VSC register address from block, sub-block, and register fields.
- System/CPU communication registers include chip ID, reset, memory BIST, interface mode, PLL/sys clocks, GPIO, local data, and local status.
- FIFO macros parameterize ingress/egress and FIFO number: `REG_TEST`, `REG_TOP_BOTTOM`, `REG_HIGH_LOW_WM`, `REG_CT_THRHLD`, `REG_CONTROL`, and related SRAM/debug registers.
- SPI4 registers cover setup, status, deskew, pattern generator/checker, sticky, debug, and grant/status values.
- MAC registers cover 10GbE-specific state and tri-speed per-port registers such as `REG_MODE_CFG`, `REG_PAUSE_CFG`, `REG_MAX_LEN`, `REG_MAC_HIGH_ADDR`, `REG_MAC_LOW_ADDR`, `REG_DEV_SETUP`, `REG_DBG`, and `REG_TX_IFG`.
- The statistics enum names RMON counter indices used by `vsc7326.c`, with helper macros for byte counters.
- Ingress filter macros include unicast/multicast enable, values, masks, and ethertype registers.

## Control Flow And State
The header has no executable flow. Its state model is the VSC register layout. `vsc7326.c` uses these macros to build initialization tables, reset ports, update watermarks, configure MAC addresses and filters, read RMON counters, and clear statistics.

## Dependencies And Integration Points
It is tightly coupled to `vsc7326.c` and to `gmac` operations for VSC-based boards. It also indirectly depends on TPI access because the VSC driver converts these CRA addresses to TPI offsets for 16-bit high/low register accesses.

## Risks And Edge Cases
`CRA` accepts raw values and masks them, so invalid block/sub/address values silently alias rather than failing. Several comments note datasheet quirks and errata, especially MIIM and traffic shaper encoding. The header includes registers that are not used, which can be useful for diagnostics but increases the chance of selecting a plausible but wrong register.

## Test Signals
Static build coverage confirms macro names. Runtime validation comes through VSC MAC tests: reset/BIST, port initialization, SPI4 datapath lock, MAC address filter behavior, stats counter reads, and speed/flow-control programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/vsc7326_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/Makefile

## Purpose
This Makefile declares the Linux kernel build objects for the Chelsio T3 `cxgb3` driver.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CHELSIO_T3) += cxgb3.o` builds the module/object when the kernel config enables Chelsio T3.
- `cxgb3-objs` links `cxgb3_main.o`, PHY drivers (`ael1002.o`, `vsc8211.o`, `aq100x.o`), hardware setup (`t3_hw.o`, `mc5.o`, `xgmac.o`), SGE (`sge.o`), L2 table (`l2t.o`), and offload support (`cxgb3_offload.o`) into `cxgb3.o`.

## Control Flow And State
There is no runtime control flow. The file controls build-time composition of the driver.

## Dependencies And Integration Points
The object list establishes integration between the main PCI/netdev driver, T3 hardware module code, PHY implementations, MAC, SGE DMA queues, Layer 2 table, and offload control path. It depends on the kernel Kbuild system and `CONFIG_CHELSIO_T3`.

## Risks And Edge Cases
Leaving an object out can produce missing symbols or silently omit a PHY/offload path. Adding an object without matching config dependencies can break builds. Object ordering is mostly link-time composition, but symbol availability must match declarations in shared headers such as `common.h` and `adapter.h`.

## Test Signals
The primary signal is a successful kernel/module build with `CONFIG_CHELSIO_T3=y/m`, followed by successful probe paths for boards requiring each listed PHY object and offload path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/adapter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/adapter.h

## Purpose
`adapter.h` defines the OS-facing T3 adapter, port, SGE queue, and helper structures for `cxgb3`. It is included through `common.h` and centralizes Linux-specific state around netdevs, PCI, interrupts, work items, DMA rings, and offload device integration.

## Important APIs, Types, And Functions
- `struct iscsi_config` stores iSCSI MAC flags and optional send/receive hooks.
- `struct port_info` connects an adapter to a netdev port, queue-set assignment, PHY, MAC, link config, iSCSI address/config, activity, and link-fault state.
- Adapter flags include `FULL_INIT_DONE`, `USING_MSI`, `USING_MSIX`, `QUEUES_BOUND`, `TP_PARITY_INIT`, and `NAPI_INIT`.
- SGE data structures model free lists (`struct sge_fl`), response queues (`struct sge_rspq`), TX queues (`struct sge_txq`), queue sets (`struct sge_qset`), and the top-level `struct sge`.
- `struct adapter` aggregates `t3cdev`, PCI/MMIO state, device maps, parameters, interrupt stats, MSI-X metadata, SGE/MC5/MC7 modules, ports, delayed/workqueue jobs, debugfs root, locks, and a no-fail SKB.
- Inline helpers are `t3_read_reg`, `t3_write_reg`, `adap2pinfo`, `phy2portid`, `tdev2adap`, and `offload_running`.
- Prototypes expose SGE control, interrupt handler selection, netdev TX, management TX, queue allocation/coalescing, OS link callbacks, and EDC firmware loading.

## Control Flow And State
The header defines state used throughout the driver lifecycle. Probe allocates and fills `struct adapter`, creates netdev ports with `port_info`, prepares SGE queues, and binds queues/interrupts. Open/close paths update `open_device_map`, start/stop SGE, timers, and NAPI. Interrupt paths update `irq_stats`, queue work items, and dispatch through SGE/OS handlers. Offload uses the embedded `t3cdev` and `OFFLOAD_DEVMAP_BIT`.

## State And Persistence Behavior
Software state persists for the device lifetime: ring indices/generation bits, DMA addresses, queue credits, counters, work items, link state, and hardware module statistics. Hardware state is accessed by `t3_read_reg`/`t3_write_reg` through `adapter->regs`. Queue rings are DMA-backed and mirrored by software descriptor arrays.

## Dependencies And Integration Points
The header depends on Linux PCI, spinlocks, interrupts, timers, cache alignment, mutexes, bit operations, I/O accessors, `t3cdev`, and netdev internals. It integrates SGE, MC5/MC7, PHY/MAC common definitions, iSCSI/offload hooks, debugfs, workqueues, MSI/MSI-X, and netdev transmit queues.

## Risks And Edge Cases
Many fields are concurrency-sensitive: queue locks, response lock, adapter work lock, MDIO mutex, and stats lock must match their call paths. Ring indices/generation bits and DMA mappings must stay synchronized with hardware contexts. `phy2portid` assumes at most two ports and compares against port 0's embedded PHY. The no-fail SKB and workqueue paths imply recovery paths that must be robust under memory pressure and hardware fatal errors.

## Test Signals
Signals include clean probe/remove, open/close, MSI/MSI-X and legacy interrupt coverage, queue allocation/free with DMA leak checks, NAPI packet receive and TX reclaim, offload open/close state, link-fault work execution, and debugfs/stat counters matching traffic and injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/adapter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/ael1002.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/ael1002.c

## Purpose
`ael1002.c` implements multiple 10G PHY variants for Chelsio T3: AEL1002, AEL1006, AEL2005, AEL2020, QT2045, and direct XAUI. It provides `cphy_ops` implementations for reset, power, interrupts, module detection, EDC firmware loading, link status, and prep functions used by adapter board setup.

## Important APIs, Types, And Functions
- `struct reg_val` and `set_phy_regs` apply MDIO register write/change scripts.
- `ael100x_txon` enables board GPIOs needed for AEL100x TX.
- `ael_i2c_rd` reads module EEPROM bytes through the PHY I2C bridge with timeout handling.
- `get_link_status_r` and `get_link_status_x` compute 10GBASE-R/X link status from PMA/PCS/PHYXS MDIO status.
- `ael1002_*` handles basic AEL1002 reset/power/no-op interrupts.
- `ael1006_ops` uses generic LASI interrupt helpers with AEL1002-style power.
- `ael2xxx_get_module_type` decodes SFF module type and twinax length from EEPROM.
- `ael2005_*` and `ael2020_*` detect hot-plug module changes, load optical or twinax EDC firmware/settings, preserve/re-enable interrupt state across reset, and report module/link-change causes.
- `qt2045_ops` supports a 10GBASE-CX4 PHY with possible address remap from 0 to 1.
- `xaui_direct_ops` supports direct XAUI link status from XGMAC SERDES status registers.
- Exported prep functions are `t3_ael1002_phy_prep`, `t3_ael1006_phy_prep`, `t3_ael2005_phy_prep`, `t3_ael2020_phy_prep`, `t3_qt2045_phy_prep`, and `t3_xaui_direct_phy_prep`.

## Control Flow And State
Board preparation calls a `t3_*_phy_prep` function, which initializes `struct cphy` with capabilities, MDIO ops, operation table, and description. Reset paths power up the PHY, apply vendor registers, read module type where relevant, choose optical or twinax EDC setup, and may load firmware words from `t3_get_edc_fw` into `phy->phy_cache` before writing them over MDIO. Interrupt handlers read GPIO/module status, classify module changes, reset when the required EDC profile changes, call generic LASI handling, and return `cphy_cause_module_change` and/or `cphy_cause_link_change`.

## State And Persistence Behavior
`phy->modtype` records detected module type. `phy->priv` records the active EDC profile (`edc_none`, `edc_sr`, or `edc_twinax`) to avoid unnecessary firmware reloads. `phy->phy_cache` holds downloaded EDC register/value data. Hardware state spans PMA/PMD, PCS, PHYXS, GPIO, I2C bridge, and board GPIO registers. Interrupt enable state is read before reset and restored when possible.

## Dependencies And Integration Points
The file depends on `common.h`, `regs.h`, MDIO MMD constants, generic PHY helpers in T3 hardware code, XGMAC SERDES registers, adapter GPIO helpers, and `t3_link_changed` for immediate link notification in AEL2020 interrupt enable. It integrates with board setup through prototypes in `common.h`.

## Risks And Edge Cases
Module EEPROM I2C reads can time out. EDC firmware loading is size/profile-specific; wrong firmware or stale cache state can break optical/twinax links. Hot-unplug retains EDC state intentionally, so module replacement with a different type relies on interrupt detection and reset. Some reset paths contain long sleeps, including 500 ms waits for AEL2020 microcontroller setup. The AEL2020 reset path re-enables interrupts via `ael2005_intr_enable`, which is suspicious and should be reviewed if behavior changes.

## Test Signals
Signals include PHY prep success for each supported type, correct 10G link reporting, module insertion/removal events, EDC firmware request/load paths for SR and twinax modules, LASI interrupt handling, power-down/up behavior, QT2045 alternate address detection, and direct XAUI low-signal reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/ael1002.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/aq100x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/aq100x.c

## Purpose
`aq100x.c` implements the Aquantia AQ100x 1000/10GBASE-T PHY support for Chelsio T3. It provides a `cphy_ops` table for reset, interrupts, autonegotiation, advertisement, loopback, link status, power management, and board preparation.

## Important APIs, Types, And Functions
- Register enums name AQ-specific PMA/PMD, XGXS, autonegotiation, and vendor MMD registers such as `AQ_LINK_STAT`, `AQ_IMASK_PMA`, `AQ_ANEG_STAT`, `AQ_FW_VERSION`, `AQ_IFLAG_GLOBAL`, and `AQ_IMASK_GLOBAL`.
- Bit enums define interrupt masks, advertisement bits, reset bits, and low-power bit.
- `aq100x_reset` performs a vendor-MMD PHY reset and always waits up to 3 seconds.
- `aq100x_intr_enable/disable/clear/handler` configure and clear PMA/global interrupt paths and report link-change causes.
- `aq100x_power_down`, `aq100x_autoneg_enable`, and `aq100x_autoneg_restart` manage low power and autoneg restart.
- `aq100x_advertise` programs 10G, 1G, 100M, and pause advertisement registers.
- `aq100x_set_loopback` toggles PMA loopback, while `aq100x_set_speed_duplex` returns unsupported.
- `aq100x_get_link_status` reads link state and decodes negotiated speed/duplex from `AQ_ANEG_STAT`.
- `t3_aq100x_phy_prep` initializes `struct cphy`, hard-resets the PHY through adapter GPIO, waits for firmware/MDIO readiness, checks firmware version and low-power state, and verifies XAUI settings.

## Control Flow And State
Prep initializes capabilities for 1G/10G copper with autonegotiation, toggles a per-port GPIO reset line, sleeps for firmware load, polls vendor reset bits, warns but allows prep to succeed on MDIO failures or timeout paths, checks firmware version `101`, clears low-power mode, and verifies XAUI RX/TX config. Runtime autoneg calls power the PHY up then set `BMCR_ANENABLE | BMCR_ANRESTART`. Link status returns early if link is down, otherwise it decodes speed and duplex.

## State And Persistence Behavior
The PHY stores operational state in MDIO registers across PMA/PMD, AN, PHYXS, and vendor MMDs. The driver does not keep private software state beyond the generic `struct cphy`. Hardware reset and low-power clearing persist until later power/reset operations. Interrupt status is latch-like and cleared by reading global/PMA status.

## Dependencies And Integration Points
The file depends on `common.h`, `regs.h`, T3 MDIO helpers, Linux MDIO constants, adapter GPIO register `A_T3DBG_GPIO_EN`, and `cphy_init`. It integrates with the T3 board setup path through `t3_aq100x_phy_prep`, and with generic link management through the `cphy_ops` callbacks.

## Risks And Edge Cases
Prep deliberately returns success for some reset/MDIO timeout conditions to let adapter preparation continue, which can leave a nonfunctional PHY that only emits warnings. Firmware version mismatches also warn rather than fail. `set_speed_duplex` is unsupported, so forced speed mode must be avoided for this PHY. The advertised `mmds` omits `MDIO_DEVS_AN` even though AN registers are used, which depends on MDIO access mode behavior elsewhere.

## Test Signals
Signals include successful GPIO reset timing, firmware version reads, low-power exit, XAUI config validation, autoneg advertisement for 10G/1G/100M/pause combinations, link status decoding for 10G/1G/100M/10M, loopback enable/disable, and interrupt clear/handler returning link-change events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/aq100x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/common.h

## Purpose
`common.h` is the central hardware/common interface for Chelsio T3 `cxgb3`. It defines logging macros, global constants, adapter/PHY/MAC/SGE/TP/MC5/MC7 parameter and statistics structures, PHY operation contracts, helper wrappers, and prototypes for the hardware, interrupt, link, MAC, TP, SGE, and PHY implementation files.

## Important APIs, Types, And Functions
- Logging/debug macros are `CH_ERR`, `CH_WARN`, `CH_ALERT`, `CH_MSG`, and `CH_DBG`, with an extra `NETIF_MSG_MMIO` category.
- Constants cover ports, frame sizes, EEPROM size, RSS table, TCB, MTU table, congestion windows, TP SRAM size, pause bits, IRQ stats, TP version fields, SGE queue counts, async/immediate packet sizes, descriptor flits, and MAC accumulation timing.
- Core hardware structs include `adapter_info`, `adapter_params`, `vpd_params`, `pci_params`, `mc5`, `mc7`, `mac_stats`, `tp_mib_stats`, `tp_params`, `qset_params`, `sge_params`, `mc5_params`, `trace_params`, and `link_config`.
- PHY abstractions include `mdio_ops`, `cphy_ops`, `cphy`, module type enums, loopback direction, interrupt cause bits, and EDC firmware sizes.
- Inline helpers include `t3_mdio_read`, `t3_mdio_write`, `cphy_init`, `for_each_port`, `adapter_info`, `uses_xaui`, `is_10G`, `is_offload`, `core_ticks_per_usec`, and `is_pcie`.
- Prototypes cover register helpers, MDIO/PHY helpers, interrupt control, link events, adapter prep/init/reset/firmware, MAC operations, MC5, TP offload and stats, MTU/trace/scheduler configuration, SGE context operations, and all supported PHY prep functions.

## Control Flow And State
This header defines the contracts that structure T3 driver flow. Adapter prep fills `adapter_params`, VPD/PCI fields, and `adapter_info`; hardware init configures MC5/MC7, TP, SGE, MACs, firmware, and RSS; open/close/link operations use `link_config`, `cphy_ops`, and MAC prototypes; interrupts flow through common interrupt prototypes and PHY/MAC handlers; offload and iSCSI/RDMA paths query control structures and context setup functions.

## State And Persistence Behavior
Most structures describe software mirrors of persistent hardware configuration: VPD clock/MAC data, PCI mode, memory sizes, MTU/congestion tables, TP page sizing, queue parameters, MAC/TP/MC5/MC7 counters, link configuration, and trace filters. `cphy` stores module type, capabilities, MDIO interface, FIFO errors, and an EDC firmware cache.

## Dependencies And Integration Points
The header depends on Linux kernel, netdevice, ethtool, MDIO, delay, and version headers. It includes `adapter.h` late, after common types are defined. It is included by nearly every `cxgb3` hardware, PHY, MAC, SGE, and offload source file, making it the main ABI inside the driver.

## Risks And Edge Cases
Because it is a central header, changes have broad build and behavior blast radius. Structure layouts must match code assumptions in debugfs, ioctl/offload paths, and hardware context programming. PHY operation callbacks are optional for some features but many call paths assume the relevant pointer exists for the selected PHY. Constants such as frame sizes, queue counts, and EDC cache size encode hardware limits.

## Test Signals
Signals include full driver build coverage, probe on multiple board types, link/autoneg behavior across PHYs, MAC/TP/SGE stats reads, firmware/version checks, offload control queries, SGE context setup/teardown, and static checks for prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ctl_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ctl_defs.h

## Purpose
`cxgb3_ctl_defs.h` defines command IDs and payload structures for internal `cxgb3` offload control requests between upper-layer protocol drivers and the T3 low-level driver.

## Important APIs, Types, And Functions
- Command IDs cover adapter limits and resources (`GET_MAX_OUTSTANDING_WR`, `GET_TX_MAX_CHUNK`, TID/STID/RTBL ranges, L2T capacity, MTUs, WR length, MAC-to-interface lookup, DDP parameters, ports), iSCSI params, RDMA params/CQ/control-QP operations, offload page info, iSCSI IPv4 address, and embedded firmware/TP version info.
- `struct tid_range`, `mtutab`, `iff_mac`, `iscsi_ipv4addr`, `ddp_params`, `adap_ports`, `ulp_iscsi_info`, `rdma_info`, `rdma_cq_op`, `rdma_cq_setup`, `rdma_ctrlqp_setup`, `ofld_page_info`, and `ch_embedded_info` define typed request/response payloads.

## Control Flow And State
There is no executable flow. Upper-layer offload clients pass command IDs and matching structures to control dispatch code in `cxgb3_offload`/`t3cdev` paths. The low-level driver fills ranges, tables, PCI device pointers, doorbell addresses, memory windows, queue setup data, or protocol parameters.

## State And Persistence Behavior
The structures expose live adapter state rather than owning state. Returned pointers such as netdevs, PCI devices, MTU tables, and kernel doorbell addresses are borrowed from the adapter. RDMA/iSCSI setup structures can cause persistent hardware context programming when consumed by control handlers.

## Dependencies And Integration Points
The header forward-declares `net_device` and `pci_dev` and uses kernel integer types. It integrates `cxgb3` with iSCSI and RDMA upper layers, offload page allocation decisions, TID/STID allocation, L2 table sizing, and firmware/protocol version reporting.

## Risks And Edge Cases
The command enum and payload type must stay synchronized with dispatch code and upper-layer clients. Several structures contain raw pointers, so lifetime and context rules matter. Version or layout drift can break out-of-tree consumers. Resource ranges are half-open or capacity-based and require callers to validate bounds.

## Test Signals
Signals include offload control command tests for each enum path, iSCSI/RDMA bring-up, correct TID/STID/L2T/MTU/DDP values, CQ/control-QP setup success and teardown, and embedded firmware/TP version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ctl_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_defs.h

## Purpose
`cxgb3_defs.h` provides small inline helpers for mapping T3 offload connection IDs to TID table entries. It is part of the offload-facing internal API.

## Important APIs, Types, And Functions
- `VALIDATE_TID` enables validation behavior in included offload definitions.
- `atid2entry` and `stid2entry` convert active-open and server TID numbers into their table entries by subtracting base IDs.
- `lookup_tid` validates a regular TID against `ntids` and returns the entry only if it has an attached client.
- `lookup_stid` and `lookup_atid` validate server/active-open TID ranges and reject entries whose `next` pointer indicates the entry is on a free list rather than live.

## Control Flow And State
The helpers are used in offload receive/control paths when firmware messages identify a connection by TID/STID/ATID. They translate IDs into `struct t3c_tid_entry` pointers after range and live-entry checks.

## State And Persistence Behavior
The file owns no state. It reads `struct tid_info` tables defined by `cxgb3_offload.h`/`t3cdev.h`. The pointer-range checks depend on table/free-list layout in those structures.

## Dependencies And Integration Points
The header includes Linux SKB/TCP headers, `t3cdev.h`, and `cxgb3_offload.h`. It integrates firmware TID values with offload client connection state, listen entries, and active-open entries.

## Risks And Edge Cases
The free-list detection uses pointer comparisons across table regions, so it is tightly coupled to allocation layout. Invalid IDs return NULL; callers must handle NULL before dereferencing. `atid2entry` and `stid2entry` do no range checks themselves and must be called only after validation.

## Test Signals
Signals include offload connection setup/teardown, active-open and listen lookup behavior, invalid TID message handling without crashes, and tests that freed STID/ATID entries are not treated as live connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ioctl.h

## Purpose
`cxgb3_ioctl.h` defines private ioctl command numbers and payload structures for `cxgb3` diagnostics and configuration through `SIOCCHIOCTL` (`SIOCDEVPRIVATE`).

## Important APIs, Types, And Functions
- Commands include MTU table get/set, PM get/set, memory read, firmware load, trace filter set, queue-set parameter get/set, and queue-set count get/set.
- `struct ch_reg`, `ch_cntxt`, `ch_desc`, and `ch_mem_range` describe register, context, descriptor, and memory-range access.
- `CNTXT_TYPE_EGRESS`, `CNTXT_TYPE_FL`, `CNTXT_TYPE_RSP`, and `CNTXT_TYPE_CQ` identify SGE context types.
- `struct ch_qset_params` mirrors queue sizes, interrupt latency, polling, LRO, congestion threshold, vector, and queue number.
- `struct ch_pktsched_params`, `ch_mtus`, `ch_pm`, `ch_tcam`, `ch_tcb`, `ch_tcam_word`, and `ch_trace` define scheduler, MTU, protocol-memory, TCAM/TCB, and trace-filter payloads.
- `TCB_WORDS` derives TCB array size from `TCB_SIZE`, and memory IDs are `MEM_CM`, `MEM_PMRX`, and `MEM_PMTX`.

## Control Flow And State
The header has no executable flow. User-space tooling passes these structures through the driver private ioctl handler. Handlers then read/write registers, contexts, descriptors, memory windows, firmware, queue-set parameters, MTU tables, protocol memory configuration, or trace filters.

## State And Persistence Behavior
Ioctls can read and mutate persistent adapter hardware state: firmware, MTU table, queue-set sizing/coalescing, protocol-memory parameters, trace filters, and hardware memory/register contents. The flexible array in `ch_mem_range` carries variable-length memory data. TCB/TCAM structures expose hardware connection/filter state.

## Dependencies And Integration Points
The header depends on fixed-width integer types, `NMTUS`, `TCB_SIZE`, and Linux private socket ioctl numbering. It integrates user-space diagnostics/configuration with T3 hardware management code and queue/offload internals.

## Risks And Edge Cases
Private ioctl structures are ABI-sensitive. Field size, alignment, and command number changes can break tools. Several payloads expose raw hardware memory/register access and firmware loading, so validation in handlers is critical. Variable-length memory ranges require careful copy bounds. Bitfields in `ch_trace` may be compiler-layout sensitive if shared directly with user space.

## Test Signals
Signals include ioctl ABI compile checks, user-tool compatibility, bounds checks for memory/register/context reads, firmware load success/failure paths, qset parameter round trips, MTU table round trips, and trace filter programming verified by captured traffic or hardware trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ioctl.h -->
