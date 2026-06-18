# Group Research: group_605_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__a269bce6ee8c

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_defs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_defs.h

## Purpose
Defines shared Neptune/NXGE hardware constants: block base addresses, DMA CSR offsets, ring sizing defaults, DMA channel limits, port/MAC/VLAN/TCAM/FCRAM limits, interrupt logical-device numbering, validation macros, and common register bitfield helper macros.

## Main Interfaces
- Block address constants for `PIO`, `FZC_PIO`, `FZC_MAC`, `FZC_IPP`, `FFLP`, `FZC_FFLP`, `PIO_VADDR`, `DMC`, `FZC_DMC`, `TXC`, `FZC_TXC`, interrupt-mask blocks, PROM, and PIM.
- DMC/TX register offsets such as `TX_RNG_CFIG`, `TX_RING_HDH`, `TX_RING_KICK`, `TX_CS`, `RDC_TBL`, logical page registers, RED registers, and DRR weight registers.
- Ring defaults for RBR/RCR/TDC and transmit gather pointers.
- Hardware limits: `NXGE_MAX_RDCS`, `NXGE_MAX_TDCS`, `NXGE_MAX_PORTS`, `NXGE_MAX_VRS`, `NXGE_MAX_RDC_GROUPS`, `NXGE_MAX_VLANS`, TCAM and hash sizes.
- Classification constants for TCAM formats, flow-key fields, and FCRAM match types.
- Address/bit helpers: `NXGE_BASE()`, `NXGE_VAL()`, `TDMC_PIOVADDR_OFFSET()`, `RDMC_PIOVADDR_OFFSET()`, `DMC_OFFSET()`, `TDMC_OFFSET()`.
- Validation macros for ports, TXDMA pages/functions/channels, VR pages, logical devices, timers, and SID vectors.

## Dependencies And Relationships
This is a foundational include used by nearly every NXGE per-block hardware header. It supplies base offsets consumed by `nxge_hw.h`, `nxge_mac_hw.h`, `nxge_ipp_hw.h`, `nxge_fflp_hw.h`, `nxge_espc_hw.h`, and driver implementation code.

## Research Notes
This header mixes active definitions with legacy/conditional blocks under `OLD` and `ORIGINAL`. It also contains a legacy-looking typo in the `LDGIMGN` macro reference, using `PIO_LDGIMGN` where the block base defined earlier is `PIO_LDGIM`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc.h

## Purpose
Defines the EEPROM/SPROM content layout used by NXGE to discover factory MAC addresses, port counts, module strings, board model strings, PHY type, firmware/image size, interrupt counts, version, and checksum.

## Main Interfaces
- ESPC NCR register aliases such as `ESPC_MAC_ADDR_0`, `ESPC_NUM_PORTS_MACS`, module string registers, board model string registers, `ESPC_PHY_TYPE`, `ESPC_MAX_FM_SZ`, `ESPC_INTR_NUM`, `ESPC_VER_IMGSZ`, and `ESPC_CHKSUM`.
- Masks and shifts for packed SPROM fields, including port count, MAC address count, string lengths, firmware image size, version, and checksum.
- String access macros `ESPC_MOD_STR(n)` and `ESPC_BD_MOD_STR(n)`.
- PHY encoding constants `ESC_PHY_10G_FIBER`, `ESC_PHY_10G_COPPER`, `ESC_PHY_1G_FIBER`, `ESC_PHY_1G_COPPER`, and `ESC_PHY_NONE`.
- Bitfield unions:
  - `mac_addr_0_t`
  - `mac_addr_1_t`
  - `phy_type_t`
  - `intr_num_t`

## Dependencies And Relationships
Includes `nxge_espc_hw.h` for register address construction. The parsed values are consumed by ESPC/SPROM routines declared in `nxge_impl.h`, especially MAC address and PHY discovery during attach.

## Research Notes
The unions expose both 64-bit raw values and endian-aware byte/field access. This file is a hardware-data layout contract, not an algorithmic component.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc_hw.h

## Purpose
Defines low-level ESPC/EPC register offsets and bit masks for accessing the PROM/NCR region through NXGE PIO.

## Main Interfaces
- PIO enable/status registers:
  - `ESPC_PIO_EN_REG`
  - `ESPC_PIO_EN_MASK`
  - `ESPC_PIO_STATUS_REG`
- EPC status/control bits for read/write initiate and complete, EEPROM address and data fields, and wait timing.
- NCR addressing helpers:
  - `ESPC_NCR_REG`
  - `ESPC_REG_ADDR(reg)`
  - `ESPC_NCR_REGN(n)`
  - `ESPC_NCR_VAL_MASK`

## Dependencies And Relationships
Includes `nxge_defs.h` for the `FZC_PROM` block base. Higher-level SPROM field names are layered in `nxge_espc.h`.

## Research Notes
This is the hardware access companion to `nxge_espc.h`; it only defines offsets and masks needed to address the PROM/NCR data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp.h

## Purpose
Defines software state, statistics, and configuration constants for the Fast Frame Lookup Processor: VLAN/RDC mapping, TCAM flow entries, FCRAM hash-cell occupancy, programmable classification keys, and FFLP error accounting.

## Main Interfaces
- Error/stat structures:
  - `fflp_errlog_t`
  - `nxge_fflp_stats_t`
- FCRAM occupancy constants for empty, IPv4 exact, IPv6 exact, optimistic, and mixed cell layouts.
- `fcram_cell_t`: tracks cell type, occupied subareas, and shadow location.
- `fcram_parition_t`: describes a hash partition with id/base/mask/relocation/flags/offset/size.
- `tcam_flow_spec_t`: TCAM entry plus flags, user metadata, and validity.
- Classification config flags such as `NXGE_CLASS_TCAM_LOOKUP`, `NXGE_CLASS_FLOW_USE_IPSRC`, `NXGE_CLASS_FLOW_USE_IPDST`, `NXGE_CLASS_FLOW_USE_SRC_PORT`, `NXGE_CLASS_FLOW_USE_DST_PORT`, and `NXGE_CLASS_DISCARD`.
- `vlan_rdcgrp_map_t`: VLAN-to-RDC-group mapping.
- `nxge_classify_t`: central software classification state containing locks, TCAM entries, programmable class state, flow keys, FCRAM hash table, per-partition state, and fragment-bug tracking.

## Dependencies And Relationships
Includes `npi_fflp.h` and uses `tcam_entry_t` from the FFLP hardware definitions. The state is initialized and manipulated by the classify/FFLP routines prototyped in `nxge_impl.h`.

## Research Notes
The file documents FCRAM cell packing rules in detail. There is a likely legacy typo: `FCRAM_SUBAREA7_OCCUPIED` is defined as `0x20`, duplicating subarea 5 instead of using a distinct bit.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hash.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hash.h

## Purpose
Declares CRC/hash helper functions used by FFLP flow hashing.

## Main Interfaces
- CRC initialization and computation:
  - `nxge_crc32c_init()`
  - `nxge_crc32c()`
  - `nxge_crc_ccitt_init()`
  - `nxge_crc_ccitt()`
- H1 hash computation variants:
  - `nxge_compute_h1_table1()`
  - `nxge_compute_h1_table4()`
  - `nxge_compute_h1_serial()`
  - `nxge_init_h1_table()`
- Macro aliases:
  - `nxge_compute_h2()` maps to CCITT CRC.
  - `nxge_compute_h1()` maps to the table4 implementation.

## Dependencies And Relationships
This header is consumed by FFLP classification/hash implementation code that computes H1/H2 values for FCRAM lookup entries.

## Research Notes
Despite the filename, the include guard is `_SYS_NXGE_NXGE_CRC_H`, reflecting its CRC-helper role.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hw.h

## Purpose
Defines the hardware ABI for the NXGE Fast Frame Lookup Processor, including VLAN table registers, programmable L2/L3 class registers, TCAM key/mask/control/result formats, FCRAM/hash registers, flow-key registers, error logs, and in-memory entry layouts for TCAM and FCRAM operations.

## Main Interfaces
- VLAN table hardware:
  - `FFLP_ENET_VLAN_TBL_REG`
  - `fflp_enet_vlan_tbl_t`
- TCAM programmable class registers and structures:
  - `tcam_class_prg_ether_t`
  - `tcam_class_prg_ip_t`
  - `tcam_class_t`
  - L3 programmable class masks/shifts for RF-NIU/Neptune-L.
- TCAM key/control/result:
  - `FFLP_TCAM_KEY_*`
  - `FFLP_TCAM_MASK_*`
  - `FFLP_TCAM_CTL_REG`
  - `tcam_class_key_ip_t`
  - `tcam_ctl_t`
  - `tcam_res_t`
  - `tcam_ipv4_t`, `tcam_ipv6_t`, `tcam_ether_t`, `tcam_reg_t`, `tcam_entry_t`
- Error hardware:
  - `vlan_par_err_t`
  - `tcam_err_t`
  - `hash_lookup_err_log1_t`
  - `hash_lookup_err_log2_t`
  - `fflp_err_mask_t`
  - `hash_tbl_data_log_t`
- FFLP global config and FCRAM timing:
  - `fflp_cfg_1_t`
  - `fcram_ref_tmr_t`
  - `fcram_phy_rd_lat_t`
- Flow hash configuration:
  - `flow_class_key_ip_t`
  - `hash_h1poly_t`
  - `hash_h2poly_t`
  - `flow_prt_sel_t`
  - `flow_template_t`
  - `flow_key_cfg_t`
  - `tcam_key_cfg_t`
- FCRAM entry formats:
  - `hash_optim_t`
  - `hash_hdr_t`
  - `hash_ports_t`
  - `hash_match_action_t`
  - `hash_ipv4_t`
  - `hash_ipv6_t`
  - `fcram_entry_t`
  - `fcram_entry_format_t`
- PIO helper macros for reading/writing TCAM and hash registers.

## Dependencies And Relationships
Includes `nxge_defs.h` and later `netinet/in.h` for address structures in flow templates and hash entries. It supplies the hardware types used by `nxge_fflp.h`, FFLP NPI code, and classification routines declared in `nxge_impl.h`.

## Research Notes
This header is layout-sensitive and heavily endian-conditional. It contains some duplicate and typo-preserving symbols, such as repeated `FCRAM_LOOKUP_HIGH_PRI`, repeated `TCAM_LOOKUP_HIGH_PRI`, duplicated `HASH_ENTRY_TYPE_OPTIM_IP4`, and `FCRAM_ENTRY_UNKOWN`; consumers may depend on those exact names.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_flow.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_flow.h

## Purpose
Defines user/kernel flow-specification structures and ioctl payloads for receive classification and hash configuration.

## Main Interfaces
- Flow match structures for TCP/UDP IPv4/IPv6, AH/ESP IPv4/IPv6, raw IP, Ethernet programmable frames, generic IP user classes, and IPv6 fragments.
- `flow_spec_t`: packed entry/mask union keyed by `flow_type`.
- Flow type constants from `FSPEC_TCPIP4` through `FSPEC_HDATA`.
- Conversion macros for IPv4/IPv6 addresses, ports, TCAM class, and protocol fields.
- `flow_resource_t`: packed flow object tying a channel cookie, flow cookie, location, and `flow_spec_t`.
- Receive classification ioctl commands:
  - `NXGE_RX_CLASS_GCHAN`
  - `NXGE_RX_CLASS_GRULE_CNT`
  - `NXGE_RX_CLASS_GRULE`
  - `NXGE_RX_CLASS_GRULE_ALL`
  - `NXGE_RX_CLASS_RULE_DEL`
  - `NXGE_RX_CLASS_RULE_INS`
- `rx_class_cfg_t`: packed ioctl payload with rule count, rule locations, and flow resource.
- RX hash/tunnel config commands:
  - `NXGE_IPTUN_CFG_*`
  - `NXGE_CLS_CFG_*`
- `iptun_cfg_t` and `cfg_cmd_t`: packed tunnel/hash configuration payloads.

## Dependencies And Relationships
Includes `netinet/in.h` and aliases `S6_addr32` for IPv6 address word access. FFLP/classification ioctl handling is declared in `nxge_impl.h` as `nxge_rxclass_ioctl()` and `nxge_rxhash_ioctl()`.

## Research Notes
The packed structs are ABI-facing ioctl payloads; field order and size are part of the interface. `rawip4_spec_t` uses `struct in6_addr` fields for source/destination despite its IPv4 name, so consumers should follow the existing layout rather than inferring from the type name.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_flow.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fm.h

## Purpose
Defines NXGE Fault Management Architecture ereport names, block identifiers, ereport IDs, and attribute metadata used to report hardware and software faults.

## Main Interfaces
- Ereport attribute name strings for detailed error type, port/channel numbers, TCAM/VLAN/hash logs, RDMC/TDMC logs, IPP/ZCP state, FIFO entries, TXC ECC/reorder state, and related diagnostic fields.
- Ereport ID packing macros:
  - `EREPORT_FM_ID_SHIFT`
  - `EREPORT_FM_ID_MASK`
  - `EREPORT_INDEX_MASK`
- FM block IDs mapped from hardware block IDs, including MAC, MIF, IPP, TXC, TXDMA, RXDMA, ZCP, ESPC, FFLP, PCIE, VIR, XAUI, and XFP.
- `nxge_fm_ereport_id_t`
- `nxge_fm_ereport_attr_t`: index, display string, ereport class, and `ddi_fault_impact_t`.
- Ereport enums for PCS/MIF/FFLP/IPP/RDMC/ZCP/RXMAC/TDMC/TXC/TXMAC/ESPC/software/XAUI/XFP failures.

## Dependencies And Relationships
Includes `sys/ddi.h` for DDI fault impact types. `nxge_impl.h` declares `nxge_fm_report_error()` and external FMA handle-check helpers that consume these identifiers.

## Research Notes
This header is a taxonomy for fault reporting. The enum values are block-ID shifted, so consumers can recover the reporting hardware block from an ereport ID.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fzc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fzc.h

## Purpose
Declares initialization and configuration routines for function-zero controlled NXGE resources: interrupts, logical pages, TX/RX DMA partitioning, RDC tables, RED, DRR, and system error masks.

## Main Interfaces
- Interrupt setup:
  - `nxge_fzc_intr_init()`
  - `nxge_fzc_intr_ldg_num_set()`
  - `nxge_fzc_intr_tmres_set()`
  - `nxge_fzc_intr_sid_set()`
- RX/TX logical page programming:
  - `nxge_fzc_dmc_rx_log_page_vld()`
  - `nxge_fzc_dmc_rx_log_page_mask()`
  - `nxge_init_fzc_rxdma_channel_pages()`
  - `nxge_init_fzc_txdma_channel_pages()`
- TX/RX DMA initialization:
  - `nxge_init_fzc_tdc()`
  - `nxge_init_fzc_rdc()`
  - `nxge_init_fzc_txdma_channel()`
  - `nxge_init_fzc_rxdma_channel()`
  - port/common initialization variants.
- RDC table binding:
  - `nxge_init_fzc_rdc_tbl()`
  - `nxge_fzc_rdc_tbl_bind()`
  - `nxge_fzc_rdc_tbl_unbind()`
- RED/clearlog/DRR helpers and logical device group setup.
- Optional sun4v NIU logical-page workaround entry points under `NIU_LP_WORKAROUND`.

## Dependencies And Relationships
Includes `npi_vir.h`. The prototypes are repeated or consumed from `nxge_impl.h`, and operate on `p_nxge_t`, DMA ring types, and RDC group types defined in other NXGE headers.

## Research Notes
This is a declaration-only coordination header. It separates FZC-owned hardware programming from per-block RX/TX/MAC logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fzc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hio.h

## Purpose
Defines Hybrid I/O support for NXGE in sun4v logical-domain environments: service/guest detection, hypervisor function tables, virtual regions, DMA channel mappings, virtual interrupt state, MAC share callbacks, and HIO lifecycle prototypes.

## Main Interfaces
- Environment macros:
  - `isLDOMservice()`
  - `isLDOMguest()`
  - `isLDOMs()`
- Hypervisor function pointer types for VR assignment/unassignment/info and RX/TX DMA channel assignment/logical-page configuration.
- `nxhv_vr_fp_t`, `nxhv_dc_fp_t`, `nxhv_fp_t`: resolved HV API tables.
- HIO identity and layout:
  - `nxge_hio_type_t`
  - `vr_base_address_t`
  - `vr_region_t`
  - `vp_channel_t`
  - `vpc_type_t`
  - `VP_VC_OFFSET()`
- Virtualized DMA CSR offset enums for RDC and TDC pages.
- Virtual interrupt definitions:
  - `pio_ld_op_t`
  - `hio_ldg_t`
- Core state structures:
  - `nx_rdc_tbl_t`
  - `nxge_hio_vr_t`
  - `nxge_hio_dc_t`
  - `nxge_hio_data_t`
- Prototypes for HIO init/uninit, DMA channel group management, MAC share allocation/bind/query/free, guest register mapping, VR add/release, logical-page config, interrupt add/remove, LDSV access, HV init, and hostinfo setup.

## Dependencies And Relationships
Includes `nxge_mac.h`, `nxge_ipp.h`, `nxge_fflp.h`, and `sys/mac_provider.h`. It bridges NXGE driver state with Crossbow MAC groups/rings and sun4v NIU hypervisor APIs.

## Research Notes
The file explicitly distinguishes service-domain physical channel numbers from guest-domain virtual page/channel numbers. That distinction is central to correctly interpreting `nxge_hio_dc_t.page` versus `nxge_hio_dc_t.channel`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hw.h

## Purpose
Aggregates per-block NXGE hardware headers and defines global device register layouts for function control, partitioning, DMA binding, logical interrupt devices/groups, reset, system error status/masks, SMX/debug/GPIO/PIM, and logical page translation.

## Main Interfaces
- Includes per-block hardware ABIs:
  - FFLP, IPP, MAC, RXDMA, TXC, TXDMA, ZCP, ESPC, N2 ESR, SRAM, and PHY hardware headers.
- Core types:
  - `dc_map_t`
  - `lg_map_t`
  - `nxge_mode_t`
- Function/partition control:
  - `DEV_FUNC_SR_REG`
  - `dev_func_sr_t`
  - `MULTI_PART_CTL_REG`
  - `multi_part_ctl_t`
  - `VADDR_REG`
  - `DMA_BIND_REG`
  - `dma_bind_t`
- Logical interrupt support:
  - LD/LDG constants and register offsets.
  - `ldg_num_t`
  - `ldsv_t`
  - `ldsv2_t`
  - `ld_im_t`
  - `ldgimgm_t`
  - `ldgitmres_t`
  - `sid_t`
- Reset and error handling:
  - `rst_ctl_t`
  - `sys_err_mask_t`
  - `sys_err_stat_t`
- Meta arbiter and SMX/debug:
  - `dty_tid_ctl_t`
  - `dty_tid_stat_t`
  - `smx_cfg_dat_t`
  - `smx_int_stat_t`
  - `smx_ctl_t`
  - `smx_dbg_vec_t`
  - PIO debug/training/arbiter unions.
- GPIO and PIM register formats.
- Logical page partitioning structures:
  - `log_page_vld_t`
  - `log_page_mask_t`
  - `log_page_value_t`
  - `log_page_relo_t`
  - `log_page_hdl_t`

## Dependencies And Relationships
This header requires host endianness and bit ordering macros to be defined. It is included by `nxge_impl.h` and provides the global hardware register definitions used by FZC, interrupt, partitioning, and error-handling code.

## Research Notes
Most register formats are 64-bit unions with endian-specific 32-bit low-word layouts. `nxge_defs.h` also defines some overlapping interrupt constants; this header is the fuller hardware-register view.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_impl.h

## Purpose
Defines the internal NXGE driver implementation interface: OS includes, hypervisor API versions, DMA/common macros, driver status and platform enums, DMA allocation state, logical interrupt software state, PCI/register mappings, alternate MAC bookkeeping, cross-module includes, and implementation prototypes.

## Main Interfaces
- NIU HV API version constants and sun4v HV API numbers.
- DMA and NPI access macros:
  - `DMA_COMMON_*`
  - `NPI_*_HANDLE_SET/GET`
  - descriptor and DMA cookie helpers.
- Core types/enums:
  - `nxge_status_t`
  - `dev_func_shared_t`
  - `dma_method_t`
  - `nxge_rx_block_size_t`
  - `dma_size_t`
  - `dma_type_t`
  - `rx_page_state_t`
  - `niu_type_t`
  - `niu_hw_type_t`
  - `platform_type_t`
  - `cfg_type_t`
  - output/debug message enums.
- DMA state:
  - `nxge_dma_common_t`
  - `nxge_dma_pool_t`
- Logical interrupt state:
  - `nxge_ldg_t`
  - `nxge_ldv_t`
  - interrupt handler typedefs.
- PCI/register mapping:
  - `pci_cfg_t`
  - `dev_regs_t`
- MAC address management:
  - `nxge_mac_addr_t`
  - `nxge_mmac_t`
  - `nxge_mmac_stats_t`
- Main prototype groups for classify/FFLP, kstats, hardware reset/ioctl/interrupts, TX send, RXDMA config, ndd parameters, virtual/FZC, MAC/PHY/MII/MDIO, ESPC/SPROM, debug, buffer free, and sun4v weak HV symbols.

## Dependencies And Relationships
Includes Solaris networking, streams, DDI/FMA, MAC provider, hypervisor, and many NXGE internal headers. It is the central internal include used by NXGE implementation `.c` files rather than a narrow hardware layout header.

## Research Notes
The file encodes many board/product identities, including Neptune, Huron, Maramba, Alonso, Rock, N2/NIU, RF/NIU, and specific board model strings. It also contains weak sun4v hypervisor declarations so the same driver can bind where HV services may or may not be present.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp.h

## Purpose
Defines IPP software state, statistics, error log structures, limits, and lifecycle/error-handling prototypes for the IP Packet Processing block.

## Main Interfaces
- Limits:
  - `IPP_MAX_PKT_SIZE`
  - `IPP_MAX_ERR_SHOW`
- `ipp_errlog_t`: multiple-error flag, DFIFO read pointer, state machine, and ECC syndrome.
- `nxge_ipp_stats_t`: counters for init/error events, missed SOP/EOP, DFIFO ECC, PFIFO parity/over/underflow, checksum errors, packet discard, and saved errlog.
- `nxge_ipp_t`: configuration, interrupt config, status register snapshot, max packet size, and stats pointer.
- Prototypes:
  - `nxge_ipp_reset()`
  - `nxge_ipp_init()`
  - `nxge_ipp_disable()`
  - `nxge_ipp_drain()`
  - `nxge_ipp_handle_sys_errors()`
  - `nxge_ipp_fatal_err_recover()`
  - `nxge_ipp_eccue_valid_check()`
  - `nxge_ipp_inject_err()`

## Dependencies And Relationships
Includes `nxge_ipp_hw.h` and `npi_ipp.h`. IPP state is embedded in higher-level driver state and initialized through routines declared in `nxge_impl.h`.

## Research Notes
This header is the software-facing wrapper around the IPP hardware register definitions. Error handling is a first-class part of the interface.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp_hw.h

## Purpose
Defines IPP hardware registers, address calculations, configuration bits, interrupt status/mask bits, ECC control layout, FIFO pointer masks, counter masks, and reset timing.

## Main Interfaces
- Register offsets for IPP config, discard/checksum/ECC counters, interrupt status/mask, PFIFO/DFIFO read/write data, FIFO pointers, state machine, checksum status, FFLP checksum info, debug select, ECC syndrome, EOP-miss pointer, and ECC control.
- Port address helpers:
  - `IPP_REG_ADDR(port_num, reg)`
  - `IPP_PORT_ADDR(port_num)`
- Configuration bits:
  - `IPP_SOFT_RESET`
  - `IPP_IP_MAX_PKT_BYTES_*`
  - PIO write enables
  - checksum/drop/ECC/enable bits.
- Interrupt status bits for missed SOP/EOP, DFIFO ECC classes, ECC entry index, PFIFO parity/index, PFIFO over/underflow, checksum counter max, and discard counter max.
- `ipp_status_t`: endian-aware interrupt status union.
- `ipp_ecc_ctrl_t`: endian-aware ECC injection/correction control union.
- Interrupt-mask disable bits, DFIFO entry counts, pointer masks, and counter masks.

## Dependencies And Relationships
Includes `nxge_defs.h` for `FZC_IPP`. Higher-level IPP software state and prototypes are in `nxge_ipp.h`.

## Research Notes
The port-address macros encode the non-linear IPP port layout for ports 0 through 3. The bitfield unions require one of `_BIT_FIELDS_HTOL` or `_BIT_FIELDS_LTOH`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac.h

## Purpose
Defines software MAC-layer state and statistics for NXGE XMAC/BMAC ports, including MTU limits, interrupt masks, link state, transceiver capabilities, counters, multicast hash filters, address tables, and host-info state.

## Main Interfaces
- MTU/frame constants:
  - `NXGE_MTU_DEFAULT_MAX`
  - `NXGE_DEFAULT_MTU`
  - `NXGE_MIN_MAC_FRAMESIZE`
  - `NXGE_MAXIMUM_MTU`
- MAC interrupt-mask composites for XMAC and BMAC TX/RX.
- `nxge_link_state_t`
- Common stats:
  - `nxge_mac_stats_t`
- Per-MAC counters:
  - `nxge_xmac_stats_t`
  - `nxge_bmac_stats_t`
- `hash_filter_t`: multicast hash refcounts and per-bit refcounts.
- `nxge_mac_t`: port identity/mode, link check mode, jumbo flag, config registers, frame sizing, pause/control state, MAC/alternate/filter addresses, hash table, host-info entries, stats pointers, and default MTU.

## Dependencies And Relationships
Includes `nxge_mac_hw.h` and `npi_mac.h`. The state is initialized and manipulated by MAC/PHY routines declared in `nxge_impl.h`.

## Research Notes
The header abstracts over XMAC and BMAC while keeping separate counter structures because the two hardware blocks expose different counter widths and semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac_hw.h

## Purpose
Defines the MAC/PHY hardware ABI for NXGE: port type encoding, XMAC/BMAC/PCS/XPCS/ESR/MIF address calculations, register offsets, configuration/status masks, endian-aware register unions, counter masks, host-info entries, and SerDes/link diagnostic constants.

## Main Interfaces
- General port/PHY encoding:
  - `NXGE_PORT_SPD_*`
  - `NXGE_PHY_*`
  - `NXGE_PORT_1G_COPPER`
  - `NXGE_PORT_10G_FIBRE`
  - `NXGE_PORT_TN1010`
  - `nxge_network_mode_t`
  - `nxge_port_t`
  - `nxge_port_mode_t`
  - `nxge_linkchk_mode_t`
  - link interrupt/monitor enums
  - `xcvr_inuse_t`
- Address helpers:
  - `XMAC_REG_ADDR()`, `XMAC_PORT_ADDR()`
  - `BMAC_REG_ADDR()`, `BMAC_PORT_ADDR()`
  - `PCS_REG_ADDR()`, `PCS_PORT_ADDR()`
  - `XPCS_ADDR()`, `XPCS_PORT_ADDR()`
  - `ESR_ADDR()`
  - `MIF_ADDR()`
- BMAC register offsets and unions:
  - `btxmac_config_t`
  - `brxmac_config_t`
  - `bxif_config_t`
- XMAC register offsets and union:
  - `xmac_cfg_t`
- Register families for alternate addresses, hash tables, host-info tables, frame counters, byte counters, state machines, internal diagnostics, preamble data, and debug/training vectors.
- MIF definitions:
  - Clause 22/45 frame fields.
  - `mif_frame_t`
  - `mif_cfg_t`
  - `mif_poll_stat_t`
  - `mif_poll_mask_t`
  - `mif_stat_t`
- PCS definitions:
  - MII control/status/advertisement masks.
  - `pcs_ctrl_t`
  - `pcs_stat_t`
  - `pcs_anar_t`
  - `pcs_cfg_t`
  - `pcs_stat_mc_t`
- XPCS definitions:
  - Control/status/speed/package/test/config/mask/counter masks.
  - `xpcs_ctrl1_t`
  - `xpcs_stat1_t`
  - `xpcs_speed_ab_t`
  - `xpcs_dev_in_pkg_t`
  - `xpcs_ctrl2_t`
  - `xpcs_stat2_t`
  - `xpcs_stat_t`
  - `xpcs_test_ctl_t`
  - `xpcs_diag_t`
  - `xpcs_config_t`
- ESR/SerDes constants for reset, PLL, control, test config, RGMII config, signal observation, and loopback.
- Generic bit helpers:
  - `NXGE_BASE()`
  - `NXGE_VAL_GET()`
  - `NXGE_VAL_SET()`

## Dependencies And Relationships
Includes `nxge_defs.h` for base block addresses and shared helper constants. `nxge_mac.h` builds software stats/state on these register definitions, and MAC/PHY implementation code uses the address helpers and bit masks for link setup, reset, counters, filtering, and diagnostics.

## Research Notes
This is the largest MAC ABI header in the group and is highly sensitive to endian and bitfield ordering. It preserves support for both 10G XMAC and 1G BMAC paths, plus internal PCS/XPCS and external MII/MDIO access through MIF.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac_hw.h -->