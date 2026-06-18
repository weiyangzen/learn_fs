# sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc.h lines 10840-13703

## Scope

This chunk covers the tail of the Mellanox/NVIDIA mlx5 firmware interface header. It is generated ABI description rather than executable code: the structs are bit-accurate command, register, event, capability, and general-object layouts consumed through the `MLX5_GET()`, `MLX5_SET()`, command mailbox, register access, and general object command helpers.

The range starts in the `mtutc` time adjustment register tail, defines port/management/QoS capability access masks, event and command queue records, initial PCI interface and health segment layout, many port and management register documents, flow table root and LAG commands, UMEM/UCTX/MEMIC and software steering object inputs, security offload objects, VHCA migration and page-tracking objects, SyncE/PTP/PCIe congestion objects, and ends with PSP key rotation/SPI generation command formats and the header guard close.

## Purpose

The chunk provides firmware-facing data contracts for mlx5 subsystems that are spread across networking, RDMA, VFIO migration, vDPA, fwctl, devlink, clock/PTP, and hardware steering:

- Capability access masks: `pcam`, `mcam`, `qcam`, and `sbcam` expose which port, management, QoS, and shared-buffer registers/features firmware supports.
- Register documents: port state/counters/buffers/module access, management component update, reset, temperature, real-time clock, PPS, PTP, SyncE, QoS, shared-buffer, and debugging/troubleshooting layouts.
- Command transport primitives: EQE/event payload wrapping, PCIe command queue entry, mailbox block, command input/output headers, and memory translation table entries.
- Firmware boot and health: initial segment fields for firmware revision, command queue address/stride/doorbell, NIC interface mode, health buffer, clear interrupt bit, syndrome, and health counter.
- Resource lifecycles: create/query/modify/destroy style inputs and outputs for flow tables, LAG/vport LAG, MEMIC, UMEM, UCTX, software ICM, Geneve TLV options, subfunctions, general objects, security offload objects, and page tracking.
- Acceleration/security objects: IPsec, MACsec, encryption key, internal KEK, flow meter ASO, sampler, TLS static/progress parameters, PSP key rotation, and PSP SPI/key generation.
- Migration and virtualization: suspend/resume VHCA, query/save/load VHCA state, advanced virtualization caps, page-track object configuration, and dirty-page report entry layout.

## Important APIs, Types, and Data

The capability structs are compact feature-bit maps. `mlx5_ifc_pcam_reg_bits` selects a port feature/access group and returns masks for registers such as `ppcnt`, `pptb`, `pbmc`, `pplm`, and `pphcr`, plus feature bits for FEC rates, buffer ownership, discard/statistical counter groups, connector type, and per-lane/buffer counters. `mlx5_ifc_mcam_reg_bits` similarly exposes management access registers such as `mtmp`, `mfrl`, `mrtc`, tracer registers, `mtutc`, `mpegc`, `mpir`, `mcqs`, `mcqi`, `mcc`, `mcda`, SyncE, `mtptm`, `mtctr`, and `mrtcq`. `mlx5_ifc_qcam_reg_bits` covers QoS registers including QCAP/QPTS/QDPM/QPDPM and trust-state features. `mlx5_ifc_sbcam_reg_bits` adds shared-buffer capability masks and sizing limits.

The command/event ABI includes `mlx5_ifc_eqe_bits`, `mlx5_ifc_cmd_queue_entry_bits`, `mlx5_ifc_cmd_in_bits`, `mlx5_ifc_cmd_out_bits`, `mlx5_ifc_cmd_if_box_bits`, and `mlx5_ifc_mtt_bits`. These define ownership/signature bits, inline command data, mailbox pointer fragments, token/status fields, linked mailbox blocks, and MTT read/write permissions. `mlx5_ifc_initial_seg_bits` is the large MMIO initial segment used during device initialization and health handling.

Port and management registers include PAOS port administrative/operational state, PCAP port capability masks, PCMR CRC/FCS/entropy behavior, PBMC/shared buffer programming, PDDR troubleshooting pages, PPHCR histograms, MTMPS/MTPPSE PPS pin control/events, MCQS/MCQI/MCC/MCDA component update state and data, MFRL firmware reset negotiation, MRTC/MTPTM/MTCTR real-time/PTM timestamp capture, MTMP/MTcap temperature sensors, MCIA module I2C access, ETS/QPTS/QPDPM/PPTB QoS, and SyncE MSECQ/MSEES/MRTCQ layouts.

The register document unions `mlx5_ifc_ports_control_registers_document_bits`, `mlx5_ifc_debug_enhancements_document_bits`, and `mlx5_ifc_uplink_pci_interface_document_bits` provide typed overlays for generic register-access code. The port document union aggregates many layouts defined earlier in the file and in this chunk, with a large reserved fallback so a register payload can be treated as one typed document.

Flow and LAG command structs include `set_flow_table_root`, `modify_flow_table`, `mlx5_ifc_lagc_bits`, `create/modify/query/destroy_lag`, and create/destroy vport LAG command shapes. The `MLX5_MODIFY_FLOW_TABLE_MISS_TABLE_ID` and `MLX5_MODIFY_FLOW_TABLE_LAG_NEXT_TABLE_ID` flags control which flow table context fields are updated. LAG context fields encode FDB selection, port select mode, active port, LAG state, and TX remap affinities.

Memory and user context objects include `modify_memic`, `alloc_memic`, `dealloc_memic`, `mlx5_ifc_umem_bits`, `create/destroy_umem`, `mlx5_ifc_uctx_bits`, `create/destroy_uctx`, `mlx5_ifc_sw_icm_bits`, and `mlx5_ifc_geneve_tlv_option_bits`. These are used by DevX, vDPA, fwctl, software steering, and firmware-managed memory/object allocation paths. UMEM embeds variable-length MTT entries.

General object types and object commands define object IDs for encryption key, IPsec, sampler, flow meter ASO, MACsec, internal KEK, RDMA control, PCIe congestion event, and flow table alias. The chunk provides object body layouts for IPsec ASO and SA state, MACsec ASO and secure channel/association state, encryption keys and wrapped DEKs, internal KEKs, flow meters, samplers, PCIE congestion event thresholds, and command wrappers using `mlx5_ifc_general_obj_in_cmd_hdr_bits` and `mlx5_ifc_general_obj_out_cmd_hdr_bits` from earlier chunks.

Migration and virtualization command types include VHCA suspend/resume, query/save/load migration state, advanced RDMA and virtualization capabilities, page-track report entries, page-track object state/ranges, subfunction partition query, and alloc/dealloc SF commands. These layouts are directly relevant to VFIO live migration and scalable function provisioning.

## Control Flow

This header does not run control flow, but it encodes the control sequences expected by the driver and firmware.

Capability discovery precedes register use. mlx5 core code queries PCAM/MCAM/QCAM/SBCAM groups, then tests individual mask bits before using optional registers or features. For example, port code populates `pcam_reg` and `mcam_reg` selectors, clock code uses MTPPS fields for PPS pin configuration and timestamp reads, and reset code checks MFRL capabilities before negotiating firmware reset levels.

Command submission follows the command queue/mailbox contract. The driver writes `mlx5_ifc_cmd_in_bits` or a command-specific input, may chain `mlx5_ifc_cmd_if_box_bits` mailbox blocks, rings the command doorbell described by the initial segment, and later reads `mlx5_ifc_cmd_out_bits` status/syndrome or command-specific output. EQ handling consumes `mlx5_ifc_eqe_bits` ownership and event type/subtype around the per-event union declared earlier in the file.

Register access is read/modify/write by layout. Many registers contain `field_select`, enable, clear, event-arm, or snapshot bits. Callers must set only intended fields and preserve reserved fields. Examples include MTPPS pin state and pulse duration updates, MTPPSE event arming, MFRL reset negotiation, MSEES SyncE admin fields, shared buffer occupancy clearing, and PDDR troubleshooting page selection.

Object lifecycles are create/query/modify/destroy. LAG is created with a `lagc` context, modified by `field_select`, queried into the same context, and destroyed. General objects are created with object type-specific bodies, queried/modified with matching object IDs, and destroyed by generic commands defined elsewhere. UMEM/UCTX/SF/MEMIC lifecycles allocate firmware IDs or address ranges and later deallocate them explicitly.

Migration flows use ordered state transitions. VHCA migration can suspend initiator or responder, query migration state and required UMEM size, save chunks or incremental state into a supplied VA/mkey/size buffer, load state into a destination VHCA, and resume. Page tracking is configured as a general object with ranges and reporting QP, then modified between tracking/reporting/error states while report entries carry dirty addresses.

Security offload flows combine key objects, ASO state, and steering. Encryption key/internal KEK objects provide key material or wrapped-key handles. IPsec and MACsec objects reference DEK numbers, PDs, salts/IVs/SCI, replay window mode, extended sequence number overlap, ASO return register, lifetime/remove-flow arms, and packet counters. Flow steering and ASO WQEs then act on those object IDs.

## State and Persistence Behavior

Most state described here lives in firmware or device MMIO/register space, not in this header. The structs are the shared schema for mutating and observing that state.

Firmware persistent or semi-persistent state includes reset negotiation in MFRL, component update state/data in MCQS/MCQI/MCC/MCDA, module and port configuration registers, QoS/ETS/trust/DSCP mappings, shared buffer allocation/occupancy watermarks, SyncE administrative tracking, clock/PPS pin configuration, and security key/object contents. Some of these settings affect the device until changed or reset; component update and reset state can outlive an individual driver command.

Resource identity is persistent across the life of each firmware object. Returned or supplied IDs such as `uid`, `umem_id`, `function_id`, `obj_id`, `vhca_id`, QP number, mkey, DEK number, update handle, LAG state/active port, and MEMIC address must be tracked by callers and invalidated on failure, reset, or destroy. UMEM and page tracking additionally depend on host memory remaining pinned/mapped for firmware access.

Counters and event arms are stateful. Buffer occupancy maximums can be cleared, IPsec/MACsec ASO lifetime and remove-flow counters are armed, PPS event generation is explicitly armed, PCIe congestion object thresholds latch event state, and page-track reporting state advances as dirty entries are emitted.

The initial segment is live device state. Fields such as `initializing`, `nic_interface`, command queue physical address, health buffer, `clear_int`, syndrome, and health counter are used during initialization, recovery, and health polling. Incorrect writes to MMIO-backed fields can affect command transport or interrupt/health behavior.

## Dependencies and Integration Points

All layouts depend on mlx5 IFC bitfield conventions: arrays of `u8` with bit widths are not normal C storage fields, and access must go through generated-style helpers such as `MLX5_GET`, `MLX5_SET`, `MLX5_ADDR_OF`, and size macros. Many structs also depend on definitions from earlier chunks, including the event union, health buffer, flow table context, general object headers, flow table property layouts, and many port register layouts referenced by the document union.

Core mlx5 integration points include `drivers/net/ethernet/mellanox/mlx5/core/port.c` for PCAM/MCAM and MTPPSE access, `core/lib/clock.c` for MTPPS/PTP pin control, `core/fw_reset.c` and `core/devlink.c` for MFRL reset levels and types, `core/fs_cmd.c` for flow table modification flags, `core/lag/lag.c` for LAG/vport LAG commands, `core/sf/cmd.c` for subfunction allocation, `core/lib/crypto.c` for encryption-key objects, and `core/en/pcie_cong_event.c` for PCIe congestion event objects.

Accelerator integrations are extensive. IPsec object fields and ASO modes are set by Ethernet IPsec offload code and referenced by hardware steering actions. MACsec object fields, replay window sizes, EPN state, and ASO return register are used by MACsec offload. Flow meter ASO and sampler objects are used by TC offload paths. PSP commands are used by `en_accel/psp.c` to rotate device keys and generate SPI/key tuples.

Userspace-facing and virtualization integrations include RDMA DevX UCTX/UMEM creation, fwctl UCTX usage, vDPA UMEM-backed queues, VFIO mlx5 migration commands for VHCA state and dirty page tracking, and scalable function partition/alloc/dealloc commands used by mlx5 SF support.

Management and diagnostics integrate through devlink, ethtool, PTP hardware clock, thermal/health reporting, firmware update/reset flows, module EEPROM/I2C access, SyncE, and PCIe health/congestion notifications. The port document union ties many of these features to the generic register access transport.

## Risks

ABI drift is the main risk. Every field width, offset, reserved gap, enum value, bit mask, variable-length tail, and union overlay must match firmware. Small layout changes can silently program the wrong firmware field because the generated helpers address by bit offset.

Reserved fields must stay zero unless firmware documents otherwise. Many command/register bodies are mostly reserved bits around a few active fields. Reusing stack or heap buffers without zeroing can send unintended bits to firmware, especially for `field_select`, ASO contexts, reset negotiation, LAG modification, and security objects.

Capability checks are mandatory. Optional bits such as enhanced PCAM/MCAM features, MTPPS extensions, MCIA 32-dword access, SyncE registers, page tracking, IPsec/MACsec/general object types, PCIe congestion events, and SF support must be verified before issuing commands. Assuming support will produce command failures or undefined firmware behavior on older devices.

Firmware-owned IDs and host DMA references are leak-prone. UMEM IDs, UCTX UIDs, object IDs, update handles, SF function IDs, page-track reporting QPs, mkeys, and MEMIC ranges require precise cleanup paths. Host VA/mkey/size fields for migration and UMEM/page tracking must reference valid pinned memory for the whole firmware operation.

Security object handling has high blast radius. IPsec, MACsec, TLS, PSP, encryption key, wrapped DEK, and KEK layouts carry key material, salts, IVs, sequence-number state, replay windows, PDs, and lifetime policy. Wrong key size/purpose, stale DEK number, bad overlap/ESN/EPN state, or incorrect ASO register selection can break traffic security or expose material to the wrong protection domain.

Reset and migration state machines are fragile. MFRL reset states distinguish idle, negotiation, in-progress, timeout, NACK, and unload timeout; devlink and firmware reset paths must map them to user-visible reset behavior. VFIO migration must handle uninitialized, idle, ready, dirty, and init states, and must not treat a zero-size dirty report as success when firmware is still reporting.

Flexible array layouts need careful sizing. `mcqi_reg_bits data[]`, `mcda_reg_bits data[]`, `umem_bits mtt[]`, `query_esw_functions_out_bits host_sf_enable[]`, SF partition arrays, page-track ranges, and PSP `key_spi[]` outputs require callers to allocate command buffers based on element counts and firmware-advertised sizes.

## Test and Validation Signals

Build coverage should compile all mlx5 users with warnings and sparse/endian checks enabled, ensuring member names and generated accessors remain consistent after header regeneration. Because this file is included widely, a layout/member mismatch should break users in Ethernet, RDMA, VFIO, vDPA, fwctl, and core mlx5 code.

ABI validation should compare generated bit offsets and struct sizes against the mlx5 firmware specification for capability masks, initial segment, command queue entry, mailbox block, MFRL, MTPPS/MTPPSE, MCQI/MCC/MCDA, LAG, UMEM/UCTX, IPsec/MACsec, page tracking, PCIe congestion, and PSP command buffers.

Runtime command tests should query PCAM/MCAM/QCAM/SBCAM capabilities before exercising optional registers, then issue representative register reads/writes for PAOS, PBMC/SBPR/SBCM, MTPPS/MTPPSE, MFRL, MTMP, MCIA, QPTS/QPDPM/QETC, SyncE, and PCIe congestion object configuration. Tests should verify status/syndrome handling and that reserved fields are zeroed.

Lifecycle tests should create/query/modify/destroy LAG and vport LAG, UMEM, UCTX, MEMIC, SF allocations, sampler, flow meter ASO, encryption key, IPsec, MACsec, and page-track objects. They should include error cleanup, repeated create/destroy loops, device reset in the middle of lifecycles, and validation that firmware IDs are not reused after destroy by stale driver state.

Security offload tests should cover IPsec replay window sizes, ESN overlap modification, ASO increment-SN and replay-protection modes, hard/soft lifetime/remove-flow arms, MACsec confidentiality/EPN/replay windows, key object purposes and sizes, wrapped-key paths, PSP 128-bit and 256-bit SPI generation, and PSP key rotation failure paths.

Migration tests should run suspend/query/save/load/resume flows for both initiator and responder op-mods, incremental and chunked save modes, required UMEM size changes, short buffer handling, dirty page tracking range setup, reporting state transitions, zero-entry reports, and error-state recovery.

Health and reset tests should validate command queue ownership/signature behavior, initial segment health syndrome/counter polling, clear interrupt behavior, firmware reset negotiation through MFRL levels/types/methods, and devlink-visible reset outcomes for timeout, NACK, and unload-timeout states.

## Cross-Chunk Notes

This chunk depends on earlier `mlx5_ifc.h` chunks for common command headers, capability layouts, event unions, general object headers, flow table context, many port register bodies referenced by the document union, and the bitfield accessor macro ecosystem. The merge lane should synthesize this with prior chunks into one per-file report for `sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc.h`; this worker intentionally writes only the chunk research document.
