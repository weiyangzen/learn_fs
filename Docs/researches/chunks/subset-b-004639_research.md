# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_pcol.h lines 5897-11301

## Purpose

This chunk is a generated MCDI protocol contract for the Solarflare/SFC Siena-family NIC driver. It defines command IDs, privilege classes, request/response lengths, field offsets, bit positions, variable-array sizing helpers, and enum values used by host driver code to speak to management-controller firmware. There is no executable C control flow here; the important behavior is the binary ABI described by the macros.

The range covers hardware monitoring, PHY/media queries, lights-out offloads, firmware test/workaround controls, NVRAM metadata, CLP and MUM subprotocols, dynamic sensors, event subscriptions, EVB/buffer-table/license helper structures, EVQ/RXQ/TXQ lifecycle, filter insertion/removal, parser-dispatcher discovery, VI/SR-IOV/PIO allocation, and capability discovery.

## Important APIs, Types, and Protocol Areas

- `MC_CMD_SENSOR_INFO` and `MC_CMD_READ_SENSORS` define the legacy static sensor model. Sensor info is paged, page bit 31 indicates a next page in extended responses, and sensor values are `MC_CMD_SENSOR_VALUE_ENTRY_TYPEDEF` dwords with 16-bit value, 8-bit state, and 8-bit type. States include OK, warning, fatal, broken, no-reading, and init-failed.
- `MC_CMD_DYNAMIC_SENSORS_LIST`, `MC_CMD_DYNAMIC_SENSORS_GET_DESCRIPTIONS`, and `MC_CMD_DYNAMIC_SENSORS_GET_READINGS` define the newer handle-based dynamic sensor API. Handles identify sensors, descriptions carry name/type/limits, readings carry handle/value/state, and the generation count is persistent across reboots and incremented when the table changes.
- `MC_CMD_GET_PHY_STATE`, `MC_CMD_SETUP_8021QBB`, `MC_CMD_GET_PHY_MEDIA_INFO`, and MUM QSFP commands expose PHY health, priority flow control setup, SFP/QSFP media EEPROM-like data, link capability/status, and PHY BIST polling.
- `MC_CMD_WOL_FILTER_GET`, `MC_CMD_ADD_LIGHTSOUT_OFFLOAD`, and `MC_CMD_REMOVE_LIGHTSOUT_OFFLOAD` define WoL and lights-out ARP/IPv6 neighbor-solicitation offload filters. The add call returns a filter ID later used by remove.
- `MC_CMD_TESTASSERT` and `MC_CMD_WORKAROUND` are firmware control/testing hooks. `TESTASSERT_V2` can trigger assertion, watchdog, load/store trap, or invalid jump scenarios. `WORKAROUND` toggles firmware-defined workaround IDs and has special extended output for multicast filter chaining (`BUG26807`) indicating whether FLR was performed.
- `MC_CMD_NVRAM_TEST`, `MC_CMD_NVRAM_PARTITIONS`, `MC_CMD_NVRAM_METADATA`, and `NVRAM_PARTITION_TYPE` enumerate persistent flash partitions and metadata. Partition IDs include MC firmware, expansion ROM, static/dynamic config, logs, dumps, license storage, PHY partitions, FPGA/FC/MUM/SUC partitions, factory defaults, FRU, bundle partitions, recovery map, and partition map.
- `MC_CMD_CLP` multiplexes CLP operations including setting/getting MAC and boot options. The input operation enum distinguishes no-op, set/get MAC, set/get boot, and V2 MAC forms.
- `MC_CMD_MUM` is an insecure/admin-oriented subprotocol for the MUM/SUC controller. It includes raw/read/write/register access, logging, GPIO read/write/config/enable, sensor reads, clock programming, FPGA load control, ATB sensor read, QSFP operations, and DDR information reporting.
- Shared structures include `EVB_PORT_ID`, `EVB_VLAN_TAG`, `BUFTBL_ENTRY`, `LICENSED_APP_ID`, `LICENSED_FEATURES`, `LICENSED_V3_APPS`, `LICENSED_V3_FEATURES`, `TX_TIMESTAMP_EVENT`, `RSS_MODE`, `CTPIO_STATS_MAP`, and `QUEUE_CRC_MODE`.
- `MC_CMD_INIT_EVQ`, `MC_CMD_INIT_RXQ`, and `MC_CMD_INIT_TXQ` define queue creation. EVQs accept timer/count/interrupt configuration and 4K-aligned DMA page arrays. RXQs support legacy and extended V3/V4/V5 layouts, packed stream, equal-stride super-buffer mode, snapshot mode, event merging, outer classification requests, QDMA buffer-size selection, and prefix selection. TXQs support checksum modes, timestamps, pacer bypass, inner checksum flags, TSOv2, CTPIO, M2M D2C, descriptor proxy, and Qbb flags.
- `MC_CMD_FINI_EVQ`, `MC_CMD_FINI_RXQ`, and `MC_CMD_FINI_TXQ` tear down queue instances previously created by the corresponding init commands.
- `MC_CMD_ALLOC_BUFTBL_CHUNK`, `MC_CMD_PROGRAM_BUFTBL_ENTRIES`, and `MC_CMD_FREE_BUFTBL_CHUNK` manage Onload buffer table resources by owner ID, page size, chunk handle, first ID, and DMA addresses.
- `MC_CMD_FILTER_OP` is the main filter ABI. It supports insert/remove/subscribe/unsubscribe/replace, opaque 64-bit handles, port/v-adaptor binding, match-field bitmasks, RX destinations, RX modes, RSS or dot1p contexts, TX destination controls, MAC/port/EtherType/VLAN/IP fields, unknown multicast/unicast matches, VXLAN/NVGRE/Geneve encapsulation matches in the extended forms, and DPDK `rte_flow` flag/mark actions in V3.
- `MC_CMD_GET_PARSER_DISP_INFO` returns parser-dispatcher capabilities: supported RX match masks, insertion restrictions, security-rule info, supported encapsulated matches, and VNIC encapsulation rule matches.
- `MC_CMD_ALLOC_VIS`, `MC_CMD_FREE_VIS`, `MC_CMD_GET_VI_ALLOC_INFO`, `MC_CMD_DUMP_VI_STATE`, `MC_CMD_ALLOC_PIOBUF`, and `MC_CMD_FREE_PIOBUF` manage VI and PIO resources and expose diagnostic state for queue backing tables and metadata.
- `MC_CMD_GET_SRIOV_CFG` and `MC_CMD_SET_SRIOV_CFG` expose PF/VF enablement, VF count, RID offset, and stride. Set is admin-only.
- `MC_CMD_GET_CAPABILITIES` and `GET_CAPABILITIES_V2` expose feature flags and firmware identity for RX/TX datapath CPUs and packet-dispatch firmware. Flags gate EVB, VXLAN/NVGRE, Qbb, RSS modes, packed-stream, timestamps, batching, VLAN insertion/stripping, TSO, RX prefix lengths, event merging, multicast filter chaining, and other datapath features.

## Control Flow and Lifetimes

The host driver builds MCDI request buffers using these offsets and length macros, sends command IDs to firmware, and parses response buffers by the matching output layouts. Sequencing is implied by resource lifetimes:

- Probe/configuration code queries capabilities, resource limits, port assignment, MAC address allocation, sensors, PHY state, media info, parser-dispatcher capabilities, SR-IOV state, and NVRAM partitions/metadata.
- Runtime datapath setup allocates VIs, creates EVQs, creates RXQs/TXQs backed by DMA page arrays, programs buffer table chunks for Onload paths, installs filters, and optionally allocates PIO buffers.
- Runtime monitoring reads legacy or dynamic sensors and listens for sensor/link/reboot/FW alert event classes via `MC_CMD_EVENT_CTRL`.
- Shutdown/error paths remove filters, free PIO/buffer-table resources, finish TXQ/RXQ/EVQ instances, and free VIs.
- Special test and recovery paths can generate driver events, dump VI state, read MC registers, deliberately crash firmware, toggle firmware workarounds, restore MAC state after reset, or manipulate MUM hardware controls.

Resource handles are firmware-owned and opaque to the host: filter handles, buffer-table chunk handles, PIO buffer handles, VI base/count, lights-out filter IDs, dynamic sensor handles, RSS/dot1p context IDs referenced by filters, and queue instance IDs. The header repeatedly documents that handles should be considered opaque and that sentinel all-ones values are invalid for filter handles.

## State and Persistence Behavior

Most commands describe volatile runtime state inside the NIC firmware: queue tables, filter tables, VI allocation, PIO buffers, buffer table entries, event subscriptions, port assignment, and SR-IOV configuration. These must be reconstructed after reset or firmware reboot unless the broader driver has explicit persistence logic.

Persistent or semi-persistent areas in this chunk are:

- NVRAM partition contents and metadata, including firmware, configuration, logs, licenses, bundle state, factory defaults, and partition maps.
- Dynamic sensor generation count, which the comments state is maintained by the MC, persistent across reboots, and incremented whenever the sensor table changes.
- Sensor limit programming through `MC_CMD_SENSOR_SET_LIMS`, marked as a warranty-voiding insecure operation.
- MUM/SUC GPIO, clock, FPGA-load, firmware, boot ROM, production/user ROM, fuses/lockbits, and DDR state, where some effects may outlive a single host driver session depending on underlying hardware/firmware.

## Dependencies and Integration Points

The macros depend on the driver MCDI transport and packing helpers elsewhere in the SFC driver. Consumers must use the offset/length/LBN/WIDTH definitions consistently with kernel endianness helpers and MCDI buffer accessors.

Privilege categories (`SRIOV_CTG_GENERAL`, `LINK`, `ADMIN`, `INSECURE`, `ONLOAD`) are integration boundaries for PF/VF and management policy. General calls are available for ordinary driver operation; link/admin/insecure/onload calls must be guarded by privilege checks and feature discovery.

Important cross-protocol dependencies include:

- Queue commands depend on VI allocation, interrupt/vector allocation, DMA mapping, and 4K-aligned host memory pages.
- Filter RX modes depend on RSS context allocation or dot1p mapping allocation commands defined outside this chunk.
- Filter extension support depends on parser-dispatcher discovery and capability flags such as VXLAN/NVGRE and DPDK firmware IDs.
- Dynamic sensors tie into unsolicited `CODE_DYNAMIC_SENSORS_CHANGE` events and event-control subscription.
- Legacy sensor state ties into `SENSOREVT` events and page-aware sensor info discovery.
- TX/RX timestamp fields and CTPIO events integrate with event queue parsing and PTP/timestamp feature licensing.
- `GET_CAPABILITIES` gates use of advanced queue flags, packed-stream, RSS, timestamps, VLAN, TSO, Qbb, EVB, and overlay filtering.
- NVRAM metadata integrates with update, diagnostics, license, and firmware-management tooling outside this chunk.

## Risks and Edge Cases

- ABI drift is the core risk. Any offset, length, enum, or bit-position mismatch will corrupt MCDI requests or misparse firmware responses.
- Variable-length responses have MCDI v1/v2 maxima. Callers must use the `_LEN(num)` and `_NUM(len)` helpers and avoid assuming all entries fit in a legacy 252-byte response.
- Sensor APIs are split between legacy paged masks and dynamic handle-based sensors. A driver using the wrong path for a capability can miss sensors or mishandle change events.
- DMA-backed commands require correct DMA address width, alignment, buffer length, and lifetime. `READ_SENSORS` requires a 4K-aligned buffer unless using the all-ones cmdclient response path; queue init requires arrays of 4K-aligned page addresses.
- Queue init variants are easy to misuse: some fields are ignored in packed-stream/equal-stride modes, V4 buffer size is QDMA-specific, V5 prefix selection is newer, and firmware may override EVQ flags in low-latency/throughput/auto modes.
- Filter programming is high-risk because match-field bitmasks must correspond exactly to filled fields. Encapsulation matches require different field sets, VNI/VSID type encoding, and firmware variant support. DPDK match actions fail on non-DPDK firmware and mark values must be within capability-reported limits.
- `MC_CMD_WORKAROUND_BUG26807` can FLR functions with installed filters for admin callers. Client code must treat this as disruptive state loss and not as a simple feature toggle.
- `MC_CMD_TESTASSERT`, `MC_CMD_READ_REGS`, `MC_CMD_MUM`, and `MC_CMD_SENSOR_SET_LIMS` are admin/insecure/debug surfaces and should not be exposed to untrusted paths.
- Some comments call out older firmware that does not understand newer workaround IDs. Callers should treat `EINVAL`/`ENOTSUP` according to the documented compatibility guidance.
- Opaque handles can change on filter replace, and all-ones is guaranteed invalid. Callers must update stored handles from responses rather than deriving or reusing stale values.
- SR-IOV RID offset/stride fields allow zero for no-change and `MC_CMD_RESOURCE_INSTANCE_ANY` for firmware allocation; confusing these values can produce invalid VF topology.

## Test Signals

Useful validation signals for code using this chunk:

- Compile-time checks that MCDI request/response buffer sizes match `_LEN`, `_LENMIN`, `_LENMAX`, and variant-specific constants.
- Probe tests that call `GET_CAPABILITIES`, select only supported queue/filter/sensor paths, and reject unsupported advanced flags gracefully.
- Sensor tests covering legacy page 0, extended multi-page masks, dynamic sensor list/description/reading batches, generation-count changes, and dropped stale handles.
- Queue lifecycle tests that allocate VIs, init EVQ/RXQ/TXQ with aligned DMA pages, process events, and then finish/free resources in reverse order.
- Filter tests for insert/remove/replace, opaque handle update, RSS and simple RX modes, unknown unicast/multicast filters, overlay VNI/VSID matches, and parser-dispatcher supported-match discovery.
- Reset/reboot tests ensuring queues, filters, VI allocation, PIO buffers, lights-out offloads, and event subscriptions are recreated or cleaned up after MC reboot.
- Negative tests for unsupported firmware variants, privilege failures, bad lengths, insufficient DMA buffer lengths, too many variable-array entries, invalid handles, and invalid filter mark values.
- Debug-path tests should verify `TESTASSERT` handling only in controlled environments and confirm the driver reports firmware assertion/watchdog/trap outcomes without assuming normal command completion.
