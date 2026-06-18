# Research: subset-b-005918

This grouped report covers the source files assigned to `subset-b-005918`. Each section is keyed by the exact source path and is intended to be split into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smsc911x.h -->
# sources/distributed-fs/ceph-client/include/linux/smsc911x.h

Purpose: This header defines the platform-data contract for the SMSC LAN911x/LAN921x Ethernet controller driver. It is used by non-DT or board-file style platform devices to describe interrupt wiring, bus width, PHY selection, and an optional fixed MAC address.

Important APIs/types/functions: The only exported type is `struct smsc911x_platform_config`, with `irq_polarity`, `irq_type`, `flags`, `shift`, `phy_interface`, and `mac[ETH_ALEN]`. Constants define active-low/high IRQ polarity, open-drain/push-pull IRQ type, 16-bit/32-bit access flags, internal/external PHY forcing, MAC-address preservation, and `SMSC911X_SWAP_FIFO`.

Control flow: There is no executable flow in the header. The network driver reads the struct during platform-device probe, then chooses register access width, IRQ configuration, PHY binding, and FIFO byte-swapping behavior.

State and persistence: Configuration is static platform state attached to `dev.platform_data`. The MAC address field may seed persistent network identity if `SMSC911X_SAVE_MAC_ADDRESS` is selected.

Dependencies and integration: Depends on `linux/phy.h` for `phy_interface_t` and `linux/if_ether.h` for `ETH_ALEN`. Integrates with platform bus Ethernet devices and PHYLIB.

Risks and test signals: Mis-set bus width, shift, FIFO byte-swap, or PHY flags can produce silent packet corruption or probe failure. Useful tests are platform probe, PHY attach, IRQ delivery, link up/down, and traffic on big-endian or board-file systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smsc911x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smscphy.h -->
# sources/distributed-fs/ceph-client/include/linux/smscphy.h

Purpose: This header centralizes SMSC/Microchip Ethernet PHY register definitions and shared helper prototypes for LAN83C185/LAN87xx PHY drivers, including interrupts, energy detect, and wake-on-LAN programming.

Important APIs/types/functions: It names MII registers such as `MII_LAN83C185_ISF`, `IM`, `CTRL_STATUS`, and `SPECIAL_MODES`; interrupt bits for link down, auto-negotiation complete, and energy-on; power and mode masks; and LAN874x MMD wake filters, PME, magic packet, broadcast, and pattern-detect bits. It declares `smsc_phy_config_intr`, `smsc_phy_handle_interrupt`, `smsc_phy_config_init`, `lan87xx_read_status`, tunable get/set helpers, and `smsc_phy_probe`.

Control flow: PHY drivers include this header to implement probe/config/init, configure interrupt masks, service PHY interrupt status, read link state, and expose ethtool tunables.

State and persistence: State lives in PHY registers and MMD WOL registers. WOL filters and PME state can persist across suspend depending on PHY power mode.

Dependencies and integration: The prototypes consume `struct phy_device`, `irqreturn_t`, and `struct ethtool_tunable`, tying the header to PHYLIB, IRQ handling, and ethtool.

Risks and test signals: Incorrect interrupt masks can miss link changes or storm interrupts. WOL bit placement is hardware-sensitive. Test with PHY interrupt mode, polling fallback, link renegotiation, suspend/resume WOL, and ethtool tunable reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smscphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/actions/owl-sps.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/actions/owl-sps.h

Purpose: This tiny Actions Semi Owl SoC header exposes a system power switch helper for changing power-gate state through SPS registers.

Important APIs/types/functions: It declares `owl_sps_set_pg(void __iomem *base, u32 pwr_mask, u32 ack_mask, bool enable)`. The arguments identify the MMIO base, the power-control bit mask, the acknowledgement bit mask, and whether the domain is being enabled or disabled.

Control flow: Callers pass the already mapped SPS base and domain-specific masks. The implementation is expected to write the power gate request and poll or check acknowledgement.

State and persistence: State is entirely hardware PM state in SPS registers. Changes affect power domains and therefore the availability of dependent IP blocks until the next power transition.

Dependencies and integration: Requires MMIO annotations and integer types from common kernel headers. It integrates with Actions Owl power-domain or clock/reset code that owns the SPS register map.

Risks and test signals: Bad masks can power down the wrong block or hang waiting for an ack. Validate by toggling each domain, checking register ack transitions, and boot-testing peripherals that depend on the domain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/actions/owl-sps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/airoha/airoha_offload.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/airoha/airoha_offload.h

Purpose: This header defines Airoha network offload integration between Ethernet PPE/NPU providers and WLAN or network consumers. It covers PPE callbacks, NPU DMA descriptors, WLAN command IDs, IRQ helpers, and optional stubs when the Airoha drivers are not enabled.

Important APIs/types/functions: `struct airoha_ppe_dev` carries `setup_tc_block_cb` and `check_skb` operations plus private data. `airoha_ppe_get_dev`/`put_dev` acquire the PPE provider. `struct airoha_npu_rx_dma_desc` and `struct airoha_npu_tx_dma_desc` define packed RX/TX DMA descriptors with bit masks for length, done, packet ID, FOE ID, SID, radio/VAP/frame type, and TXWI data. `enum airoha_npu_wlan_set_cmd` and `enum airoha_npu_wlan_get_cmd` enumerate message IDs for PCIE addresses, descriptors, BA windows, token sizes, counters, DMA addresses, and NPU versions. `struct airoha_npu` conditionally contains device, regmap, per-core spinlocks/work items, IRQs, stats, and operation hooks.

Control flow: Consumers acquire PPE or NPU handles, call inline wrappers, and dispatch through provider operation tables. WLAN setup sends set/get messages, fetches queue addresses, and manages NPU IRQ state. PPE paths can inspect SKBs and attach TC block offload.

State and persistence: Runtime state is in provider-owned `priv`, NPU cores, spinlock-protected memory accesses, IRQ status, DMA rings, firmware/shared memory, and hardware stats. The header itself stores no state.

Dependencies and integration: Includes `skbuff`, `spinlock`, and `workqueue`; uses `struct device`, `regmap`, `gfp_t`, DMA addresses, and optional `CONFIG_NET_AIROHA`/`CONFIG_NET_AIROHA_NPU`. It integrates with netdev TC offload, WLAN datapaths, PPE flow offload, and NPU firmware messaging.

Risks and test signals: Inline wrappers assume operation pointers are valid after successful acquisition. Descriptor packing, endianness, and queue IDs are fragile. Test provider-disabled builds, module builds, SKB offload checks, TC setup, NPU reserved-memory initialization, IRQ enable/disable, DMA ring ownership, and firmware command round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/airoha/airoha_offload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/amd/isp4_misc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/amd/isp4_misc.h

Purpose: This AMD SoC header publishes one shared string constant identifying the AMD ISP4 display I2C adapter name.

Important APIs/types/functions: It defines `AMDISP_I2C_ADAP_NAME` as `"AMDISP DesignWare I2C adapter"`. There are no structs or functions.

Control flow: There is no runtime flow. Drivers include the header to use an identical adapter-name string when registering, finding, or matching the DesignWare I2C adapter associated with AMD display/ISP plumbing.

State and persistence: No state is stored. The value affects naming and lookup identity in driver registration paths.

Dependencies and integration: It has no include dependencies beyond the compiler and is guarded by `__SOC_ISP4_MISC_H`. It integrates with AMD ISP/display and I2C adapter code through a shared string contract.

Risks and test signals: The risk is string drift: producers and consumers must use the same constant or adapter lookup may fail. Test by checking adapter registration names and any consumers that call into I2C by name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/amd/isp4_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/amlogic/meson-canvas.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/amlogic/meson-canvas.h

Purpose: This Amlogic Meson header defines the canvas allocator/configuration API used by video/display clients to program hardware canvas entries that describe pixel-buffer layout.

Important APIs/types/functions: It defines wrap modes (`MESON_CANVAS_WRAP_NONE`, `_X`, `_Y`), block modes (`LINEAR`, `32x32`, `64x64`), endian-swap modes, an opaque `struct meson_canvas`, and APIs `meson_canvas_get`, `meson_canvas_alloc`, `meson_canvas_free`, and `meson_canvas_config`.

Control flow: A consumer gets a canvas provider from its device, allocates a canvas index, configures the index with physical address, stride, height, wrapping, tiling, and endian mode, then frees the index when done.

State and persistence: The provider tracks canvas index ownership and writes persistent hardware table entries until reconfigured or freed. The caller owns buffer lifetime and physical address validity.

Dependencies and integration: Includes `linux/kernel.h` and uses `struct device`. Integrates with Meson DRM, VPU, video decoder, and other multimedia drivers using shared canvas hardware.

Risks and test signals: Wrong stride, block mode, endian mode, or stale physical address causes corrupted scanout/video. Test allocation exhaustion, double-free handling, display/video rendering for each block mode, and suspend/resume restoration if the provider loses register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/amlogic/meson-canvas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/andes/irq.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/andes/irq.h

Purpose: This Andes RISC-V header publishes SoC-specific interrupt and CSR numbers used by Andes PMU and supervisor local interrupt code.

Important APIs/types/functions: It defines `ANDES_RV_IRQ_PMOVI` as interrupt 18, `ANDES_RV_IRQ_LAST`, `ANDES_SLI_CAUSE_BASE`, and PMU-related CSRs `ANDES_CSR_SLIE`, `ANDES_CSR_SLIP`, and `ANDES_CSR_SCOUNTEROF`.

Control flow: There is no executable flow. Low-level irqchip or perf/PMU code uses these constants to map counter overflow and SLI causes to Linux IRQ handling.

State and persistence: State exists in CPU CSRs and interrupt pending/enable registers. The header only names those hardware resources.

Dependencies and integration: It is standalone and integrates with RISC-V arch code, Andes irqchip support, and performance counter overflow handling.

Risks and test signals: Wrong CSR or IRQ numbering breaks PMU overflow interrupts or local interrupt dispatch. Test perf counter overflow, IRQ domain mapping, and boot on Andes cores with SLI enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/andes/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/apple/rtkit.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/apple/rtkit.h

Purpose: This header defines the client API for Apple RTKit, the mailbox-based runtime protocol used to boot, manage, and exchange messages with Apple coprocessors.

Important APIs/types/functions: `struct apple_rtkit_shmem` describes shared-memory buffers with IOVA, size, buffer pointer, DMA address, and private cookie. `struct apple_rtkit_ops` provides callbacks for crashed state, received messages, shared-memory setup/destruction, and power/state events. The opaque `struct apple_rtkit` is created by `devm_apple_rtkit_init` or `apple_rtkit_init`. Lifecycle APIs include `apple_rtkit_free`, `reinit`, `boot`, `quiesce`, `wake`, `shutdown`, `poweroff`, `idle`, state queries, endpoint start, message send with completion control, and polling.

Control flow: A device initializes RTKit with ops and cookie, boots the coprocessor, starts endpoints, handles callbacks as messages arrive, sends endpoint messages, and transitions through idle/wake/quiesce/shutdown as the device power state changes.

State and persistence: RTKit owns mailbox protocol state, running/crashed flags, endpoint state, shared-memory mappings, and DMA buffers. Firmware-side state persists while the coprocessor remains powered.

Dependencies and integration: Uses `struct device`, DMA addresses, completions/timeouts, and Apple mailbox/coprocessor providers. Integrates with Apple GPU, ISP, audio, storage, and other RTKit-managed devices.

Risks and test signals: Message ordering, endpoint readiness, shared-memory lifetime, and crash recovery are high risk. Test boot/reboot, endpoint start failure, timeout behavior, crash callback delivery, suspend/resume, DMA mapping cleanup, and polling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/apple/rtkit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/apple/sart.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/apple/sart.h

Purpose: This header exposes Apple SART access-control management for devices that need to allow or revoke DMA-visible physical memory regions through Apple system address range tables.

Important APIs/types/functions: It declares opaque `struct apple_sart`, `devm_apple_sart_get`, `apple_sart_add_allowed_region`, and `apple_sart_remove_allowed_region`. Regions are expressed as physical address and size.

Control flow: A consumer gets the SART provider for its device, adds allowed regions before firmware/device DMA access, and removes them when buffers are no longer valid.

State and persistence: SART hardware stores access-control entries. The provider likely tracks slot allocation and region ownership; entries persist until removed or hardware reset.

Dependencies and integration: Uses `struct device` and `phys_addr_t`. Integrates with Apple DMA-capable coprocessor drivers, RTKit clients, and platform security/IO mapping code.

Risks and test signals: Failure to add entries blocks device DMA; failure to remove entries leaves stale DMA access to memory. Overlapping or incorrectly sized regions can violate isolation. Test DMA success/failure around add/remove, cleanup on probe errors, suspend/resume, and teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/apple/sart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/apple/tunable.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/apple/tunable.h

Purpose: This header describes Apple tunable register programming parsed from firmware/device-tree data and applied to MMIO blocks.

Important APIs/types/functions: `struct apple_tunable` holds parsed register/value/mask style data for a tunable sequence. `devm_apple_tunable_parse` parses a named property or node for a device and returns managed tunable data. `apple_tunable_apply(void __iomem *regs, struct apple_tunable *tunable)` applies the sequence to a mapped register block.

Control flow: Platform drivers parse tunables during probe, map their hardware registers, then apply the tunable at the appropriate initialization or power-up point.

State and persistence: Parsed tunable data is managed with the device lifetime. Applied values persist in hardware registers until reset, power loss, or later writes.

Dependencies and integration: Uses `struct device` and MMIO annotations. It integrates with Apple SoC drivers that need firmware-provided register tweaks without hard-coding every variant.

Risks and test signals: Wrong property parsing, missing masks, or applying tunables before clocks/resets are ready can corrupt hardware setup. Test absent properties, malformed entries, probe deferral, power-cycle reapplication, and readback of expected register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/apple/tunable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/brcmstb/brcmstb.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/brcmstb/brcmstb.h

Purpose: This Broadcom STB header provides helpers for decoding SoC ID registers and optional APIs for retrieving SoC family/product identifiers from the Broadcom STB SoC driver.

Important APIs/types/functions: `BRCM_ID(reg)` extracts the family/product ID using the register format, and `BRCM_REV(reg)` extracts the low 8-bit revision. When `CONFIG_SOC_BRCMSTB` is enabled, `brcmstb_get_family_id` and `brcmstb_get_product_id` are declared; otherwise stub behavior is provided by the remainder of the header.

Control flow: Drivers call the ID helpers or SoC query APIs during probe to gate quirks, compatible behavior, or revision-specific setup.

State and persistence: No state is stored here. The underlying SoC driver owns the cached or hardware-read identifiers.

Dependencies and integration: Includes `linux/kconfig.h` for `IS_ENABLED`. Integrates with Broadcom STB platform drivers, clocks, reset, PM, and peripheral quirks.

Risks and test signals: Mis-decoding IDs can select wrong hardware quirks. Test on old and new register formats, disabled `CONFIG_SOC_BRCMSTB` builds, and drivers that branch on family/product values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/brcmstb/brcmstb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/cirrus/ep93xx.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/cirrus/ep93xx.h

Purpose: This Cirrus Logic EP93xx header shares SoC helper declarations and platform constants for legacy EP93xx ARM systems.

Important APIs/types/functions: It defines `enum ep93xx_soc_model` for 9301/9307/9312 variants, chip revision constants D0 through E2, `struct ep93xx_regmap_adev`, and `to_ep93xx_regmap_adev`. The auxiliary-device wrapper carries a `regmap`, raw base pointer, shared spinlock, and provider-specific `write`/`update_bits` hooks.

Control flow: EP93xx platform code can expose syscon/regmap-backed auxiliary devices; consumers recover the containing `ep93xx_regmap_adev`, then perform locked register writes or masked updates through the provided callbacks.

State and persistence: The auxiliary device stores pointers to the mapped register block and synchronization primitive. Actual state is in EP93xx system registers and persists until reset or later writes.

Dependencies and integration: Includes auxiliary bus, compiler attributes, and container macros. Integrates with EP93xx syscon/regmap providers, clock, reset, pinctrl, and peripheral drivers needing shared register access.

Risks and test signals: Callback locking must be consistent with all users of the same regmap. Test auxiliary-device probe/remove, concurrent `update_bits` users, revision-specific behavior, and boot on each declared SoC model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/cirrus/ep93xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/dove/pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/dove/pmu.h

Purpose: This Marvell Dove header declares power-management unit interfaces for controlling or querying Dove SoC PM state.

Important APIs/types/functions: `struct dove_pmu_domain_initdata` names a power domain and its power, reset, and isolation masks. `struct dove_pmu_initdata` carries PMC/PMU MMIO bases, IRQ data, IRQ-domain start, and a domain table. The exported functions are `dove_init_pmu_legacy` and `dove_init_pmu`.

Control flow: Legacy board code supplies explicit init data to `dove_init_pmu_legacy`; DT/platform paths can call `dove_init_pmu`. The PMU implementation uses the domain masks to sequence power, reset, and isolation.

State and persistence: PMU/PMC registers hold domain power, reset, isolation, and IRQ state. Domain metadata is static init data supplied at boot.

Dependencies and integration: Integrates with Marvell Dove ARM platform support, suspend/resume code, clocks, reset, and power-domain users.

Risks and test signals: Incorrect masks can hold a domain in reset or expose an unpowered bus. Test domain on/off transitions, IRQ-domain numbering, legacy and DT initialization, suspend/resume, and device probe after PMU registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/dove/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/cpu.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/cpu.h

Purpose: This Intel/IXP4xx header defines CPU and SoC identification helpers for legacy IXP4xx network processor platforms.

Important APIs/types/functions: It provides macros and inline helpers that classify IXP4xx variants based on CPU or SoC ID values, along with constants for supported devices and revisions.

Control flow: Platform setup and drivers call the helpers to select register maps, feature availability, and errata workarounds.

State and persistence: No state is owned by the header. It interprets CPU ID state obtained from architecture registers or platform code.

Dependencies and integration: Integrates with ARM IXP4xx platform code, NPE, queue manager, Ethernet, PCI, GPIO, and board-file support.

Risks and test signals: Wrong ID masks can enable unsupported peripherals or skip required errata. Test variant detection on each supported IXP4xx CPU, compile with and without platform options, and boot/probe of dependent NPE/QMGR devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/npe.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/npe.h

Purpose: This header defines the public API for IXP4xx Network Processing Engines, including register layout, handle structure, firmware loading, and message exchange.

Important APIs/types/functions: `struct npe_regs` describes NPE control/status/mailbox registers. `struct npe` carries ID, MMIO regs, and device state. `npe_name` indexes `npe_names`. APIs include `npe_running`, `npe_send_message`, `npe_recv_message`, `npe_send_recv_message`, `npe_load_firmware`, `npe_request`, and `npe_release`.

Control flow: A consumer requests an NPE by ID, loads firmware if needed, checks running state, exchanges mailbox messages, and releases the handle during teardown.

State and persistence: NPE firmware and runtime state live in the hardware engine. The handle tracks the selected NPE and mapped registers while requested.

Dependencies and integration: Integrates with IXP4xx Ethernet/crypto/network acceleration drivers, firmware loading, and platform MMIO code.

Risks and test signals: Firmware/message protocol mismatches can wedge the NPE. Test request/release reference handling, firmware load errors, message timeout paths, and packet processing on each engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/npe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/qmgr.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/qmgr.h

Purpose: This header exposes the IXP4xx queue manager API used by NPE-backed networking and other queue-based hardware blocks.

Important APIs/types/functions: It defines queue counts, queue length, status bits, watermarks, IRQ sources, and `struct qmgr_regs`. APIs include `qmgr_put_entry`, `qmgr_get_entry`, queue status helpers, `qmgr_release_queue`, IRQ setup/enable/disable, and `qmgr_request_queue`/`__qmgr_request_queue` with debug owner metadata.

Control flow: Consumers request a queue with length and watermarks, push and pop 32-bit entries, react to configured queue IRQs, and release the queue at teardown.

State and persistence: Queue contents, read/write pointers, status, overflow/underflow flags, and IRQ enables are hardware state. `qmgr_queue_descs` tracks software descriptions when debugging is enabled.

Dependencies and integration: Integrates with IXP4xx NPE drivers, interrupt handling, and platform MMIO mapping.

Risks and test signals: Queue length/watermark mismatch can overflow, underflow, or lose interrupts. Test queue request collisions, empty/full transitions, IRQ source configuration, and high-rate NPE traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/qmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/marvell/octeontx2/asm.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/marvell/octeontx2/asm.h

Purpose: This Marvell OcteonTX2 header provides architecture-level assembly helper definitions for SoC-specific low-level code.

Important APIs/types/functions: On ARM64 it defines `otx2_lmt_flush(ioaddr)` using `ldeor`, `cn10k_lmt_flush(val, addr)` using `steorl`, and `otx2_atomic64_fetch_add(incr, ptr)` using `ldadda`. Non-ARM64 builds provide compile-safe fallbacks.

Control flow: Packet/CPT enqueue paths perform LMT stores, then call the flush macro to force the hardware-visible operation with the required release/atomic semantics. Atomic add returns the previous 64-bit value.

State and persistence: State is in memory and coprocessor-facing LMTST side effects. The helpers impose ordering but do not store software state.

Dependencies and integration: Depends on ARM64 LSE instruction availability when compiled for ARM64. Integrates with OcteonTX2/CN10K NIX packet send and CPT instruction enqueue paths.

Risks and test signals: Ordering bugs here can drop descriptors or enqueue stale data. Test ARM64 and non-ARM64 builds, NIX/CPT enqueue stress, memory-ordering validation, and toolchain support for the embedded `.cpu generic+lse` assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/marvell/octeontx2/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/marvell/silicons.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/marvell/silicons.h

Purpose: This header names Marvell silicon IDs or families for shared use across Marvell platform and driver code.

Important APIs/types/functions: On ARM64 it defines `CN20K_CHIPID` as `0x20` and inline `is_cn20k(struct pci_dev *pdev)`, which tests the low byte of `pdev->subsystem_device`. Non-ARM64 builds define `is_cn20k(pdev)` as a false expression that consumes the argument.

Control flow: PCI-backed Marvell drivers call `is_cn20k` during probe or quirk selection to choose CN20K-specific behavior.

State and persistence: No state is stored. The helper interprets PCI subsystem device IDs supplied by hardware/firmware.

Dependencies and integration: Includes Linux types and PCI definitions. Integrates with Marvell PCI device drivers that support multiple silicon families.

Risks and test signals: A wrong subsystem-device interpretation can select incompatible queue/register behavior. Test CN20K and non-CN20K PCI devices, ARM64/non-ARM64 builds, and all call sites that gate quirks on `is_cn20k`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/marvell/silicons.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/dvfsrc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/dvfsrc.h

Purpose: This MediaTek header exposes the DVFS Resource Collector client API for bandwidth, OPP, and voltage-level requests.

Important APIs/types/functions: `enum mtk_dvfsrc_cmd` defines request/query command IDs for bandwidth, HRT bandwidth, peak bandwidth, OPP, Vcore level, VSCP level, and max marker. When `CONFIG_MTK_DVFSRC` is enabled, `mtk_dvfsrc_send_request` and `mtk_dvfsrc_query_info` are declared. Disabled builds return `-ENODEV`.

Control flow: Device drivers send a command plus 64-bit data to request resource changes, or query command-specific info into an integer pointer. The DVFSRC provider translates these into hardware PM/resource decisions.

State and persistence: Requests affect DVFSRC-managed performance state and may persist while the consumer remains active. The header stores no client state.

Dependencies and integration: Uses `struct device`, integer types, and `CONFIG_MTK_DVFSRC`. Integrates with MediaTek interconnect, memory bandwidth, power, and multimedia drivers.

Risks and test signals: Unsupported commands, stale device pointers, or missing provider support can degrade performance or power behavior. Test disabled-config stubs, request/query return codes, bandwidth stress, and suspend/resume resource restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/dvfsrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/infracfg.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/infracfg.h

Purpose: This MediaTek header is a shared register map for infrastructure bus protection, SMI clamp, GALS, and reset control bits across many MediaTek SoCs.

Important APIs/types/functions: It defines hundreds of register offsets and bit masks for MT8365, MT8195, MT8192, MT8188, MT8186, MT8183, MT8173, MT8167, MT2701, MT7622, MT6735, and common infrastructure registers. It declares `mtk_infracfg_set_bus_protection` and `mtk_infracfg_clear_bus_protection`, both operating on a `struct regmap`, mask, and `reg_update` flag.

Control flow: Power-domain, clock, and multimedia drivers use the masks to set isolation/protection before powering down a domain and clear them after powering up. Some sequences require ordered multi-step masks and status polling.

State and persistence: Hardware registers hold bus-protection, clamp, reset, and control state. The state persists until explicitly changed or reset and directly affects interconnect reachability.

Dependencies and integration: Uses `BIT`, `GENMASK`, `regmap`, and MediaTek SoC PM domains. It integrates with genpd, display/video/camera/audio/GPU power sequencing, SMI, and infracfg syscon nodes.

Risks and test signals: Incorrect masks or ordering can deadlock AXI/GALS paths, isolate active masters, or hang power transitions. Test every domain transition, timeout paths, concurrent runtime PM, and register readback on each SoC variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/infracfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-cmdq.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-cmdq.h

Purpose: This MediaTek header exposes the Command Queue/GCE packet-building API used by display, multimedia, and power drivers to program hardware command buffers.

Important APIs/types/functions: It defines address helpers, SPR indices, `enum cmdq_logic_op`, `struct cmdq_operand`, `struct cmdq_client_reg`, and `struct cmdq_client`. Enabled builds export mailbox client creation/destruction, packet create/destroy, register writes by subsystem or physical address, masked writes, secure-register read/write helpers, memory move, wait/acquire/clear/set event, polling, logic/assign operations, address polling, absolute/relative jumps, and end-of-command. Disabled builds return `-EINVAL`, `-ENOMEM`, or no-op stubs as appropriate.

Control flow: A driver creates a CMDQ mailbox client, allocates a packet, appends write/poll/event/logic/jump commands, submits through the mailbox implementation, then destroys the packet and client. `cmdq_client_reg` lets consumers abstract MMIO versus physical-address command encoding.

State and persistence: Packets hold command-buffer state; GCE threads hold SPRs, events, and execution state. Hardware register writes persist in target IP blocks.

Dependencies and integration: Includes mailbox client and MediaTek CMDQ mailbox definitions. Integrates with DRM display pipelines, MMSYS, mutex, power domains, and multimedia engines.

Risks and test signals: Command encoding mistakes can write wrong registers or hang a GCE thread. Event waits can deadlock if producers are missing. Test disabled stubs, packet buffer sizing, masked writes, event sequencing, timeout/error paths, and display atomic commits using CMDQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-cmdq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mmsys.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mmsys.h

Purpose: This MediaTek header defines multimedia system routing and configuration APIs for display/video pipelines.

Important APIs/types/functions: It forward-declares `enum mtk_ddp_comp_id`, defines DPI output format enum values, enumerates many DDP component IDs, and declares `mtk_mmsys_ddp_connect`, `mtk_mmsys_ddp_disconnect`, `mtk_mmsys_ddp_dpi_fmt_config`, merge async config, HDR config, mixer input alpha/channel configuration, VPP resize/merge config, and VPP resize DCM config.

Control flow: Display drivers connect DDP components for a pipeline, configure format/mixer/HDR/merge blocks, then disconnect routes during teardown or mode changes.

State and persistence: MMSYS route registers, mixer configuration, HDR parameters, and clock-gating/DCM state persist in the multimedia syscon until changed or reset.

Dependencies and integration: Uses `struct device`, DDP component IDs, and MediaTek DRM/video drivers. Often coordinated with CMDQ and mutex APIs.

Risks and test signals: Wrong routing can produce blank display or conflicting paths. Test every display pipeline route, format conversion, HDR/mixer settings, atomic enable/disable, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mutex.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mutex.h

Purpose: This header defines MediaTek display mutex APIs used to synchronize multimedia pipeline components and start-of-frame sources.

Important APIs/types/functions: It declares opaque `struct mtk_mutex`, enums for mutex module indices and SOF source indices, and functions to get/put a mutex, prepare/unprepare resources, add/remove components, enable/disable, enable via CMDQ, acquire/release, and write module/SOF registers.

Control flow: A display pipeline gets a mutex, prepares it, adds components in route order, selects SOF, enables it for frame synchronization, and disables/removes/unprepares on teardown. CMDQ-enabled paths program the enable operation through command packets.

State and persistence: Mutex hardware stores component masks, SOF source, enable/acquire state, and prepared clock/reset state. The handle tracks ownership.

Dependencies and integration: Integrates with MediaTek DRM, MMSYS, CMDQ, regmap, and componentized display drivers.

Risks and test signals: Component mask or SOF mismatches cause frame-start deadlocks or tearing. Test atomic modesets, CMDQ and non-CMDQ enable paths, acquire timeout behavior, suspend/resume, and component add/remove symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_sip_svc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_sip_svc.h

Purpose: This MediaTek header defines Secure Monitor Call/SIP service IDs used by kernel drivers to request secure firmware services.

Important APIs/types/functions: It provides preprocessor constants for MediaTek SIP service function IDs and related arguments. No local state or implementation is present.

Control flow: Consumers pass these IDs to ARM SMCCC helpers to invoke secure-world services for power, clocks, memory, or SoC-specific controls.

State and persistence: State is maintained by secure firmware and affected hardware registers. Results may persist across normal-world driver lifetimes.

Dependencies and integration: Integrates with MediaTek platform drivers and ARM SMCCC firmware interfaces.

Risks and test signals: Wrong function IDs can fail silently, return firmware errors, or alter secure hardware state unexpectedly. Test firmware return codes, unavailable-firmware handling, and SoC-specific service compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_sip_svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_wed.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_wed.h

Purpose: This header defines the MediaTek Wireless Ethernet Dispatch interface shared between WLAN drivers and the MediaTek Ethernet/WED offload provider.

Important APIs/types/functions: It defines TX/RX queue counts, WED WO command IDs, packed buffer descriptors, bus type enum, `struct mtk_wed_ring`, `struct mtk_wed_wo_rx_stats`, `struct mtk_wed_buf`, `struct mtk_wed_device`, and `struct mtk_wed_ops`. Inline helpers attach a device through the RCU-protected global `mtk_soc_wed_ops`, query RX/AMSDU capabilities, and macro-dispatch ring setup, IRQ, register, PPE, TC, reset, RRO, and stop/start operations. Disabled builds provide no-op or error-returning stubs.

Control flow: WLAN drivers fill `mtk_wed_device.wlan`, call attach, configure rings and buffers, start WED with IRQ masks, send firmware/WO messages, update RX stats, and detach/stop/reset when the WLAN device stops.

State and persistence: `mtk_wed_device` holds runtime ring descriptors, DMA addresses, buffer pools, WDMA/WPDMA register offsets, offload capabilities, token ranges, and callbacks. Hardware rings and firmware state persist while WED is running.

Dependencies and integration: Uses RCU, regmap, PCI, SKBs, netdevice, TC setup types, DMA, and `CONFIG_NET_MEDIATEK_SOC_WED`. Integrates WLAN drivers with MediaTek Ethernet, PPE, WDMA, and firmware offload.

Risks and test signals: Operation pointer lifetime, RCU attach semantics, ring DMA setup, token ranges, and version-gated RX/RRO support are critical. Test disabled configs, attach failure cleanup, traffic offload, IRQ masks, reset recovery, RRO/AMSDU paths, TC offload, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_wed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mmp/cputype.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/mmp/cputype.h

Purpose: This header provides Marvell MMP/PXA-family CPU type detection helpers.

Important APIs/types/functions: It defines ID masks and inline/macros that classify MMP and related Marvell application processors by CPU ID or SoC revision.

Control flow: Platform and peripheral drivers use the helpers during initialization to choose variant-specific register offsets, clocks, or quirks.

State and persistence: The header interprets architecture CPU ID state; it stores no mutable data.

Dependencies and integration: Integrates with ARM platform support for MMP/PXA, board files, clocks, pinctrl, and legacy drivers.

Risks and test signals: Bad masks or disabled config paths can misclassify SoCs. Test compile-time coverage for each enabled CPU family and boot/probe on representative MMP variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/mmp/cputype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/nxp/lpc32xx-misc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/nxp/lpc32xx-misc.h

Purpose: This NXP LPC32xx header declares miscellaneous SoC helper functions and constants shared by LPC32xx platform drivers.

Important APIs/types/functions: With `CONFIG_ARCH_LPC32XX`, it declares `lpc32xx_return_iram(void __iomem **mapbase, dma_addr_t *dmaaddr)`, `lpc32xx_set_phy_interface_mode(phy_interface_t mode)`, and `lpc32xx_loopback_set(resource_size_t mapbase, int state)`. Disabled stubs return zero IRAM size, NULL/zero addresses, and no-op behavior.

Control flow: Consumers request IRAM mapping/DMA address information, set the Ethernet PHY interface mode, or toggle loopback control for a register base.

State and persistence: IRAM mapping information is platform-owned, while PHY mode and loopback state are system-control register state that persists until changed or reset.

Dependencies and integration: Depends on Linux types and PHY interface definitions. Integrates with LPC32xx Ethernet/MAC, IRAM users, and platform miscellaneous control code.

Risks and test signals: Disabled stubs can hide missing architecture support; callers must handle zero IRAM. Test Ethernet PHY mode selection, loopback enable/disable, IRAM consumers, and non-LPC32xx build behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/nxp/lpc32xx-misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/pxa/cpu.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/pxa/cpu.h

Purpose: This PXA header provides CPU identification helpers for PXA210/25x/26x/27x/3xx/93x families and related Marvell variants.

Important APIs/types/functions: It defines variant-specific `__cpu_is_*` macros under config guards, maps them to public `cpu_is_*` helpers, and uses CPU ID/JTAG ID bit masks documented in the file comments. Disabled family configs make helpers compile to false.

Control flow: Platform code and drivers call the helpers to select silicon-specific code paths, errata, clocking, pin mux, and memory-controller behavior.

State and persistence: The helpers read or consume CPU ID values; no mutable state is stored here.

Dependencies and integration: Includes `asm/cputype.h` on ARM and integrates with PXA board/platform support, MFP, SMEMC, clocks, GPIO, and legacy drivers.

Risks and test signals: Conditional helpers can hide code at build time; wrong masks can classify a stepping incorrectly. Test build matrices for PXA25x/PXA27x/PXA3xx, runtime detection on each supported stepping, and users that gate register writes on these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/pxa/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/pxa/mfp.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/pxa/mfp.h

Purpose: This header defines the PXA/MMP Multi-Function Pin configuration encoding and public pin-configuration APIs.

Important APIs/types/functions: It enumerates MFP pin IDs for GPIOs and named peripheral pins, defines `mfp_cfg_t`, bitfield macros for pin, alternate function, drive strength, low-power state, low-power edge detection, and pull state, and provides construction macros `MFP_CFG`, `MFP_CFG_DRV`, `MFP_CFG_LPM`, and `MFP_CFG_X`. For PXA3xx/MMP it defines `struct mfp_addr_map`, address-map macros, and functions `mfp_init_base`, `mfp_init_addr`, `mfp_read`, `mfp_write`, `mfp_config`, `mfp_config_run`, and `mfp_config_lpm`.

Control flow: Platform code maps MFPR registers, initializes pin offset tables, applies arrays of encoded pin configs, and switches between run and low-power configurations around suspend/resume.

State and persistence: MFP register values define pin muxing, drive, pulls, and low-power behavior. The core also maintains pin offset/default tables initialized by platform code.

Dependencies and integration: Integrates with PXA/MMP board files, pin control, GPIO, suspend/resume, and peripheral drivers.

Risks and test signals: Encoded bitfields are dense; wrong pin IDs or low-power states can break boot pins, wake sources, or bus signals. Test pin mux arrays, suspend/resume low-power switching, GPIO mapping through `mfp_to_gpio`, and register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/pxa/mfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/pxa/smemc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/pxa/smemc.h

Purpose: This header defines PXA static memory controller interfaces and register constants.

Important APIs/types/functions: It declares `pxa_smemc_set_pcmcia_timing`, `pxa_smemc_set_pcmcia_socket`, `pxa2xx_smemc_get_sdram_rows`, `pxa3xx_smemc_get_memclkdiv`, and `pxa_smemc_get_mdrefr`. It also conditionally declares `pxa25x_get_clk_frequency_khz` and `pxa27x_get_clk_frequency_khz`, with zero-return stubs when the respective family is disabled.

Control flow: PCMCIA/board code programs socket and timing values; memory and clock code query SDRAM rows, memory clock divisor, MDREFR MMIO, or legacy core frequency values.

State and persistence: SMEMC and MDREFR registers hold bus timing, PCMCIA socket, refresh, and memory clock state until reset or reprogramming.

Dependencies and integration: Integrates with PXA platform initialization, flash/PCMCIA/external memory drivers, and low-level suspend/resume code.

Risks and test signals: Incorrect timings can corrupt external memory transactions. Test early boot memory access, flash reads/writes, suspend/resume restore, and variant-specific timing values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/pxa/smemc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/apr.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/apr.h

Purpose: This Qualcomm header defines APR/GPR packet formats, bus/driver registration helpers, and send/port APIs for Qualcomm audio/service packet routing.

Important APIs/types/functions: It exports `aprbus`, APR/GPR header field macros, message type constants, basic response opcodes, packed `struct apr_hdr`, `apr_pkt`, `apr_resp_pkt`, `gpr_hdr`, `gpr_pkt`, `gpr_resp_pkt`, response structs, service-version helpers, `gpr_port_cb`, `struct pkt_router_svc`, `struct apr_device`, `struct apr_driver`, module registration macros, `apr_send_pkt`, `gpr_alloc_port`, `gpr_free_port`, `gpr_send_port_pkt`, and `gpr_send_pkt`.

Control flow: APR/GPR drivers register on `aprbus`, bind to service IDs/domains, receive callback packets, allocate optional GPR ports, send packets with packed headers, and unregister through module helpers.

State and persistence: Device/service state lives in `apr_device`, router services, spinlocks, callback/private pointers, and remote subsystem routing. Packet headers carry token/opcode state for request/response correlation.

Dependencies and integration: Uses driver core, spinlocks, module device tables, and Qualcomm APR/GPR DT bindings. Integrates with audio DSP, remoteproc/rpmsg-like transports, and service routing.

Risks and test signals: Header packing, size fields, domain/port IDs, and callback locking are critical. Test packet round trips, basic response parsing, driver probe/remove, GPR port allocation, remote SSR, and malformed packet sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/apr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/geni-se.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/geni-se.h

Purpose: This Qualcomm header is the shared API/register definition for GENI/QUP Serial Engines used by SPI, I2C, I3C, UART, and related serial drivers.

Important APIs/types/functions: It defines transfer modes, protocol types, ICC paths, `struct geni_se`, common register offsets, IRQ/status/control bit masks, FIFO and DMA fields, hardware-version helpers, bandwidth constants, inline helpers for protocol reads, command setup/cancel/abort, FIFO depth/width reads, and exported functions for SE init, mode selection, packing, resources on/off, clock table/frequency matching, DMA prep/unprep, interconnect get/set/enable/disable/tag, and firmware loading.

Control flow: A serial driver initializes `struct geni_se`, turns resources on, configures FIFO/DMA/GPI mode, sets packing and clocks, issues master/secondary commands, handles IRQ or DMA completion, then disables resources.

State and persistence: State spans SE MMIO registers, clock/interconnect votes, DMA mappings, firmware protocol selection, command active bits, FIFOs, and IRQ masks.

Dependencies and integration: Uses MMIO accessors, clocks, DMA mapping, interconnect framework, and `CONFIG_QCOM_GENI_SE`. Integrates with Qualcomm QUP wrapper and serial peripheral drivers.

Risks and test signals: Hardware-version-specific FIFO depth, command abort/cancel races, ICC votes, and DMA cleanup are high risk. Test FIFO and DMA transfers, protocol detection, resource power cycling, suspend/resume, error IRQs, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/geni-se.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/irq.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/irq.h

Purpose: This header defines Qualcomm IRQ-domain flags and helpers for wake-capable interrupt controllers such as PDC and MPM.

Important APIs/types/functions: It defines `GPIO_NO_WAKE_IRQ`, `IRQ_DOMAIN_FLAG_QCOM_PDC_WAKEUP`, `IRQ_DOMAIN_FLAG_QCOM_MPM_WAKEUP`, and inline `irq_domain_qcom_handle_wakeup` to detect domains that need Qualcomm wake handling.

Control flow: GPIO/irqchip code checks the domain flags when mapping or configuring IRQ wake behavior, especially when a GPIO IRQ has a separate wake interrupt path.

State and persistence: Wake capability is stored in IRQ domain flags and irqchip state. Hardware wake configuration persists through suspend until cleared.

Dependencies and integration: Depends on IRQ domain structures and integrates with Qualcomm PDC, MPM, GPIO, pinctrl, and suspend wakeup paths.

Risks and test signals: Incorrect flags can make wake IRQs unavailable or duplicated. Test suspend/resume wake from GPIOs, domains without wake flags, and GPIOs with `GPIO_NO_WAKE_IRQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/llcc-qcom.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/llcc-qcom.h

Purpose: This Qualcomm header defines Last Level Cache Controller slice IDs, descriptors, EDAC register data, driver data, and the client API for activating/deactivating LLCC slices.

Important APIs/types/functions: It enumerates many `LLCC_*` use-case IDs, defines `struct llcc_slice_desc`, EDAC register data/offset structures, `struct llcc_drv_data`, and APIs `llcc_slice_getd`, `llcc_slice_putd`, `llcc_get_slice_id`, `llcc_get_slice_size`, `llcc_slice_activate`, and `llcc_slice_deactivate`, with disabled stubs.

Control flow: Consumers acquire a slice descriptor by use-case ID, read ID/size, activate it before use, deactivate it when no longer needed, and release the descriptor.

State and persistence: LLCC hardware tracks slice activation, capacity allocation, and EDAC registers. Descriptor references and driver data track software ownership.

Dependencies and integration: Integrates with Qualcomm SoC drivers, GPU/display/camera/video/modem consumers, EDAC, regmap, and platform data.

Risks and test signals: Wrong use-case ID or activation balancing can waste cache or break performance isolation. Test disabled configs, repeated get/put, activate/deactivate nesting, EDAC register access, and workload performance on LLCC users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/llcc-qcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/mdt_loader.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/mdt_loader.h

Purpose: This header exposes Qualcomm MDT firmware loading helpers for remote processors and PAS/SCM-authenticated images.

Important APIs/types/functions: It defines MDT segment flags `QCOM_MDT_TYPE_MASK`, `QCOM_MDT_TYPE_HASH`, and `QCOM_MDT_RELOCATABLE`. APIs include `qcom_mdt_get_size`, `qcom_mdt_load`, `qcom_mdt_pas_load`, `qcom_mdt_load_no_init`, and `qcom_mdt_read_metadata`; disabled builds return `-ENODEV` or `ERR_PTR(-ENODEV)`.

Control flow: Remoteproc or subsystem drivers request firmware, calculate required memory, load segments into a memory region, optionally authenticate through PAS context, get relocation base, and read metadata for secure monitor calls.

State and persistence: Firmware contents are copied to reserved memory; relocation base and PAS context tie the image to remote-subsystem boot state.

Dependencies and integration: Uses firmware API, devices, physical addresses, and Qualcomm SCM PAS context. Integrates with remoteproc, modem/audio/GPU/DSP firmware loaders, and reserved memory.

Risks and test signals: Segment bounds, relocatable address handling, and metadata parsing are security-sensitive. Test malformed firmware, undersized memory regions, PAS load failure, no-init loading, and remoteproc boot/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/mdt_loader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/pdr.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/pdr.h

Purpose: This header defines Qualcomm Protection Domain Restart service lookup and restart helpers.

Important APIs/types/functions: It defines service name/PFR lengths, opaque `struct pdr_service` and `struct pdr_handle`, `enum servreg_service_state`, and APIs `pdr_handle_alloc`, `pdr_add_lookup`, `pdr_restart_pd`, and `pdr_handle_release`.

Control flow: A client allocates a PDR handle with a status callback, adds service lookups by name/path, receives service up/down/early-down/uninit state changes, can request PD restart, and releases the handle.

State and persistence: The PDR subsystem owns lookup registrations, service objects, callback private data, and remote service state. Remote protection domains persist independently across restarts.

Dependencies and integration: Includes Qualcomm QMI support and integrates with service registry, remoteproc/subsystem restart, audio/modem/WLAN clients, and GLINK/QMI transports.

Risks and test signals: Service path/name mismatch prevents notifications; restart calls can disrupt shared domains. Test service up/down callbacks, SSR events, lookup cleanup, restart failure, and long service names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/pdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/pmic_glink.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/pmic_glink.h

Purpose: This header defines the Qualcomm PMIC GLINK client API for battery manager, USB-C, and related PMIC message owners.

Important APIs/types/functions: It defines owner IDs for BATTMGR, USBC, and USBC_PAN, message types request/response and notify, `struct pmic_glink_hdr`, `pmic_glink_send`, `devm_pmic_glink_client_alloc`, and `pmic_glink_client_register`.

Control flow: A client allocates a managed PMIC GLINK client with owner ID, receive callback, PDR callback, and private pointer, registers it, and sends messages containing the common header plus payload.

State and persistence: Client registration and callback/private data live in the PMIC GLINK core. Remote PMIC service state may change during PDR/SSR.

Dependencies and integration: Uses device-managed allocation, GLINK transport, and Qualcomm PMIC subsystems. Integrates with USB-C, battery, charger, and power-supply drivers.

Risks and test signals: Owner/opcode mismatches or endian mistakes break remote protocol. Test client registration before service availability, send/response, notifications, PDR callback delivery, and teardown during remote restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/pmic_glink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom-pbs.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom-pbs.h

Purpose: This header exposes Qualcomm PMIC PBS trigger support for clients that need to execute PMIC programmable boot sequencer scripts.

Important APIs/types/functions: It declares PBS client data types and helper functions for acquiring a PBS client and triggering a sequence, with device-managed integration in the implementation.

Control flow: A driver obtains the PBS client associated with its device or phandle and calls the trigger helper when a PMIC-side sequence is required.

State and persistence: PBS state resides in PMIC hardware/firmware. Triggered sequences may alter regulators, resets, or PMIC registers until explicitly changed.

Dependencies and integration: Integrates with Qualcomm PMIC, regmap/SPMI, power/reset, and peripheral drivers needing PMIC scripts.

Risks and test signals: Wrong PBS trigger can affect board power state. Test probe deferral, absent PBS provider, trigger return codes, and hardware side effects on target boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom-pbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom_aoss.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom_aoss.h

Purpose: This header defines the Qualcomm Always-On Subsystem QMP interface used for low-power mode and always-on resource messages.

Important APIs/types/functions: It declares opaque `struct qmp` and helpers to get/put a QMP channel and send AOSS/QMP messages, with disabled stubs in non-enabled builds.

Control flow: Consumers obtain a QMP handle from a device or phandle, send command strings/messages to AOSS, and release the handle when done.

State and persistence: The QMP core owns mailbox/transport state. AOSS keeps resource votes or low-power configuration until updated.

Dependencies and integration: Integrates with Qualcomm mailbox/QMP, power domains, regulators, remoteproc, and system suspend code.

Risks and test signals: Message strings are firmware contracts; typos can silently fail or leave stale votes. Test missing provider, timeout/error returns, suspend/resume messaging, and multiple consumers sharing QMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom_aoss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/qmi.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/qmi.h

Purpose: This header defines the in-kernel Qualcomm QMI helper framework for encoding/decoding TLV messages, service lookup, handles, transactions, and callbacks.

Important APIs/types/functions: It defines QMI element descriptors, array/string/struct encodings, transaction state, service info, handle operations, and APIs for handle init/release, adding/removing lookup, sending requests/responses/indications, transaction init/wait/cancel, encoding, decoding, and message handler dispatch.

Control flow: A QMI service/client initializes a handle with ops, registers lookups or server state, creates transactions for requests, sends encoded messages, waits for responses, and dispatches incoming messages to handlers based on type and message ID.

State and persistence: `qmi_handle` and transactions maintain socket/transport bindings, pending responses, service lookup state, locks/lists, and private callbacks. Remote services persist across subsystem restarts.

Dependencies and integration: Integrates with Qualcomm QRTR sockets, workqueues, mutexes/completions, service registry, PDR, remoteproc clients, and subsystem-specific protocols.

Risks and test signals: TLV descriptor mismatches can corrupt decode, leak memory, or reject valid messages. Transaction timeout/cancel paths are race-prone. Test encode/decode vectors, lookup add/remove, concurrent transactions, SSR, malformed messages, and handler coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/qmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/smd-rpm.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/smd-rpm.h

Purpose: This header defines Qualcomm SMD RPM request structures and APIs for communicating resource votes to the Resource Power Manager.

Important APIs/types/functions: It declares RPM resource/request IDs, `struct qcom_smd_rpm`, `struct qcom_smd_rpm_req`, and request/write helpers used to send key/value resource state to RPM over SMD.

Control flow: A client builds one or more RPM requests for a resource, submits them to the RPM handle, and waits for acknowledgement or error from the transport.

State and persistence: RPM keeps active/sleep resource votes for clocks, regulators, bus, and power resources. Client-side request data is transient.

Dependencies and integration: Integrates with Qualcomm SMD, regulators, clocks, interconnect/bus scaling, and legacy RPM power-management code.

Risks and test signals: Resource IDs and state sets are firmware contracts; bad IDs can affect unrelated resources. Test vote apply/remove, sleep/active sets, transport failure, and suspend/resume resource retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/smd-rpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem.h

Purpose: This header exposes Qualcomm Shared Memory APIs for allocating and retrieving SMEM items shared with remote processors.

Important APIs/types/functions: It defines `QCOM_SMEM_HOST_ANY` and declares `qcom_smem_is_available`, `qcom_smem_alloc`, `qcom_smem_get`, `qcom_smem_get_free_space`, `qcom_smem_get_soc_id`, `qcom_smem_get_feature_code`, and `qcom_smem_bust_hwspin_lock_by_host`.

Control flow: Consumers check availability, allocate or retrieve host/item entries, read sizes, query SoC/feature IDs, and optionally recover a stuck hardware spinlock for a remote host.

State and persistence: SMEM allocations live in shared memory and may persist across subsystem restarts. Hardware spinlocks protect shared metadata.

Dependencies and integration: Integrates with Qualcomm SMEM core, hwspinlock, socinfo, remoteproc, modem/adsp/wcnss clients, and boot firmware.

Risks and test signals: Wrong host/item IDs can corrupt shared protocol data. Spinlock busting is dangerous and should be exceptional. Test availability before probe, allocation races, size validation, socinfo queries, and remote restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem_state.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem_state.h

Purpose: This header defines Qualcomm SMEM state bit providers/consumers used for low-latency shared state flags between processors.

Important APIs/types/functions: `struct qcom_smem_state_ops` contains an `update_bits` operation. Consumer APIs include `qcom_smem_state_get`, `devm_qcom_smem_state_get`, `qcom_smem_state_put`, and `qcom_smem_state_update_bits`. Provider APIs include `qcom_smem_state_register` and `qcom_smem_state_unregister`. Disabled stubs return errors or no-op.

Control flow: Providers register a state object for a DT node. Consumers get a state plus assigned bit, update masked bits, and release the handle.

State and persistence: State bits are stored in provider-managed shared memory or registers and may be visible to remote processors through SMEM.

Dependencies and integration: Uses device tree nodes, devices, and Qualcomm SMEM state providers. Integrates with remoteproc handshakes, modem/WLAN/audio state, and power-management signaling.

Risks and test signals: Bit allocation mismatches can signal the wrong state to firmware. Test DT bit parsing, managed get cleanup, concurrent update_bits, provider unregister with consumers, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/smem_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/socinfo.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/socinfo.h

Purpose: This header defines the Qualcomm SMEM socinfo layout and feature-code/product-code helpers.

Important APIs/types/functions: It defines SMEM item and string lengths, `SOCINFO_MAJOR`, `SOCINFO_MINOR`, `SOCINFO_VERSION`, packed `struct socinfo` fields for format/version/build IDs/chip IDs/serial/platform/PMIC/feature data, `enum qcom_socinfo_feature_code`, and product-code helpers such as `SOCINFO_PCn`.

Control flow: The socinfo driver reads the SMEM socinfo item, interprets fields by format version, publishes SoC identity, and exposes feature/product codes to other drivers.

State and persistence: Data is bootloader/firmware-populated SMEM state, usually persistent for the boot lifetime.

Dependencies and integration: Integrates with `qcom_smem_get`, Linux soc bus registration, debugfs/sysfs style identity reporting, and Qualcomm driver quirk selection.

Risks and test signals: Format-version changes require careful bounds checks; reading fields not present in older formats can misreport identity. Test old/new socinfo formats, feature-code decode, build/chip ID strings, and SMEM absence handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/socinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/ubwc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/ubwc.h

Purpose: This header defines Qualcomm Universal Bandwidth Compression configuration data and helpers for multimedia clients.

Important APIs/types/functions: `struct qcom_ubwc_cfg_data` stores UBWC mode flags, version, swizzle, macrotile, bank spread, and minimum access length data. Constants define swizzle enable levels and UBWC versions 1.0 through 6.0. Inline helpers return global config data and test individual fields such as UBWC mode, 64-byte min access length, macrotile mode, bank spread, and swizzle.

Control flow: Display, GPU, camera, or video drivers obtain config data and use helpers to select register programming for compressed buffers.

State and persistence: Config data is static SoC capability information. Hardware register programming in consumers persists until changed.

Dependencies and integration: Integrates with Qualcomm DRM, camera, video codecs, GPU/display memory format negotiation, and SoC data tables.

Risks and test signals: Wrong UBWC version or swizzle causes memory layout corruption. Test compressed framebuffer/video formats, SoC-specific config retrieval, fallback when no data is present, and cross-IP consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/ubwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/wcnss_ctrl.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/qcom/wcnss_ctrl.h

Purpose: This header exposes a Qualcomm WCNSS control helper for opening named rpmsg channels.

Important APIs/types/functions: It declares `qcom_wcnss_open_channel(void *wcnss, const char *name, rpmsg_rx_cb_t cb, void *priv)` returning an `rpmsg_endpoint`.

Control flow: A WCNSS consumer requests a channel by name, provides an RX callback and private pointer, then uses the returned endpoint for rpmsg communication.

State and persistence: Channel and endpoint state are managed by the WCNSS/rpmsg core. Remote WLAN firmware owns channel availability across subsystem restarts.

Dependencies and integration: Integrates with rpmsg, Qualcomm WCNSS remoteproc/control drivers, WLAN/Bluetooth/FM clients, and subsystem restart handling.

Risks and test signals: Channel-name mismatch or SSR during open can fail endpoint creation. Test channel open/close, RX callback dispatch, remote restart, and missing firmware channel behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/qcom/wcnss_ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/renesas/r9a06g032-sysctrl.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/renesas/r9a06g032-sysctrl.h

Purpose: This Renesas header exposes a system-controller helper for configuring the R9A06G032 DMA mux.

Important APIs/types/functions: It declares `r9a06g032_sysctrl_set_dmamux(u32 mask, u32 val)` when `CONFIG_CLK_R9A06G032` is enabled; otherwise the inline stub returns `-ENODEV`.

Control flow: DMA or peripheral setup code calls the helper with a mask/value pair to update DMAMUX selection in the sysctrl block.

State and persistence: The DMAMUX selection is hardware register state and persists until reprogrammed or reset.

Dependencies and integration: Integrates with Renesas R9A06G032 clock/sysctrl and DMA/peripheral drivers.

Risks and test signals: Incorrect mask/value routes DMA requests incorrectly. Test disabled configs, DMA channel operation for each muxed peripheral, and sysctrl readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/renesas/r9a06g032-sysctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-rst.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-rst.h

Purpose: This Renesas R-Car header exposes reset-controller helpers for reading mode pins and setting remote-processor boot addresses.

Important APIs/types/functions: With `CONFIG_RST_RCAR`, it declares `rcar_rst_read_mode_pins(u32 *mode)` and `rcar_rst_set_rproc_boot_addr(u64 boot_addr)`. Disabled stubs return `-ENODEV`.

Control flow: Platform or remoteproc code reads boot mode pins for configuration decisions and writes a remote processor boot address before releasing reset.

State and persistence: Mode-pin state reflects latched hardware boot configuration. Remoteproc boot address is reset-controller state used during processor start.

Dependencies and integration: Integrates with Renesas R-Car reset driver, boot configuration, and remoteproc support.

Risks and test signals: Boot-address mistakes can start firmware at the wrong location. Test mode read errors, disabled build stubs, remoteproc boot, and reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-rst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-sysc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-sysc.h

Purpose: This Renesas R-Car header declares CPU power control helpers in the system controller.

Important APIs/types/functions: It declares `rcar_sysc_power_down_cpu(unsigned int cpu)` and `rcar_sysc_power_up_cpu(unsigned int cpu)`.

Control flow: CPU hotplug or suspend code calls these helpers to transition individual CPUs through the R-Car SYSC power controller.

State and persistence: CPU power state is maintained in SYSC registers and affects core availability until powered up again.

Dependencies and integration: Integrates with Renesas R-Car SMP, CPU hotplug, suspend/resume, and power-domain code.

Risks and test signals: Incorrect CPU index or power sequencing can hang SMP bring-up or hotplug. Test CPU offline/online cycles, system suspend, and failure paths for invalid CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-chipid.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-chipid.h

Purpose: This Samsung Exynos header defines CHIPID register offsets and bitfields, especially for Exynos5422 binning, speed group, and auxiliary info.

Important APIs/types/functions: It defines PRO_ID, PKG_ID, LOT_ID, AUX_INFO offsets, revision masks/shifts, Exynos ID mask, and Exynos5422 fields for IDS, speed group, table, SG_A/SG_B, sign, bin2, TMCB, and ARM/KFC up/down values.

Control flow: The Exynos chipid driver reads these registers, decodes SoC identity and ASV/binning data, then publishes it to SoC/OPP/thermal or debug code.

State and persistence: CHIPID registers are read-only or fuse-derived SoC identity state that persists for the device lifetime.

Dependencies and integration: Integrates with Samsung Exynos socinfo, ASV/OPP, thermal, and platform detection code.

Risks and test signals: Incorrect field extraction can choose wrong voltage/frequency bins. Test register decode against known silicon, revision masking, and OPP/ASV consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-chipid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-pmu.h

Purpose: This header exposes Exynos PMU helpers for system powerdown configuration and PMU regmap access.

Important APIs/types/functions: It defines `enum sys_powerdown` values `SYS_AFTR`, `SYS_LPA`, `SYS_SLEEP`, and `NUM_SYS_POWERDOWN`, declares `exynos_sys_powerdown_conf`, and conditionally declares `exynos_get_pmu_regmap` and `exynos_get_pmu_regmap_by_phandle`. Disabled stubs return `ERR_PTR(-ENODEV)`.

Control flow: Power-management code configures the selected system powerdown mode before suspend. Drivers needing PMU registers obtain the global or phandle-selected PMU regmap.

State and persistence: PMU registers hold low-power mode, wake, retention, and PHY control state. Regmap handles are provider-owned.

Dependencies and integration: Uses regmap and device tree nodes. Integrates with Exynos suspend/resume, PHY, clock, reset, and power-domain drivers.

Risks and test signals: Wrong mode configuration can prevent suspend or resume. Test disabled PMU configs, regmap lookup by phandle, AFTR/LPA/SLEEP transitions, wakeup sources, and PHY control users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-regs-pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-regs-pmu.h

Purpose: This large Samsung header is a shared register-offset catalog for Exynos and Tensor GS101 PMU blocks used by power, reset, retention, PHY, wakeup, and low-power code.

Important APIs/types/functions: It defines central sequence, wake mask/stat, MIPI/USB/DP PHY control, inform/spare registers, CPU/core/L2/common power registers, low-power clock/reset/retention registers, pad retention options, PS_HOLD, local power bits, Exynos3/4/5/5420/5433/7870/990/2200/autov920-specific offsets, and extensive GS101 ALIVE/cluster/subblock/system/interrupt/PHY/PMLINK/HCU register offsets and helper macros.

Control flow: Exynos PM, clock, reset, PHY, and SoC drivers include this header to program PMU registers during boot, suspend entry/exit, CPU hotplug, PHY power, wake-mask setup, and shutdown/reboot.

State and persistence: PMU registers directly control retention, power gating, wake status, boot inform values, reset cause, and PHY enables. Some fields survive low-power modes and are used during resume.

Dependencies and integration: Uses `BIT` style masks and integrates with Exynos PMU regmap users, Samsung clock/reset/PHY drivers, CPU hotplug, and Tensor GS101 platform code.

Risks and test signals: Offset mistakes can write unrelated PMU registers, causing failed suspend, broken wake, or power loss. Test suspend/resume, CPU hotplug, wake masks, PHY enable/disable, reset reason, and SoC-specific register subsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-regs-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/s3c-pm.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/samsung/s3c-pm.h

Purpose: This Samsung S3C header exposes legacy suspend debugging/check helpers and UART save/restore hooks.

Important APIs/types/functions: It defines `S3C_PMDBG`, inline no-op UART save/restore helpers, and optional sleep-debug functions `s3c_pm_check_prepare`, `s3c_pm_check_restore`, `s3c_pm_check_cleanup`, and `s3c_pm_check_store` when sleep debug is enabled; otherwise macros no-op.

Control flow: Legacy S3C PM code prepares checksum/debug state before suspend, restores/checks it after resume, and optionally saves/restores UART state.

State and persistence: Debug check state is maintained by the PM implementation. Hardware UART and memory checksum state are relevant across suspend.

Dependencies and integration: Integrates with Samsung S3C24xx/S3C legacy PM, UART, and debug infrastructure.

Risks and test signals: Debug code must not perturb suspend state. Test with and without sleep debug, UART console after resume, and memory/register checksum reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/samsung/s3c-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/sunxi/sunxi_sram.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/sunxi/sunxi_sram.h

Purpose: This Allwinner Sunxi header exposes SRAM claim/release helpers for devices sharing on-chip SRAM blocks.

Important APIs/types/functions: It declares `sunxi_sram_claim(struct device *dev)` and `sunxi_sram_release(struct device *dev)`.

Control flow: A device claims the SRAM region associated with it before use and releases it when finished, allowing the SRAM controller to manage ownership or routing.

State and persistence: SRAM ownership/mux state is provider-owned and may persist until release. SRAM contents persist while powered and not overwritten.

Dependencies and integration: Uses `struct device` and integrates with Sunxi SRAM controller, EMAC, crypto, display, and other SRAM-using drivers.

Risks and test signals: Missing release can block other devices; missing claim can cause ownership conflicts. Test probe deferral, double claim/release, concurrent users, and suspend/resume SRAM routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/sunxi/sunxi_sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/k3-ringacc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/k3-ringacc.h

Purpose: This TI K3 header defines the Ring Accelerator API for queue/ring allocation, configuration, push/pop operations, and DMA-ring initialization.

Important APIs/types/functions: It defines `enum k3_ring_mode`, `enum k3_ring_size`, opaque `struct k3_ringacc`/`k3_ring`, `struct k3_ring_cfg`, request flags, ring request/free/reset/config APIs, ring ID/IRQ/size/free/occupancy/full queries, push/pop at head/tail, TISCI device ID query, `struct k3_ringacc_init_data`, and `k3_ringacc_dmarings_init`.

Control flow: A client obtains a ringacc by phandle, requests one or a pair of rings, configures mode/element size/memory, pushes or pops elements, resets as needed, and frees rings at teardown.

State and persistence: Ring hardware tracks occupancy, indices, element memory, proxy use, IRQ routing, and TISCI resource ownership.

Dependencies and integration: Uses device tree, platform devices, TI SCI, DMA devices, and K3 UDMA/ethernet/storage drivers.

Risks and test signals: Ring mode, element size, proxy flag, and shared ownership must match hardware users. Test request collisions, push/pop wraparound, DMA reset occupancy, IRQ retrieval, shared rings, and TISCI resource setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/k3-ringacc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_dma.h

Purpose: This TI Keystone Navigator header defines packet DMA descriptor formats, channel configuration, and optional API wrappers for Navigator DMA.

Important APIs/types/functions: It defines descriptor bit masks for packet length, tags, EPIB/PS info, return queues, buffer length, and error flags; constants for EPIB/PS/software words; enums for TX priority, RX error mode, RX thresholds, and descriptor type; `struct knav_dma_tx_cfg`, `knav_dma_rx_cfg`, `knav_dma_cfg`, and cacheline-aligned `struct knav_dma_desc`. Enabled builds declare `knav_dma_open_channel`, `close_channel`, `get_flow`, and `device_ready`; disabled builds return NULL, `-EINVAL`, or false.

Control flow: Clients configure TX or RX flow parameters, open a named DMA channel, use descriptors and queues for packet movement, query flow IDs, and close the channel.

State and persistence: Channel allocation, descriptor pools, queue IDs, RX flow config, and hardware DMA state are provider-owned. Descriptors carry packet and software-private state.

Dependencies and integration: Includes DMAengine and integrates with Keystone QMSS, networking, and packet accelerator drivers.

Risks and test signals: Descriptor endian/bitfield mistakes cause packet loss or DMA faults. Test disabled config, channel open/close, RX starvation modes, descriptor map/unmap, flow IDs, and high-throughput traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_qmss.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_qmss.h

Purpose: This TI Keystone Navigator header exposes Queue Manager Subsystem queue and descriptor-pool APIs.

Important APIs/types/functions: It defines special queue IDs (`QPEND`, `ACC`, `GP`), shared flag, queue control commands, notification callback/config types, queue open/close/control/push APIs, pool create/destroy/count/descriptor get-put/map-unmap/DMA-to-virt APIs, and `knav_qmss_device_ready`.

Control flow: Clients open queues by name or ID, optionally configure notifications, push DMA descriptors, create descriptor pools, map descriptors for DMA, recycle descriptors, and close queues/pools.

State and persistence: QMSS owns queue state, notifications, descriptor pool occupancy, DMA mappings, and hardware accumulator/QPEND behavior.

Dependencies and integration: Integrates with Keystone Navigator DMA, packet networking, DMA mapping, and interrupt notification paths.

Risks and test signals: Queue/pool leaks, wrong descriptor size, and notification races can stall packet flow. Test queue open collisions, shared queue behavior, pool exhaustion, descriptor map/unmap, notifications, and `device_ready` gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_qmss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-io.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-io.h

Purpose: This OMAP1 header provides legacy physical-address register access helpers and register base/offset constants for clock, mux, ULPD, DSP, PWL, and control blocks.

Important APIs/types/functions: On ARM it declares `omap_readb/readw/readl` and `omap_writeb/writew/writel`; non-ARM stubs return zero/no-op. It defines constants for module config, ULPD registers, clock generator, DPLL, DSP config, pulse-width light, function mux, pull-down, and pull-up/down select registers.

Control flow: Legacy OMAP1 platform and drivers use these helpers to read/write physical SoC registers directly during early init, clock setup, muxing, and suspend/resume.

State and persistence: Register writes configure clocks, muxing, power, and DSP control until changed or reset.

Dependencies and integration: Integrates with OMAP1 ARM platform code, mux, clock, USB, and board support.

Risks and test signals: Direct physical register access is fragile and bypasses modern abstractions. Test ARM/non-ARM compile paths, early boot, clock setup, mux programming, and suspend/resume register retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-mux.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-mux.h

Purpose: This OMAP1 header enumerates legacy mux configuration IDs and exposes the `omap_cfg_reg` pin-mux programming helper.

Important APIs/types/functions: It defines large enums for OMAP7xx and OMAP1xxx mux indices covering UART, USB, MMC, I2C, SPI, keypad, camera, memory, and GPIO functions. It declares `omap_cfg_reg(unsigned long reg_cfg)` when OMAP1 mux support is enabled, otherwise an inline stub returns zero.

Control flow: Board files call `omap_cfg_reg` for each desired mux config during initialization or peripheral setup.

State and persistence: Mux register state controls pin function and persists until changed or reset.

Dependencies and integration: Integrates with OMAP1 board files, GPIO, serial, USB, MMC, and other legacy peripheral drivers.

Risks and test signals: Wrong mux enum can disconnect board pins or conflict with boot-critical signals. Test board-specific mux tables, peripheral probe, GPIO direction/IRQ behavior, and disabled mux builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-soc.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-soc.h

Purpose: This OMAP1 header defines CPU class, subclass, and type detection helpers for OMAP7xx, OMAP15xx, OMAP16xx, and specific models.

Important APIs/types/functions: It uses `omap_rev()` bit extraction macros and generated inline helpers such as `is_omap15xx`, `is_omap16xx`, model-specific `is_omap310`, `is_omap1510`, `is_omap1610`, `is_omap5912`, and public `cpu_is_omap*` macros. Disabled configs compile unsupported helpers to zero while `cpu_class_is_omap1()` is true for this platform family.

Control flow: Platform and drivers branch on these helpers during initialization to choose clocks, muxes, errata, USB, memory, and peripheral behavior.

State and persistence: The helpers interpret SoC revision state exposed by platform code; no mutable state is stored.

Dependencies and integration: Integrates with OMAP1 platform support, board files, mux, USB, clocks, and legacy drivers.

Risks and test signals: Variant misclassification can program wrong register layouts. Test `omap_rev()` values, compile variants, and boot/probe on each supported OMAP1 subclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-usb.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-usb.h

Purpose: This OMAP1 header centralizes USB OTG, UDC, and transceiver register constants shared by legacy platform, gadget, PHY, and OHCI drivers.

Important APIs/types/functions: It defines OMAP1/OMAP2 OTG and UDC base addresses, OTG register offsets, and bitfield macros for transceiver mode, idle, reset, SRP/HNP, VBUS/session status, pad enable, host/device enable, pullup/pulldown, and USB line controls.

Control flow: USB platform code and drivers use these constants to reset/configure OTG, select transceiver modes, manage host/device roles, and read session/VBUS state.

State and persistence: OTG/UDC hardware registers hold role, pad, VBUS, and transceiver control state until changed or reset.

Dependencies and integration: Integrates with OMAP1 USB gadget, OHCI host, PHY/transceiver, and board support code.

Risks and test signals: Shared constants make cross-driver coordination fragile; bad role bits can disable host/device operation. Test host and gadget modes, OTG reset, VBUS/session detection, suspend/resume, and board-specific transceiver wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti-msgmgr.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/ti-msgmgr.h

Purpose: This TI header defines mailbox message manager packet metadata used by TI K3 system firmware communication.

Important APIs/types/functions: It forward-declares `struct mbox_chan` and defines `struct ti_msgmgr_message` with payload length, payload buffer pointer, expected RX channel, and polling timeout in milliseconds.

Control flow: Client drivers fill `ti_msgmgr_message`, pass it to `mbox_send_message`, and optionally use `chan_rx` plus `timeout_rx_ms` when polling for a response.

State and persistence: The struct is transient per mailbox transfer. Hardware mailbox queues and firmware state persist outside the header.

Dependencies and integration: Integrates with the Linux mailbox framework, TI message manager controller, TI SCI firmware, and platform resource-management clients.

Risks and test signals: `len` must match SoC-specific slot sizes, and `chan_rx` must match the expected response path. Test mailbox send/receive, polled timeouts, concurrent clients, and firmware error replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti-msgmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_inta_msi.h -->
# sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_inta_msi.h

Purpose: This TI header exposes helpers for configuring MSI through TI SCI-managed Interrupt Aggregator resources.

Important APIs/types/functions: It declares `ti_sci_inta_msi_create_irq_domain(struct fwnode_handle *fwnode, struct msi_domain_info *info, struct irq_domain *parent)` and `ti_sci_inta_msi_domain_alloc_irqs(struct device *dev, struct ti_sci_resource *res)`.

Control flow: IRQ setup creates an MSI domain backed by a parent IRQ domain, then device probe code allocates IRQs using a TI SCI resource range.

State and persistence: MSI event routing and interrupt aggregator resources are managed through TI SCI firmware and hardware aggregator state.

Dependencies and integration: Integrates with TI SCI protocol, IRQ domains, MSI infrastructure, K3 interrupt aggregator, and platform devices.

Risks and test signals: Resource allocation or event mapping errors can lose interrupts. Test MSI allocation/free, IRQ delivery, firmware denial paths, and teardown on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_inta_msi.h -->
