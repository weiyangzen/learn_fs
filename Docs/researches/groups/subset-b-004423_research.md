# subset-b-004423 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_port.c

## Purpose
Implements the Freescale DPAA Frame Manager port driver. It owns Rx/Tx FMan port register programming for BMI, QMI, and Rx hardware parser blocks, exposes the port configuration/runtime API used by DPAA Ethernet MAC code, and registers the `fsl-fman-port` platform driver for FMan v2/v3 Rx and Tx port device-tree nodes.

## Important APIs, Types, and Functions
Internal register maps include `fman_port_rx_bmi_regs`, `fman_port_tx_bmi_regs`, `fman_port_qmi_regs`, and `fman_port_hwp_regs`. Runtime state is carried in `struct fman_port`, `struct fman_port_cfg`, `struct fman_port_dts_params`, and buffer-pool helper structures. Exported entry points are `fman_port_config`, `fman_port_init`, `fman_port_cfg_buf_prefix_content`, `fman_port_disable`, `fman_port_enable`, `fman_port_bind`, `fman_port_get_qman_channel_id`, `fman_port_get_device`, `fman_port_get_hash_result_offset`, `fman_port_get_tstamp`, and `fman_port_use_kg_hash`. Important internal paths include `init_bmi_rx`, `init_bmi_tx`, `init_qmi`, `init_hwp`, `set_ext_buffer_pools`, `verify_size_of_fifo`, `fill_soc_specific_params`, and the platform `fman_port_probe`.

## Control Flow and State
Probe allocates `struct fman_port`, binds the parent FMan device, reads `cell-index`, determines port type/speed from compatible strings and 10G properties, maps the port register resource, and stores driver data. `fman_port_config` allocates a transient `cfg`, copies caller queue/pool parameters, reads FMan revision, selects SoC limits/default resource budgets, and records BMI/QMI/HWP register bases. `fman_port_init` builds buffer-prefix offsets, orders external buffer pools, validates margins/FIFO sizing, passes resource parameters to core FMan, writes hardware registers, optionally initializes KeyGen hashing, then frees `cfg` to mark init complete. Enable/disable toggles QMI/BMI enable bits and polls busy status. Persistent state lives in device registers, `struct fman_port` fields, and FMan/QMan/KeyGen configuration; `cfg` is only valid between config and init.

## Dependencies and Integration Points
Depends on `fman.h` for FMan revision/resources, `fman_sp` for buffer-prefix layout and pool ordering, `fman_keygen` for PCD hashing, platform/of APIs for device-tree binding, and DPAA MAC code through `fman_port_bind`. QMan channel IDs come from the parent FMan for Tx ports. Rx ports integrate with external buffer pools and optional KeyGen distribution; Tx ports integrate with confirmation/error queues and QMI dequeue configuration.

## Risks and Test Signals
Risks include invalid revision-specific defaults, FIFO sizing that is too small for max frame and pool margins, incorrect 10G port speed detection, use of API calls before/after the `cfg` lifecycle window, QMI/BMI disable timeouts, and register bit drift for FMan errata workarounds. Test signals include DT probe of v2/v3 Rx/Tx ports, `fman_port_config` then `fman_port_init` success, link bring-up through DPAA Ethernet, hash-result/timestamp offset reads, Tx confirmation behavior, Rx buffer depletion behavior, and debug logs for BMI/QMI busy or HWP start/stop timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_port.h

## Purpose
Defines the public FMan port API and frame-error constants used by DPAA Ethernet MAC/netdev code to configure and operate FMan Rx and Tx ports.

## Important APIs, Types, and Functions
The header maps FMan frame descriptor error bits to `FM_PORT_FRM_ERR_*` constants, forward declares `struct fman_port`, and defines `fman_port_rx_params`, `fman_port_non_rx_params`, `fman_port_specific_params`, and `fman_port_params`. It declares the exported lifecycle and utility APIs implemented in `fman_port.c`: config, init, buffer-prefix configuration, enable/disable, hash/timestamp accessors, QMan channel lookup, device lookup, KeyGen hash selection, and device binding.

## Control Flow and State
There is no runtime control flow in this header. Its state model is the contract between consumers and `fman_port.c`: callers supply queue IDs and external buffer pools through `fman_port_params`, then call config/init before runtime enable/disable or metadata offset access. Error constants describe persistent status bits reported by hardware frame descriptors.

## Dependencies and Integration Points
Includes `fman.h` for FMan types, frame descriptor error definitions, buffer pool structures, and prefix content structures. It is consumed by `mac.h`, DPAA Ethernet code, FMan MAC initialization code, and any module binding platform FMan port devices.

## Risks and Test Signals
Risks are ABI-style: changing error masks, parameter structure layout, or function prototypes breaks DPAA users or misclassifies hardware frame errors. Test signals are build coverage of FMan MAC and Ethernet modules, compile checks for all exported prototypes, and runtime validation that Rx error queue/discard behavior matches descriptor status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.c

## Purpose
Provides shared FMan storage/profile helpers for buffer-pool ordering and packet buffer-prefix layout. These helpers are used by FMan ports before programming BMI buffer and internal-context registers.

## Important APIs, Types, and Functions
Exports `fman_sp_set_buf_pools_in_asc_order_of_buf_sizes` and `fman_sp_build_buffer_struct`. The first builds an ordered pool-ID array and a size-by-pool-ID array from `struct fman_ext_pools`. The second derives `struct fman_sp_int_context_data_copy`, `struct fman_sp_buf_margins`, and `struct fman_sp_buffer_offsets` from `struct fman_buffer_prefix_content`.

## Control Flow and State
Pool ordering uses insertion-sort-like placement by pool size and writes caller-provided arrays. Buffer layout aligns private data to 16-byte internal context units, initializes parser/timestamp/hash offsets to `ILLEGAL_BASE`, computes copy size for parser results and timestamp/hash context, sets external offsets for each requested metadata item, computes start margin, and aligns the final data offset to the requested alignment. The file keeps no persistent state.

## Dependencies and Integration Points
Depends on `fman_sp.h` and `fman.h` for FMan pool and prefix structures. `fman_port_init` calls both helpers before programming Rx external buffer pools and BMI internal context registers. Consumers later use the computed offsets through `fman_port_get_hash_result_offset` and `fman_port_get_tstamp`.

## Risks and Test Signals
Risks include division/modulo by an invalid zero `data_align`, incorrect assumptions about parser result and timestamp/hash sizes, pool IDs indexing beyond caller arrays, and mismatch between computed margins and actual external buffer sizes. Test signals are Rx initialization with multiple external pool sizes, prefix combinations for parser result/timestamp/hash result, timestamp extraction from received data, and rejection of too-small external buffers in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.h

## Purpose
Declares shared FMan storage/profile constants, buffer-margin structures, metadata offset structures, and helper prototypes used by FMan port initialization.

## Important APIs, Types, and Functions
Defines `ILLEGAL_BASE`, default 64-byte context alignment, external buffer pool and DMA attribute register bits, and internal-context shift constants. Important types are `fman_sp_int_context_data_copy`, `fman_sp_buf_margins`, and `fman_sp_buffer_offsets`. It declares `fman_sp_build_buffer_struct` and `fman_sp_set_buf_pools_in_asc_order_of_buf_sizes`.

## Control Flow and State
There is no runtime control flow. The header describes how buffer-prefix state is represented before it is converted into BMI register fields: copy offsets/sizes, external buffer start/end margins, and data/parser/timestamp/hash offsets.

## Dependencies and Integration Points
Includes `fman.h` and Linux integer types. It is consumed by `fman_sp.c` and `fman_port.c`, where constants are reused for BMI register shifts and pool flags.

## Risks and Test Signals
Risks are register-contract drift and offset sentinel misuse. Test signals include successful compilation of FMan port code, correct metadata offsets for configured prefix content, and Rx buffer pool programming with valid/backup/counter flags matching hardware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.c

## Purpose
Implements the FMan 10 Gigabit Ethernet Controller (TGEC/XGEC) MAC backend. It provides register programming, phylink callbacks, multicast hash filtering, timestamp enable, exception handling, and the `tgec_initialization` hook used by the FMan MAC platform driver.

## Important APIs, Types, and Functions
Defines the TGEC register map `struct tgec_regs`, configuration `struct tgec_cfg`, and backend-private `struct fman_mac`. Key functions are `tgec_config`, `tgec_init`, `tgec_free`, `tgec_initialization`, `tgec_link_up`, `tgec_link_down`, `tgec_modify_mac_address`, `tgec_add_hash_mac_address`, `tgec_del_hash_mac_address`, `tgec_set_allmulti`, `tgec_set_promiscuous`, `tgec_set_tstamp`, `tgec_set_exception`, and interrupt callback `tgec_err_exception`.

## Control Flow and State
Initialization assigns function pointers into `struct mac_device`, converts legacy XGMII DT mode to XAUI, advertises 10G full-duplex and pause capabilities, allocates the private MAC/config objects, resets the MAC if enabled, writes station address/default config/max frame/pause/interrupt masks, allocates multicast and unicast hash tables, registers FMan MAC error interrupts, frees the transient config, and disables Tx ECC exceptions. Link-up configures pause, updates the parent MAC speed, and sets Rx/Tx enable bits; link-down clears them. Multicast filtering tracks software hash entries while programming TGEC hash-table control entries. Exception enable state is mirrored in `tgec->exceptions` and hardware `imask`.

## Dependencies and Integration Points
Depends on `mac.h`, `fman_mac.h`, FMan reset/interrupt/max-frame APIs, phylink, CRC/bit-reversal helpers, and shared FMan hash-table helpers. `mac.c` selects this backend for `fsl,fman-xgec` nodes; DPAA Ethernet later uses the installed `mac_device` operations for multicast, timestamp, promiscuous, and link control.

## Risks and Test Signals
Risks include multicast hash collisions/leaks, unicast hash requests being unsupported, endian-sensitive MAC address conversion, unsupported interface assumptions, exception mask drift, FMan revision errata handling, and freeing resources on partial initialization failures. Test signals include 10G XAUI link-up/down via phylink, multicast/allmulti/promiscuous filtering, timestamp bit toggling, FMan MAC interrupt delivery, max-frame programming, and error-path probe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.h

## Purpose
Declares the TGEC/XGEC initialization entry point used by the generic FMan MAC platform driver.

## Important APIs, Types, and Functions
Includes `fman_mac.h`, forward declares `struct mac_device`, and declares `tgec_initialization(struct mac_device *mac_dev, struct device_node *mac_node, struct fman_mac_params *params)`.

## Control Flow and State
There is no runtime control flow. The declared function is the backend factory/initializer that populates `mac_device` operation pointers and creates the TGEC private state.

## Dependencies and Integration Points
Used by `mac.c` in its OF match table for `fsl,fman-xgec`. The prototype bridges generic FMan MAC probing with the 10G-specific implementation in `fman_tgec.c`.

## Risks and Test Signals
Risk is mainly signature drift between the generic MAC initialization table and backend implementation. Test signals are compile coverage with TGEC enabled and successful probe of an `fsl,fman-xgec` DT node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_tgec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.c

## Purpose
Implements the generic FMan MAC platform driver. It binds FMan MAC DT nodes to the parent FMan device and two FMan ports, dispatches to the selected MAC backend (dTSEC, TGEC, or MEMAC), and creates the child `dpaa-ethernet` platform device consumed by the DPAA Ethernet netdev driver.

## Important APIs, Types, and Functions
Defines `struct mac_priv_s` for FMan pointer, cell index, speed, and child Ethernet device. The OF match table maps `fsl,fman-dtsec`, `fsl,fman-xgec`, and `fsl,fman-memac` to backend initialization functions. Important functions are `mac_probe`, `mac_remove`, `dpaa_eth_add_device`, and `mac_exception`.

## Control Flow and State
Probe allocates `mac_device` and private state, finds and binds the parent FMan, requests and maps the MAC register resource from the FMan memory region, checks node availability, reads MAC `cell-index` and address, resolves exactly two `fsl,fman-ports` phandles, binds each FMan port, reads PHY mode with SGMII fallback, prepares `fman_mac_params`, calls the backend initializer, logs the address, and registers a `dpaa-ethernet` child with `dpaa_eth_data`. Remove drops port/FMan references and unregisters the child. Child device numbering is serialized by `eth_lock`.

## Dependencies and Integration Points
Depends on OF/platform/resource APIs, FMan core binding, `fman_port_bind`, backend initializers from `fman_dtsec`, `fman_tgec`, and `fman_memac`, phylink interface modes, and DPAA Ethernet's `dpaa_eth_data` contract. Exceptions from backends route through `mac_exception`; RX FIFO overflow is masked after first report.

## Risks and Test Signals
Risks include reference imbalance on probe error paths, missing or wrong number of port phandles, backend init failures after resources are bound, child platform device registration failures, and DT compatibility/PHY mode mismatches. Test signals include probe/remove with each MAC compatible, valid child `dpaa-ethernet` creation, correct MAC address reporting, phylink mode propagation, and leak/error-path checks around failed FMan or port binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.h

## Purpose
Defines the generic FMan MAC device abstraction shared by FMan MAC backends and the DPAA Ethernet netdev layer.

## Important APIs, Types, and Functions
`struct mac_device` holds mapped MAC registers, device/resource pointers, MAC address, two FMan ports, phylink state/config, PHY interface, multicast/promiscuous flags, backend operation callbacks, ethtool statistic callbacks, speed update callback, backend `fman_mac` private pointer, and references to parent FMan/port devices. It also defines `PORT_NUM`, `fman_config_to_mac`, and `struct dpaa_eth_data`.

## Control Flow and State
The only executable logic is the inline `fman_config_to_mac` container conversion. Runtime state is owned by `mac.c`, individual backends, and DPAA Ethernet users through the operation pointers and fields in `mac_device`.

## Dependencies and Integration Points
Includes Linux device, Ethernet, PHY, phylink, and list headers plus `fman_port.h`, `fman.h`, and `fman_mac.h`. It is the key contract between generic MAC probing, dTSEC/TGEC/MEMAC implementations, and the `dpaa-ethernet` child driver.

## Risks and Test Signals
Risks include callback signature drift, missing backend operations, stale `fman_mac` private pointers, and assumptions that exactly two FMan ports exist. Test signals are compile coverage for all FMan backends and runtime DPAA Ethernet operations for link, multicast, timestamping, ethtool stats, and speed updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Kconfig

## Purpose
Defines build-time configuration for the legacy Freescale `fs_enet` Ethernet driver and its FEC/FCC/SCC MAC and MDIO support.

## Important APIs, Types, and Functions
Key symbols are `FS_ENET`, `FS_ENET_MPC5121_FEC`, `FS_ENET_HAS_SCC`, `FS_ENET_HAS_FCC`, `FS_ENET_HAS_FEC`, `FS_ENET_MDIO_FEC`, and `FS_ENET_MDIO_FCC`. `FS_ENET` selects `MII` and `PHYLINK`; FEC support selects FEC MDIO; FCC MDIO selects `MDIO_BITBANG`.

## Control Flow and State
There is no runtime control flow. The file controls which source files are compiled and which platform/device-tree compatibles can bind at runtime. Platform constraints limit the driver to Freescale vendor support on CPM1, CPM2, or PPC MPC512x systems.

## Dependencies and Integration Points
Feeds the local Makefile and conditional code in `fs_enet.h`, `fs_enet-main.c`, and the MAC/MDIO backends. It integrates with kernel networking, phylink, MII, and mdio-bitbang subsystems through selected symbols.

## Risks and Test Signals
Risks include build combinations where declarations are present without matching objects, missing MDIO support for selected FEC hardware, and accidental exposure outside supported PowerPC/CPM platforms. Test signals are randconfig/allmodconfig coverage for CPM1, CPM2, and MPC512x, plus module dependency checks for FEC/FCC/SCC and MDIO variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Makefile

## Purpose
Builds the `fs_enet` composite driver and optional FEC/FCC/SCC MAC and MDIO objects according to Kconfig symbols.

## Important APIs, Types, and Functions
Defines `obj-$(CONFIG_FS_ENET) += fs_enet.o`, conditionally adds `mac-scc.o`, `mac-fec.o`, and `mac-fcc.o` to `fs_enet-m`, builds `mii-fec.o` and `mii-bitbang.o` as separate MDIO drivers, and sets `fs_enet-objs := fs_enet-main.o $(fs_enet-m)`.

## Control Flow and State
There is no runtime control flow. The link composition determines which `fs_ops` implementations are available to `fs_enet-main.c` and which MDIO platform drivers are emitted.

## Dependencies and Integration Points
Directly reflects `Kconfig` symbols and the `extern const struct fs_ops` declarations in `fs_enet.h`. Separate MDIO objects register their own platform drivers.

## Risks and Test Signals
Risks include missing backend objects for enabled OF match entries or duplicate symbol/link problems across configurations. Test signals are build checks for each symbol combination and verifying `fs_enet.o` contains only supported backend ops for the chosen platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fec.h

## Purpose
Defines Fast Ethernet Controller event and control bit masks shared by the `fs_enet` FEC MAC backend and FEC MDIO driver.

## Important APIs, Types, and Functions
Constants cover interrupt events (`FEC_ENET_*`), Ethernet control bits (`FEC_ECNTRL_*`), receive control bits including MII/RMII/promiscuous/duplex controls, transmit control bits including full duplex and graceful stop, `FEC_MAX_MULTICAST_ADDRS`, and `FEC_RESET_DELAY`.

## Control Flow and State
There is no runtime control flow. The macros describe persistent FEC hardware register state and event bits consumed by register read-modify-write code.

## Dependencies and Integration Points
Included by `mac-fec.c` and `mii-fec.c`, and indirectly complements the `struct fec` register layout conditionally declared in `fs_enet.h`.

## Risks and Test Signals
Risks are incorrect bit masks causing missed interrupts, wrong duplex/RMII setup, failed MII operations, or broken reset sequencing. Test signals include FEC link-up in MII and RMII modes, multicast/promiscuous filtering, graceful stop, FEC MDIO reads/writes, and event mask behavior under RX/TX traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet-main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet-main.c

## Purpose
Implements the common net_device driver for legacy Freescale CPM/FEC Ethernet controllers. It abstracts controller-specific hardware through `struct fs_ops`, while handling probe, phylink, NAPI, DMA descriptor rings, SKB TX/RX, interrupts, ethtool, and timeout recovery.

## Important APIs, Types, and Functions
Important paths include `fs_enet_probe`, `fs_enet_remove`, `fs_enet_open`, `fs_enet_close`, `fs_enet_start_xmit`, `fs_enet_napi`, `fs_enet_interrupt`, `fs_init_bds`, `fs_cleanup_bds`, `fs_timeout_work`, phylink callbacks `fs_mac_link_up` and `fs_mac_link_down`, and ethtool helpers. The OF match table selects `fs_scc_ops`, `fs_fcc_ops`, or `fs_fec_ops` depending on enabled backends and compatible strings.

## Control Flow and State
Probe allocates platform info, selects backend ops, reads CPM command for non-FEC controllers, determines PHY mode, enables optional clock, allocates netdev/private ring arrays, creates phylink, calls backend `setup_data` and `allocate_bd`, initializes locks/NAPI/ethtool/netdev ops, sets SG support, and registers the netdev. Open initializes BDs, enables NAPI, requests IRQ, connects PHY, starts phylink, and starts TX queue. Interrupt handling clears non-NAPI events, reports backend errors, disables NAPI events, and schedules poll. NAPI reclaims TX descriptors, handles TX errors/restarts, processes RX descriptors with copybreak or buffer replacement, updates stats, returns descriptors to hardware, and reenables events when complete. Close stops queue/NAPI/phylink, calls backend stop, disconnects PHY, and frees IRQ.

## Dependencies and Integration Points
Depends on Linux netdev, DMA mapping, NAPI, phylink, ethtool, OF/platform, and controller-specific `fs_ops` backends. Buffer descriptor access macros and private state come from `fs_enet.h`. MDIO connectivity is external through DT and phylink.

## Risks and Test Signals
Risks include DMA map/unmap imbalance, descriptor wrap errors, TX queue wake thresholds tied to `MAX_SKB_FRAGS`, RX copybreak/cache sync mistakes, timeout recovery racing close, backend event-mask mismatches, and partial probe cleanup leaks. Test signals include sustained RX/TX with fragmented SKBs, NAPI budget exhaustion, TX timeout recovery, phylink reconnect/link mode changes, ethtool register dumps/tunables, netpoll builds, and probe/remove error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet.h

## Purpose
Defines the shared `fs_enet` driver contract: backend operation table, platform/private state, buffer sizing, descriptor access macros, optional MPC5121 FEC register layout, and exported common descriptor helpers.

## Important APIs, Types, and Functions
Key types are `struct fs_ops`, `struct fs_platform_info`, `struct fs_enet_private`, optional `struct fec`/`struct fec_info`, and backend-specific private unions for FEC/FCC/SCC. It defines packet buffer constants (`PKT_MAXBUF_SIZE`, `PKT_MAXBLR_SIZE`, `ENET_RX_FRSIZE`), descriptor read/write macros (`CBDW_*`, `CBDR_*`, `CBDS_SC`, `CBDC_SC`), and extern backends `fs_fec_ops`, `fs_fcc_ops`, and `fs_scc_ops`.

## Control Flow and State
There is no standalone runtime control flow. The state model centers on `fs_enet_private`: locks, NAPI, netdev, phylink, ring memory, SKB arrays, current/dirty descriptor pointers, event masks, and backend-specific mapped registers/parameter RAM.

## Dependencies and Integration Points
Includes kernel netdev, PHY/phylink, DMA, CPM headers, and platform-specific CPM1/CPM2 declarations. It ties `fs_enet-main.c` to `mac-fec.c`, `mac-fcc.c`, `mac-scc.c`, and `mii-fec.c`.

## Risks and Test Signals
Risks include layout mismatches for MPC5121 FEC, endian/accessor mistakes for CPM descriptors, ring size/private allocation coupling, and backend unions being used with the wrong `fs_ops`. Test signals include build coverage across CPM1/CPM2/MPC512x, descriptor ring wrap under traffic, phylink state changes, ethtool register snapshots, and DMA debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/fs_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fcc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fcc.c

## Purpose
Implements the FCC backend for `fs_enet` on CPM2/PQ2 systems. It maps FCC registers/parameter RAM, programs FCC Ethernet operation on link-up, handles multicast filtering, interrupts, register dumps, and Tx restart errata recovery through `fs_fcc_ops`.

## Important APIs, Types, and Functions
The exported object is `const struct fs_ops fs_fcc_ops`. Important functions include `do_pd_setup`, `setup_data`, `allocate_bd`, `restart`, `stop`, `set_multicast_list`, NAPI event helpers, `get_int_events`, `clear_int_events`, `get_regs`, and `tx_restart`. Hardware access is through FCC register macros and CPM commands via `fcc_cr_cmd`.

## Control Flow and State
Setup maps three DT resources (FCC core, Ethernet parameter RAM, FCC continuation registers), stores CPM immediate memory, and allocates DPRAM for internal buffers. Restart disables RX/TX, clears parameter RAM, writes Rx/Tx BD base physical addresses, MRBLR, function codes, internal buffer pointers, CRC presets, counters, station/group addresses, frame size limits, RMII/speed/duplex mode, initializes BDs, issues `CPM_CR_INIT_TRX`, clears/enables events, and enables FCC Ethernet. `tx_restart` scans backward from hardware TBPTR to adjust retransmission state, toggles transmitter enable, and issues `CPM_CR_RESTART_TX`.

## Dependencies and Integration Points
Depends on CPM2 headers, `cpm_command`, `cpm_muram_alloc`, OF mapping/IRQ APIs, common descriptor helpers from `fs_enet.h`, and phylink-provided speed/duplex/interface from `fs_enet-main.c`.

## Risks and Test Signals
Risks include DPRAM leaks, resource unmap omissions, group-address low/high typo or stale cached multicast state, TBPTR recovery off-by-one errors, RMII speed bit inversion, and unmasked event reads causing interrupt loops. Test signals include FCC probe/link-up, multicast/promiscuous updates, TX underrun/late-collision recovery, ethtool register dumps, NAPI event masking, and CPM command failure instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fec.c

## Purpose
Implements the FEC backend for `fs_enet` on CPM1 and MPC512x-style Fast Ethernet controllers. It programs FEC registers, descriptor rings, multicast filters, MII/RMII mode, and interrupt control via `fs_fec_ops`.

## Important APIs, Types, and Functions
The exported object is `const struct fs_ops fs_fec_ops`. Important functions include `whack_reset`, `do_pd_setup`, `setup_data`, `allocate_bd`, `restart`, `stop`, `set_multicast_list`, NAPI event helpers, `rx_bd_done`, `tx_kickstart`, `get_int_events`, `clear_int_events`, and `get_regs`.

## Control Flow and State
Setup maps the FEC register resource and IRQ, initializes multicast hash cache, and sets FEC event masks. Restart resets the controller, writes station and multicast hash registers, configures max receive size, Rx/Tx descriptor base addresses, DMA/endian function code, MII speed from the associated MDIO bus private `fec_info`, interrupt vector/control mode, duplex, multicast/promiscuous state, interrupt mask, Ethernet enable, and Rx descriptor activation. Stop performs graceful transmit stop with timeout, masks interrupts, disables Ethernet, and cleans descriptors.

## Dependencies and Integration Points
Depends on `fec.h`, optional MPC5121 register layout from `fs_enet.h`, OF IRQ/mapping APIs, common descriptor helpers, and a FEC MDIO bus whose `mii_bus->priv` contains `struct fec_info`. It is selected by `fs_enet-main.c` for FEC-compatible DT nodes.

## Risks and Test Signals
Risks include assuming `dev->phydev->mdio.bus->priv` is FEC-specific, reset timeout, FEC/MPC5121 register layout divergence, multicast hash calculation errors, MII/RMII mode mistakes, and DMA coherent ring lifetime. Test signals include FEC link-up on MII/RMII, MDIO-backed MII speed programming, multicast/allmulti/promisc behavior, RX/TX interrupts and descriptor activation, graceful stop warnings, and ethtool register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-scc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-scc.c

## Purpose
Implements the SCC Ethernet backend for `fs_enet` on CPM1/CPM2 Serial Communications Controllers. It programs SCC registers and parameter RAM, allocates BD rings from CPM multi-user RAM, handles multicast mode, events, and Tx restart through `fs_scc_ops`.

## Important APIs, Types, and Functions
The exported object is `const struct fs_ops fs_scc_ops`. Important functions are `scc_cr_cmd`, `do_pd_setup`, `setup_data`, `allocate_bd`, `restart`, `stop`, `set_multicast_list`, NAPI event helpers, `get_int_events`, `clear_int_events`, `get_regs`, and `tx_restart`.

## Control Flow and State
Setup maps SCC and SCC Ethernet parameter resources and initializes event masks/hash caches. BD allocation reserves CPM MURAM and stores the virtual ring base. Restart disables SCC RX/TX, clears parameter RAM byte-by-byte, writes Rx/Tx BD offsets, function codes, MRBLR, CRC presets, counters, pad/retry/frame-size values, station address, initializes BDs, issues `CPM_CR_INIT_TRX`, clears/enables events, programs GSMR/DSR/PSMR Ethernet mode, applies duplex and multicast/promiscuous settings, and enables Rx/Tx. Stop masks events, clears enable bits, and cleans BDs.

## Dependencies and Integration Points
Depends on CPM command/MURAM APIs, SCC register definitions from architecture headers, OF IRQ/mapping, and common `fs_enet` descriptor/NAPI logic. `fs_enet-main.c` selects it for CPM SCC compatible strings when enabled.

## Risks and Test Signals
Risks include ignored `do_pd_setup` failures in `setup_data`, MURAM allocation/free mismatches, register dump size using pointer-size instead of parameter RAM structure size, SCC stop timeout logic, and multicast group programming correctness. Test signals include SCC probe on CPM1/CPM2, link-up/down, full-duplex mode, multicast/allmulti/promisc changes, Tx restart via CPM command, register dumps, and NAPI interrupt masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-scc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mii-bitbang.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mii-bitbang.c

## Purpose
Implements a CPM2 bit-banged MDIO bus for `fs_enet` FCC platforms using the kernel `mdio-bitbang` framework.

## Important APIs, Types, and Functions
Defines `struct bb_info` containing `mdiobb_ctrl`, direction/data register pointers, and MDIO/MDC masks. Important functions are bit operations `bb_set`, `bb_clr`, `bb_read`, mdiobb callbacks `mdio_dir`, `mdio_read`, `mdio`, `mdc`, `fs_mii_bitbang_init`, `fs_enet_mdio_probe`, and `fs_enet_mdio_remove`. The OF compatible is `fsl,cpm2-mdio-bitbang`.

## Control Flow and State
Probe allocates `bb_info`, creates an MDIO bitbang bus, parses the register resource plus `fsl,mdio-pin` and `fsl,mdc-pin`, maps the GPIO-like register block, computes bit masks, sets parent/driver data, and registers the bus with child PHY nodes. Runtime state is the mapped register block and masks. Remove unregisters the bus, frees bitbang structures, unmaps registers, and frees private memory.

## Dependencies and Integration Points
Depends on `mdio-bitbang`, OF address/MDIO/platform APIs, and big-endian port register accessors. Used by FCC-style `fs_enet` systems when `CONFIG_FS_ENET_MDIO_FCC` is enabled.

## Risks and Test Signals
Risks include unsynchronized read-modify-write of shared port pins, invalid pin numbers, resource size assumptions, leaked mappings on partial probe failure, and all PHYs masked until DT registration populates children. Test signals include MDIO scan/read/write with attached PHYs, concurrent GPIO user analysis, remove/unbind cleanup, and DT validation of pin properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mii-bitbang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mii-fec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mii-fec.c

## Purpose
Implements the FEC hardware MDIO bus used by `fs_enet` FEC controllers on PQ1 and MPC512x platforms.

## Important APIs, Types, and Functions
Important functions are `fs_enet_fec_mii_read`, `fs_enet_fec_mii_write`, `fs_enet_mdio_probe`, and `fs_enet_mdio_remove`. Probe creates a `mii_bus`, allocates `struct fec_info`, maps FEC registers, computes the MII clock divider from platform bus frequency or `ppc_proc_freq`, enables MII/Ethernet control bits, programs `fec_mii_speed`, and registers child PHYs. OF compatibles include `fsl,pq1-fec-mdio` and optionally `fsl,mpc5121-fec-mdio`.

## Control Flow and State
Read/write build FEC MII command words with PHY and register address, poll `FEC_ENET_MII` for up to `FEC_MII_LOOPS`, clear the event bit, and return data or timeout-like `-1` for read. Probe stores the mapped FEC pointer and calculated `mii_speed` in bus private state; the FEC MAC backend later reuses this `mii_speed` during controller restart.

## Dependencies and Integration Points
Depends on FEC register layout from `fs_enet.h`, constants from `fec.h`, OF MDIO registration, MPC5xxx bus-frequency helper when enabled, and PowerPC processor frequency fallback. It is selected by `CONFIG_FS_ENET_MDIO_FEC`.

## Risks and Test Signals
Risks include `BUG_ON` if MII mode is not enabled, write returning success even if polling timed out, divider overflow or inaccurate clock source, shared FEC registers being modified while netdev is active, and bus private assumptions by `mac-fec.c`. Test signals include PHY discovery, MDIO read/write timeout tests, MII clock measurement, FEC restart using stored speed, and MPC512x/PQ1 DT probe coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mii-fec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fsl_pq_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fsl_pq_mdio.c

## Purpose
Implements the Freescale PowerQUICC MDIO/MIIM platform driver used by Gianfar, eTSEC, UCC, and FMan MDIO nodes. It provides generic Clause 22 MDIO read/write/reset operations over Freescale MIIM registers and optional TBI PHY address and UCC mux setup.

## Important APIs, Types, and Functions
Defines MIIM register layouts `struct fsl_pq_mii` and `struct fsl_pq_mdio`, private state `fsl_pq_mdio_priv`, and per-compatible metadata `fsl_pq_mdio_data`. Core bus ops are `fsl_pq_mdio_read`, `fsl_pq_mdio_write`, and `fsl_pq_mdio_reset`. Helper selectors include `get_gfar_tbipa_from_mdio`, `get_gfar_tbipa_from_mii`, `get_etsec_tbipa`, `get_ucc_tbipa`, `ucc_configure`, and `set_tbipa`. Probe/remove are `fsl_pq_mdio_probe` and `fsl_pq_mdio_remove`.

## Control Flow and State
Probe selects compatible metadata, allocates an MDIO bus with private storage, maps the node resource, applies any MII register offset, sets bus ID/name/read/write/reset/parent, optionally finds a child `tbi-phy` and writes TBIPA through a second resource or computed address, optionally configures the owning UCC as MII management master, then registers child PHYs. Read/write program `miimadd`, `miimcon`/`miimcom`, poll `miimind` for busy/not-valid completion, and return data or timeout. Reset holds `bus->mdio_lock`, resets and initializes MIIM clock, then waits for idle.

## Dependencies and Integration Points
Depends on OF address/MDIO/platform APIs, Linux MII bus core, big-endian MMIO accessors, Gianfar register definitions when enabled, and QE/UCC mux APIs when UCC GETH is enabled. The compatible table covers legacy and modern MDIO/TBI node shapes, including `fsl,fman-mdio`.

## Risks and Test Signals
Risks include incorrect `mii_offset` for mixed MAC/MDIO maps, TBIPA address computation outside mapped ranges, timeout loops without sleeps, static one-time UCC master selection with multiple buses, freeing `mdiobus_alloc_size` memory with raw `kfree` on probe error, and FMan TBI handling split across drivers. Test signals include MDIO scan for each compatible, TBI PHY address programming, UCC mux setup, reset timeout behavior, read/write timeout injection, and probe/remove memory checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fsl_pq_mdio.c -->
