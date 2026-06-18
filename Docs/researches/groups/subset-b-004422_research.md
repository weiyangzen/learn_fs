# Research: subset-b-004422

Grouped research for Freescale/NXP DPAA FMan core, MAC, keygen, and MURAM sources. Each source file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.c

## Purpose

`fman.c` is the platform driver and central hardware bring-up layer for Freescale/NXP DPAA Frame Manager. It maps FMan device-tree resources, initializes the core register blocks (FPM, BMI, QMI, DMA, HW parser, KeyGen), allocates shared MURAM regions for DMA CAM and BMI FIFO, dispatches FMan and MAC interrupts, and exports the service APIs used by port and MAC drivers.

## Important APIs, Types, And Functions

The file defines internal big-endian register layouts for FPM, BMI, QMI, DMA, IRAM, and HWP blocks, plus `struct fman_state_struct` for runtime resource accounting and `struct fman_cfg` for one-shot initialization values. Public exported APIs include `fman_register_intr()`, `fman_unregister_intr()`, `fman_set_port_params()`, `fman_reset_mac()`, `fman_set_mac_max_frame()`, `fman_get_bmi_max_fifo_size()`, `fman_get_revision()`, `fman_get_qman_channel_id()`, `fman_get_mem_region()`, `fman_get_max_frm()`, `fman_get_rx_extra_headroom()`, and `fman_bind()`. With `CONFIG_DPAA_ERRATUM_A050385`, `fman_has_errata_a050385()` exports a global erratum flag read from device tree.

Key internal paths are `read_dts_node()`, `fman_config()`, `fman_init()`, `fman_reset()`, `dma_init()`, `fpm_init()`, `bmi_init()`, `qmi_init()`, `clear_iram()`, `enable_time_stamp()`, and `fill_soc_specific_params()`. Interrupt handling is split between `fman_err_irq()` for error pending bits and `fman_irq()` for normal pending bits.

## Control Flow

Module load registers a platform driver matching `fsl,fman`. Probe calls `read_dts_node()` to allocate `struct fman`, read `cell-index`, IRQs, clock, QMan channel range, and MURAM child resource, request normal/error IRQs, ioremap the FMan register resource, and populate child devices. `fman_config()` then allocates runtime state/config, creates a MURAM allocator, records register block pointers at fixed offsets, reads revision, applies SoC-specific limits, and prepares default thresholds. `fman_init()` saves LIODN state, resets the block, resumes QMI if halted, clears IRAM to avoid ECC noise, initializes DMA/FPM/BMI/QMI/HWP, allocates MURAM FIFO space, initializes KeyGen, enables BMI/QMI, enables timestamps, and frees the temporary config object to mark initialization complete.

Port setup enters through `fman_set_port_params()`. It takes `spinlock`, reserves task/FIFO/open-DMA resources, updates QMI thresholds for TX ports, restores LIODN programming, configures order restoration on pre-v3 hardware, and enforces that port max frame length is at least the MAC max frame length. MAC drivers register callbacks into `intr_mng[]`; the FMan IRQ handlers decode pending bits and fan out to module-specific handlers or registered MAC callbacks.

## State And Persistence Behavior

Persistent runtime state lives in `fman->state`, including revision, clock, exceptions, accumulated tasks/FIFO/open-DMA counts, per-MAC/port max frame lengths, QMan channel range, and SoC resource limits. `fman->cfg` exists only until successful init; `is_init_done()` treats a NULL config as initialized. MURAM allocations for CAM and FIFO are tracked by offsets and sizes. Boot/module parameters `fsl_fm_rx_extra_headroom` and `fsl_fm_max_frm` are lazily range-checked and then cached by static booleans on first getter call.

Hardware state is programmed via big-endian MMIO writes. LIODN values are read before reset and restored per port. Interrupt registration state is in memory and not persistent across driver reload.

## Dependencies And Integration Points

This file depends on Linux platform, OF, clock, IRQ, module, delay, and IO APIs; Freescale GUTS registers for FMan v3 reset erratum handling on PPC; `fman_muram` for MURAM allocation; and `fman_keygen` for KeyGen setup. Downstream integration is with MAC drivers (`fman_dtsec.c`, `fman_memac.c`, and peers), FMan port code via `fman_set_port_params()`, QMan channel consumers via `fman_get_qman_channel_id()`, and net buffer sizing via exported max-frame/headroom getters.

## Risks And Edge Cases

Resource accounting is manual and only grows; failed partial port setup can leave accumulated counters advanced because rollback is not performed after each reservation failure. Hardware polling uses short retry loops, making reset and IRAM failures sensitive to timing. Error IRQ absence disables many exception classes after init. `fman_bind()` increments the device reference through `get_device()` but returns only the driver pointer, so callers must follow the wider driver convention for device lifetime. This snapshot also shows apparent source corruption that a build should catch: doubled opening braces in `fman_bus_error()` and `fman_get_rx_extra_headroom()`, and a duplicate `case FMAN_EX_FPM_DOUBLE_ECC`.

## Test Signals

Build coverage is the first gate because this file has syntax-sensitive register structures and visible malformed tokens in the snapshot. Runtime validation should exercise probe failure paths, reset timeout handling, no-error-IRQ exception disabling, FMan v2/v3 revision branches, port resource exhaustion, LIODN restore with and without `CONFIG_FSL_PAMU`, module parameter range clamping, and MAC interrupt callback registration/unregistration. Hardware or emulation tests should confirm BMI/QMI thresholds, MURAM allocation offsets, KeyGen enablement, and normal/error IRQ fan-out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.h

## Purpose

`fman.h` is the internal/public interface for the DPAA Frame Manager driver family. It exposes frame descriptor status and command bits, buffer prefix layout structures, buffer pool/depletion descriptors, FMan exception and interrupt enums, core driver structs, port initialization parameters, and the exported APIs implemented by `fman.c`.

## Important APIs, Types, And Functions

Important definitions include frame descriptor command bits (`FM_FD_CMD_*`) and RX/TX/parser/keygen error bits (`FM_FD_ERR_*`), resource constants such as `FMAN_BMI_FIFO_UNITS`, `BM_MAX_NUM_OF_POOLS`, and `MAX_NUM_OF_MACS`, and the opaque `struct fman`. `struct fman_prs_result` describes the parser result layout passed in buffer prefix context. `struct fman_buffer_prefix_content`, `struct fman_ext_pools`, and `struct fman_buf_pool_depletion` define buffer layout and BMan depletion policy inputs shared with port code.

The file defines `enum fman_exceptions`, `enum fman_event_modules`, `enum fman_intr_type`, and `enum fman_inter_module_event`, plus callback typedefs `fman_exceptions_cb` and `fman_bus_error_cb`. `struct fman_dts_params`, `struct fman`, and `struct fman_port_init_params` form the main cross-file data contract.

## Control Flow

No executable flow exists here, but the header dictates the call sequence among modules. Platform probe constructs `struct fman`; MAC drivers register interrupt callbacks with `fman_register_intr()`; port drivers pass resource needs through `fman_set_port_params()`; MAC drivers synchronize max frame length through `fman_set_mac_max_frame()`; and consumers query clock, FIFO limits, QMan channels, memory resource, max frame size, and RX headroom through getters.

## State And Persistence Behavior

`struct fman` owns MMIO register pointers, callback slots, a spinlock, runtime `state`, temporary `cfg`, MURAM allocator, KeyGen handle, CAM/FIFO MURAM offsets, saved LIODN tables, and parsed device-tree parameters. The header only forward-declares several internal register/state types, keeping most implementation details private to `fman.c` while allowing pointer storage.

## Dependencies And Integration Points

The header depends on Linux IO, interrupt, and OF IRQ types. It is included by MAC implementations, port code, MURAM/keygen users indirectly, and any FMan consumer needing exported APIs. The frame descriptor and parser-result definitions integrate with DPAA datapath buffer handling outside this subset.

## Risks And Edge Cases

Because this header exposes concrete `struct fman`, many implementation fields become visible across compilation units, increasing coupling. `MAX_NUM_OF_MACS` and `FMAN_EV_CNT` fix array sizes used by interrupt dispatch and max-frame tracking. Enum-to-bit mappings are implemented separately in `fman.c`; any enum changes must update those mappings. The parser-result structure relies on exact hardware layout and endian annotations.

## Test Signals

Compile tests should cover all includers and configurations for `CONFIG_DPAA_ERRATUM_A050385`. ABI-like checks should verify parser-result and port-parameter sizes against hardware expectations. Integration tests should ensure MAC and port callers obey the declared port id, max-frame, and callback contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.c

## Purpose

`fman_dtsec.c` implements the 1G dTSEC MAC backend for FMan. It configures dTSEC registers, integrates with phylink and a TBI PCS, manages MAC address filtering and multicast hash tables, handles dTSEC and 1588 timestamp interrupts, and installs a `mac_device` operation table used by the surrounding DPAA Ethernet driver.

## Important APIs, Types, And Functions

The file defines the dTSEC register map (`struct dtsec_regs`), configuration structure (`struct dtsec_cfg`), and private MAC state (`struct fman_mac`). Initialization enters through exported `dtsec_initialization()`, which sets `mac_device` callbacks, creates the private object with `dtsec_config()`, finds the `tbi-handle` MDIO device, advertises supported phylink interfaces, and calls `dtsec_init()`.

Important operations include `dtsec_mac_config()`, `dtsec_link_up()`, `dtsec_link_down()`, `dtsec_select_pcs()`, `dtsec_modify_mac_address()`, `dtsec_add_hash_mac_address()`, `dtsec_del_hash_mac_address()`, `dtsec_set_promiscuous()`, `dtsec_set_allmulti()`, `dtsec_set_tstamp()`, and `dtsec_set_exception()`. Interrupt handlers are `dtsec_isr()` and `dtsec_1588_isr()`.

## Control Flow

`dtsec_initialization()` populates phylink and MAC callbacks, allocates/configures `struct fman_mac`, applies the global FMan max frame size, resolves an available TBI PCS node, and registers phylink interface capabilities based on device-tree mode and hardware capability bits. `dtsec_init()` optionally resets the MAC, validates configuration and callbacks, calls the low-level `init()` register programming routine, resets/configures the TBI control register, reports max frame length to FMan, allocates multicast/unicast hash tables, and registers error and normal interrupt callbacks with FMan.

At link-up, the driver programs pause behavior, speed bits, duplex and byte/nibble mode, calls `mac_dev->update_speed()`, enables RX/TX, and clears graceful stop bits. Link-down asserts graceful stop and disables RX/TX. Address changes stop the MAC gracefully, write station address registers, and restart.

## State And Persistence Behavior

Private state stores the MMIO register pointer, MAC address, phy interface, callbacks, hash tables, exception mask, PTP flags, TBI MDIO device, PCS wrapper, and saved FMan revision. Hash entries are allocated in software lists and mirrored into dTSEC hash registers. Exception state is kept in `dtsec->exceptions` and the hardware `imask`. Runtime link state persists in hardware registers until reconfigured by phylink callbacks.

## Dependencies And Integration Points

The file depends on `fman.h`, `fman_mac.h`, and `mac.h`, plus Linux phylink/PHY/MDIO, CRC32, bit reversal, OF MDIO, IO, and delay APIs. It integrates upward through `mac_device` callbacks and downward through FMan interrupt registration and max-frame validation. `tbi-handle` in device tree is mandatory for PCS access.

## Risks And Edge Cases

The dTSEC errata paths are timing-sensitive and include a documented race in the TX FIFO underrun workaround. Hash programming depends on CRC-derived buckets; bucket collisions are tracked in software lists so removal must preserve bits until a bucket is empty. The driver rejects unicast hash operations when group hash translation is active. This snapshot contains apparent compile-breaking anomalies: duplicated `tdfr` member in `struct dtsec_regs`, an extra brace after `check_init_parameters()`, and a duplicated `dtsec->exceptions &= ~bit_mask;` line.

## Test Signals

Build tests should catch the malformed struct/braces. Runtime tests should cover SGMII/1000BASE-X/2500BASE-X PCS selection, RGMII/RMII mode programming, link-up/down register effects, pause frame configuration including illegal FMan v2 pause time, multicast/unicast hash add/delete collisions, allmulti/promiscuous toggles, timestamp enable and 1588 error interrupts, and error interrupt callback mapping for all enabled dTSEC events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.h

## Purpose

`fman_dtsec.h` is the narrow declaration header for the dTSEC MAC backend. It includes the shared FMan MAC definitions and exposes `dtsec_initialization()` to the MAC device probing layer.

## Important APIs, Types, And Functions

The only API is `int dtsec_initialization(struct mac_device *mac_dev, struct device_node *mac_node, struct fman_mac_params *params);`. `struct mac_device` is forward-declared, while `struct fman_mac_params` and callback types come from `fman_mac.h`.

## Control Flow

Callers allocate and populate a generic `mac_device`, parse the FMan MAC device-tree node, prepare `fman_mac_params`, and then call `dtsec_initialization()`. The implementation fills operation pointers, configures registers, resolves PCS resources, and registers FMan interrupt callbacks.

## State And Persistence Behavior

No state is stored in the header. It creates a compile-time contract that `mac_dev->fman_mac` will be initialized and owned by the dTSEC implementation on success.

## Dependencies And Integration Points

This header integrates `fman_dtsec.c` with the generic FMan MAC probing code. It depends on `fman_mac.h` and Linux device-tree types through the function signature.

## Risks And Edge Cases

The contract does not describe ownership or cleanup semantics; callers must rely on the implementation and surrounding MAC framework. Since only one function is exposed, any signature change requires updates to the generic MAC factory code.

## Test Signals

Compile all dTSEC-enabled configurations and verify the generic MAC probe can include this header without circular dependencies. Probe tests should exercise successful and deferred PCS lookup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.c

## Purpose

`fman_keygen.c` initializes and programs the FMan KeyGen hardware, specifically the scheme and port binding machinery used here for RX hashing/spreading across frame queues. It provides a small exported interface for global KeyGen initialization and per-port hash scheme setup.

## Important APIs, Types, And Functions

The file defines KeyGen register layouts (`struct fman_kg_scheme_regs`, `struct fman_kg_pe_regs`, `struct fman_kg_regs`), software scheme state (`struct keygen_scheme`), and driver state (`struct fman_keygen`). Exported functions are `keygen_init()` and `keygen_port_hashing_init()`.

Internal helpers include `keygen_write_ar_wait()` for indirect action-register operations, builders for scheme/port/classification-plan action words, `keygen_write_sp()`, `keygen_write_cpp()`, `keygen_write_scheme()`, `get_free_scheme_id()`, `get_scheme()`, `keygen_bind_port_to_schemes()`, and `keygen_scheme_setup()`.

## Control Flow

`keygen_init()` allocates driver state, stores the MMIO base, writes global defaults, clears global default values, iterates over all 64 hardware ports to clear scheme and classification-plan bindings, enables all scheme interrupts, and sets the global enable bit. FMan core calls this during `fman_init()` after the parser/BMI/QMI blocks are initialized.

`keygen_port_hashing_init()` validates a nonzero 24-bit base FQID and power-of-two hash size, finds a free scheme, clears its software state, fills hard-coded IPv4/L4/IPsec SPI extraction/hash configuration, writes the scheme through indirect registers, marks it used, then binds the hardware port to the scheme.

## State And Persistence Behavior

Software state tracks 32 schemes in memory and whether each is used, its bound hardware port, base FQID, hash queue count, symmetric hash flag, hash shift, and match vector. Hardware state is persisted in KeyGen registers and port entries until reset or overwritten. No explicit free/unbind API exists in this subset, so schemes are effectively one-way allocations after initialization.

## Dependencies And Integration Points

The file depends on Linux IO and slab allocation, and on `fman_keygen.h`. It is integrated by `fman.c`, which passes the KeyGen register offset and stores the returned handle. Port/RX code outside this subset can call `keygen_port_hashing_init()` through the exported symbol to enable hash distribution for a hardware port.

## Risks And Edge Cases

`keygen_write_ar_wait()` busy-waits without a timeout, so hardware that never clears GO can hang the caller. The hash configuration is hard-coded and notes that symmetric hash is disabled because spreading did not work in tests. There is no rollback if scheme setup succeeds but port binding fails, leaving a used unbound scheme. This snapshot contains an apparent duplicated partial line in `keygen_scheme_setup()` around `KG_SCH_DEF_USE_KGSE_DV_1`, which should be caught by compilation.

## Test Signals

Compile tests should validate the apparent malformed line. Unit-style hardware mocks should test action-register error handling, scheme exhaustion, invalid FQID and non-power-of-two hash sizes, successful register programming fields, and binding failure behavior. Runtime tests should verify packets distribute over the configured queue range and that reset/reprobe clears stale scheme bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.h

## Purpose

`fman_keygen.h` exposes the minimal KeyGen API used by FMan core and port code. It keeps both `struct fman_keygen` and `struct fman_kg_regs` opaque while declaring initialization and per-port hashing configuration.

## Important APIs, Types, And Functions

The header forward-declares `struct fman_keygen` and `struct fman_kg_regs`. It declares `keygen_init(struct fman_kg_regs __iomem *keygen_regs)` and `keygen_port_hashing_init(struct fman_keygen *keygen, u8 hw_port_id, u32 hash_base_fqid, u32 hash_size)`.

## Control Flow

FMan core calls `keygen_init()` during hardware initialization and stores the returned handle. Later code can call `keygen_port_hashing_init()` to allocate a scheme and bind it to a hardware port for RX queue spreading.

## State And Persistence Behavior

No state lives in the header. The opaque handle represents software scheme ownership and points at persistent hardware registers programmed by the implementation.

## Dependencies And Integration Points

The header depends on Linux IO annotations and integer types. It is included by `fman.c` and any port code that configures RX hashing.

## Risks And Edge Cases

The API has no destroy, unbind, or scheme-release function, so users cannot recover a scheme through this interface after failed or obsolete configuration. The hash-size and FQID constraints are only documented/enforced by the implementation.

## Test Signals

Compile tests should cover users with sparse/IO annotations. Integration tests should verify callers do not pass a NULL KeyGen handle and that invalid hash parameters return errors without consuming schemes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_mac.h

## Purpose

`fman_mac.h` defines the shared MAC-layer contract for FMan MAC implementations. It provides Ethernet address helpers, pause/PFC constants, MAC exception enums, hash-list support, callback typedefs, and the initialization parameter structure used by dTSEC and mEMAC backends.

## Important APIs, Types, And Functions

Important types are `enet_addr_t`, `enum fman_mac_exceptions`, `struct fman_mac_params`, `struct eth_hash_entry`, and `struct eth_hash_t`. The address conversion macros `ENET_ADDR_TO_UINT64()` and `MAKE_ENET_ADDR_FROM_UINT64()` normalize 48-bit MAC addresses into the representation used by the backends. Inline helpers `dequeue_addr_from_hash_entry()`, `free_hash_table()`, and `alloc_hash_table()` implement the software hash table backing multicast/unicast filter programming.

## Control Flow

MAC implementations allocate hash tables with `alloc_hash_table()`, add/remove `eth_hash_entry` nodes as hardware hash bits are changed, and call `free_hash_table()` from their cleanup paths. Exception callbacks point back to the generic MAC device layer, allowing backend interrupt handlers to report MAC-specific events.

## State And Persistence Behavior

The hash table stores lists of dynamically allocated entries per hardware bucket so drivers can leave a hardware hash bit enabled while multiple addresses collide in the same bucket. The header itself does not persist state, but its inline cleanup owns freeing all list entries and bucket arrays.

## Dependencies And Integration Points

The header includes `fman.h`, Linux slab, PHY, and Ethernet headers. It is shared by `fman_dtsec.c`, `fman_memac.c`, and their small public headers. It also depends on local allocation helper macros such as `kmalloc_obj()` and `kmalloc_objs()` being available from the wider tree.

## Risks And Edge Cases

`ETH_HASH_ENTRY_OBJ` uses `hlist_entry_safe` even though `struct eth_hash_entry::node` is a `struct list_head`; this is suspicious and should be validated against local macro definitions or compilation. Hash helper functions are inline in the header, so bugs replicate into every MAC backend. The exception enum merges 1G, 10G, mEMAC, and timestamp events, requiring each backend to reject unsupported values cleanly.

## Test Signals

Build all MAC backends to catch list helper type mismatches. Exercise hash allocation failure, freeing partially populated tables, bucket collision removal, and unsupported exception mappings in dTSEC and mEMAC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.c

## Purpose

`fman_memac.c` implements the mEMAC backend for FMan, supporting 1G/2.5G/10G-oriented interfaces, PCS selection, optional SerDes control, MAC filtering, pause configuration, interrupt handling, phylink integration, and ethtool statistics.

## Important APIs, Types, And Functions

The file defines `struct memac_regs`, `struct memac_cfg`, and private `struct fman_mac`. Exported entry is `memac_initialization()`. The `mac_device` callbacks installed include `memac_set_promiscuous()`, `memac_modify_mac_address()`, `memac_add_hash_mac_address()`, `memac_del_hash_mac_address()`, `memac_set_exception()`, `memac_set_allmulti()`, `memac_set_tstamp()`, `memac_enable()`, `memac_disable()`, and ethtool stat readers.

Phylink operations are `memac_get_caps()`, `memac_select_pcs()`, `memac_prepare()`, `memac_mac_config()`, `memac_link_up()`, and `memac_link_down()`. Interrupt callbacks are `memac_err_exception()` and `memac_exception()`.

## Control Flow

`memac_initialization()` normalizes legacy XGMII to 10GBASE-R, installs callbacks, allocates/configures private state, creates named PCS handles for XFI/QSGMII/SGMII with compatibility fallback, optionally obtains a SerDes PHY, derives supported interface masks, applies SoC-specific half-duplex restrictions, defaults in-band autonegotiation when appropriate, and calls `memac_init()`.

`memac_init()` validates callbacks, optionally performs software reset, writes the primary MAC address, initializes command config/max-frame/pause/interrupt registers, applies an RX FIFO corruption erratum for FMan 6.0/6.3 by disabling CRC forwarding, validates max frame length with FMan core, allocates hash tables, and registers error/normal FMan interrupt callbacks. Link-up configures pause, IF_MODE speed/duplex, TX FIFO sections for 10G or 1G speeds, notifies `update_speed()`, and enables RX/TX. Link-down disables RX/TX.

## State And Persistence Behavior

Private state tracks register base, MAC address, callbacks, hash tables, exception mask, FMan revision, PCS handles, optional SerDes, allmulti flag, and RGMII half-duplex restriction. Hash state is software-list based for multicast only; unicast hash adds are rejected. Etthool stat functions read 64-bit counters by sampling high/low/high until stable.

## Dependencies And Integration Points

This file depends on FMan core APIs, shared MAC helpers, generic `mac_device`, phylink, Lynx PCS, Linux PHY/SerDes APIs, fixed PHY support, and OF MDIO/property helpers. It integrates with FMan by calling `fman_get_revision()`, `fman_get_max_frm()`, `fman_set_mac_max_frame()`, and interrupt registration APIs.

## Risks And Edge Cases

PCS fallback behavior is compatibility-sensitive when `pcs-handle-names` is absent. Optional SerDes affects supported interface discovery; without SerDes, only the default interface is assumed supported. `memac_enable()` must unwind `phy_init()` if `phy_power_on()` fails, which it does. Hash delete does not warn if an address was missing. The normal interrupt path masks with `MEMAC_ALL_ERRS_IMASK`, so magic-packet notification handling deserves scrutiny because the comment and mask naming focus on error bits. This snapshot has an apparent extra brace after `memac_config()`, which a build should catch.

## Test Signals

Build tests should catch syntax anomalies and all optional PHY/PCS configurations. Probe tests should cover named PCS handles, unnamed fallback, missing PCS, deferred PCS, optional SerDes success/failure, and machine-compatible half-duplex restrictions. Runtime tests should exercise link-up/down for MII/RGMII/SGMII/QSGMII/10GBASE-R, 10G TX FIFO settings, multicast hash collisions/allmulti transitions, pause stats, RMON and IEEE stats, SerDes power sequencing, and mEMAC exception callback mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.h

## Purpose

`fman_memac.h` is the declaration header for the mEMAC backend. It exposes the mEMAC initialization entry point and pulls in shared MAC, netdevice, and fixed-PHY definitions needed by callers.

## Important APIs, Types, And Functions

The only API is `int memac_initialization(struct mac_device *mac_dev, struct device_node *mac_node, struct fman_mac_params *params);`. `struct mac_device` is forward-declared, and shared MAC callback/config types are inherited from `fman_mac.h`.

## Control Flow

The generic MAC probing layer calls `memac_initialization()` after creating a `mac_device` and parsing device-tree parameters. The implementation fills operation callbacks, creates PCS/SerDes resources, initializes hardware, and registers FMan interrupts.

## State And Persistence Behavior

No state is stored here. Successful initialization leaves private mEMAC state attached to `mac_dev->fman_mac`.

## Dependencies And Integration Points

This header depends on `fman_mac.h`, Linux netdevice, and fixed PHY headers. It is included by the generic MAC layer when selecting an mEMAC implementation.

## Risks And Edge Cases

The header does not encode ownership, supported interfaces, or cleanup behavior; these are implementation contracts. Including fixed PHY and netdevice headers can increase compile dependencies for users that only need the function prototype.

## Test Signals

Compile mEMAC-enabled and disabled configurations. Probe-level tests should ensure the caller handles `-EPROBE_DEFER`, missing PCS, and other initialization errors returned through this single entry point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.c

## Purpose

`fman_muram.c` provides a small allocator wrapper for FMan MURAM, the internal multi-user RAM used by FMan blocks for structures such as DMA CAM and BMI FIFO. It maps a physical MURAM partition, creates a genalloc pool, zeroes memory, and returns offsets suitable for programming into FMan registers.

## Important APIs, Types, And Functions

The private `struct muram_info` stores a `gen_pool`, virtual base, and physical base. Public functions are `fman_muram_init()`, `fman_muram_offset_to_vbase()`, `fman_muram_alloc()`, and `fman_muram_free_mem()`. Internal `fman_muram_vbase_to_offset()` converts allocated virtual addresses back to hardware offsets.

## Control Flow

`fman_muram_init()` allocates `muram_info`, creates a gen_pool with 64-byte granularity, ioremaps the physical MURAM range, adds the virtual/physical mapping to the pool, zeroes the partition, and returns the handle. `fman_muram_alloc()` allocates from the pool, zeroes the allocation, and returns an offset from the mapped base. `fman_muram_free_mem()` converts an offset back to virtual address and frees the range.

## State And Persistence Behavior

Allocator state is held in the gen_pool and the virtual mapping. Allocated blocks are returned as offsets, not virtual addresses, matching FMan register programming. Memory is zeroed both at partition initialization and per allocation. There is no public destroy function in this subset, so pool/mapping teardown is absent for normal driver removal.

## Dependencies And Integration Points

The file depends on Linux IO, slab, and genalloc APIs. FMan core uses it to allocate DMA CAM and FIFO space, and any other FMan component can convert offsets back to virtual base for direct initialization.

## Risks And Edge Cases

Allocation failure returns `-ENOMEM` cast through `unsigned long`, so callers must use `IS_ERR_VALUE()` rather than NULL checks. Missing destroy/unmap support can matter for hot-unplug or probe-failure cleanup beyond the paths shown. `fman_muram_free_mem()` trusts offset and size; invalid inputs can corrupt the pool.

## Test Signals

Tests should cover init failure at allocation, pool creation, ioremap, and pool-add stages; allocation alignment and zeroing; offset-to-vbase round trips; freeing and reallocating; and caller behavior for `IS_ERR_VALUE()` allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.h

## Purpose

`fman_muram.h` declares the MURAM allocator interface used by FMan core and related modules. It keeps `struct muram_info` opaque and exposes offset-based allocation helpers.

## Important APIs, Types, And Functions

The header defines `FM_MURAM_INVALID_ALLOCATION` and forward-declares `struct muram_info`. It declares `fman_muram_init()`, `fman_muram_offset_to_vbase()`, `fman_muram_alloc()`, and `fman_muram_free_mem()`.

## Control Flow

FMan core initializes a MURAM handle from the device-tree MURAM resource, allocates hardware work areas by size, programs returned offsets into hardware registers, converts offsets to virtual addresses only when it must initialize memory directly, and frees offsets on error paths.

## State And Persistence Behavior

State is hidden behind the `muram_info` handle. Allocation identity is an offset relative to the MURAM partition base, matching hardware-visible addressing rather than CPU virtual pointers.

## Dependencies And Integration Points

The header depends only on Linux types. It is included by `fman.c` and any FMan submodule requiring MURAM memory.

## Risks And Edge Cases

`FM_MURAM_INVALID_ALLOCATION` is `-1`, while the implementation returns `-ENOMEM` on allocation failure. Callers must not check only this constant. No destroy API is declared, so lifecycle management is incomplete for full unload scenarios.

## Test Signals

Compile users should verify error checks use `IS_ERR_VALUE()`. Runtime tests should confirm offsets are valid for hardware programming and that frees use exactly the originally allocated size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.h -->
