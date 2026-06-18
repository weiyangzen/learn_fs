# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/reg.h lines 8859-13211

Chunk ID: `subset-b-004557`

## Scope and Purpose

This chunk is the final large register-definition span of Mellanox/NVIDIA `mlxsw`'s `reg.h`. It covers the tail of router register support, most management and monitoring register definitions, tunnel register definitions for NVE and IP-in-IP, shared-buffer registers, the global register-info lookup table, and the PUDE port up/down event layout.

The code is not an executing driver module by itself. It is a declarative register contract: each `MLXSW_REG_DEFINE()` declares a hardware/firmware register ID and payload length, `MLXSW_ITEM*()` macros describe bit fields and buffers inside that payload, and small `static inline` pack/unpack helpers zero and populate command payloads before the core register transport submits them. The surrounding mlxsw driver layers use these definitions to configure routing, multicast, monitoring, firmware update, device management, tunneling, shared buffers, and event decoding.

## Important APIs, Types, and Functions

- Router tail definitions include `rigr2`, `recr2`, `rmft2`, and `reiv`. `mlxsw_reg_rigr2_pack()` and `mlxsw_reg_rigr2_erif_entry_pack()` build router interface group records; `mlxsw_reg_recr2_pack()` initializes ECMP hash configuration; `mlxsw_reg_rmft2_ipv4_pack()` and `mlxsw_reg_rmft2_ipv6_pack()` program multicast forwarding TCAM entries; `mlxsw_reg_reiv_pack()` selects the egress-RIF/port-page key for egress VID mapping.
- ECMP hash enums define outer and inner header layers and fields used by `recr2`, including IPv4/IPv6 source/destination fields, protocol/next-header, flow label, and TCP/UDP ports. Callers set bit arrays after `mlxsw_reg_recr2_pack()` to choose the exact hash key.
- Fan and thermal registers include `mfcr`, `mfsc`, `mfsm`, `mfsl`, `fore`, `mtcap`, `mtmp`, `mtwe`, and `mtbr`. They expose PWM frequency/active masks, duty cycle, tachometer RPM and thresholds, fan-under-limit events, sensor count, per-sensor temperature/max/threshold data, warning bitmaps, and bulk temperature records. `MLXSW_REG_MTMP_TEMP_TO_MC()` converts signed 0.125-degree units into millidegrees Celsius.
- Module EEPROM and status access is defined by `mcia` and `mcion`. `mlxsw_reg_mcia_pack()` selects slot, module, page, device offset, size, and I2C address for SFP/QSFP/CMIS EEPROM reads. Constants encode page lengths, low/high I2C addresses, flat-memory handling, threshold page offsets, and module ID/revision values. `mlxsw_reg_mcion_pack()` selects a module for presence and low-power status bits.
- Port analyzer and sampling registers include `mpat`, `mpar`, `mpsc`, `mgpc`, `mprs`, `mogcr`, `mpagr`, and `momte`. These cover mirror-session destinations and encapsulations, per-port ingress/egress mirroring, packet sampling rate, general-purpose counters, parser depth and VXLAN UDP port, global PTP/mirroring policer configuration, global mirror-trigger mapping, and per-port mirror-trigger enable masks.
- System and firmware management registers include `mgir`, `mrsr`, `mlcr`, `mcqi`, `mcc`, `mcda`, `mcam`, `mfgd`, `mgpir`, `mbct`, `mddt`, `mddq`, `mddc`, and `mfde`. They expose hardware/firmware identity, reset commands, LED beaconing, firmware component query/control/data flows, management capability bits, firmware fatal-debug controls/events, peripheral topology, INI/binary transfer to management firmware, downstream-device tunneling/query/control, and firmware debug event payloads.
- PTP/time registers include `mtpps`, `mtutc`, `mtpppc`, `mtpptr`, `mtptpt`, and `mtpcpc`. They configure virtual PPS pins, UTC set/adjust/frequency operations, PTP message types to timestamp or trap, timestamp FIFO records, and correction-field handling.
- Tunnel registers include `tngcr`, `tnumt`, `tnqcr`, `tnqdr`, `tneem`, `tndem`, `tnpc`, `tigcr`, `tieem`, and `tidem`. They configure NVE tunnel type, TTL, flow-label and UDP-source-port hashing, underlay multicast tables, NVE QoS/ECN mapping, tunnel-port learning, IP-in-IP TTL behavior, and IP-in-IP ECN mapping/trap actions.
- Shared-buffer registers include `sbpr`, `sbcm`, `sbpm`, `sbmm`, `sbsr`, and `sbib`. They configure pool size/mode, port-priority or traffic-class quotas, port-pool quota and occupancy, multicast priority quotas, bulk occupancy snapshots, and internal per-port buffers used by features such as egress mirroring.
- `mlxsw_reg_infos[]` registers all known `struct mlxsw_reg_info` descriptors, including many definitions from earlier chunks and all definitions in this chunk. `mlxsw_reg_id_str()` linearly maps a register ID back to a human-readable register name. The final PUDE layout defines fields used to decode port up/down events.

## Control Flow

The dominant control-flow pattern is payload construction:

1. A caller allocates or receives a `char *payload` of the register's declared length.
2. The relevant `mlxsw_reg_*_pack()` helper calls `MLXSW_REG_ZERO()` for full-payload initialization.
3. The helper writes index, operation, and common RW fields through generated setters.
4. Optional follow-up helpers or direct generated setters fill variable bit arrays, repeated records, buffers, or protocol-specific fields.
5. The payload is submitted to the mlxsw register transport for query or write, and any returned payload is decoded through generated getters or explicit unpack helpers.

Router multicast programming follows this pattern closely. `mlxsw_reg_rmft2_common_pack()` zeros the register, writes valid/op/offset/VRF/ingress-RIF key fields, and optionally copies the flexible action set. IPv4 and IPv6 wrappers then set the address-family type and copy DIP/SIP values plus masks. Deletion is represented by packing `v = false` with the same key/offset semantics.

Monitoring and management helpers are thin but encode important sequencing assumptions. Firmware component update uses `mcqi` to query component limits and access granularity, `mcc` to lock/update/verify/activate/cancel the component FSM and retrieve an update handle/error/control state, and `mcda` to transfer data words under that handle. INI/binary transfer to line-card management firmware uses `mbct`: the caller packs an opcode, optionally enables opcode events, attaches up to 1 KB of data through `mlxsw_reg_mbct_dt_pack()`, marks the last chunk, and later unpacks status/FSM state.

Downstream-device access is a nested-register flow. `mlxsw_reg_mddt_pack()` receives an inner `struct mlxsw_reg_info`, bounds the inner register plus a four-byte PRM header against `MLXSW_REG_MDDT_LEN`, fills MDDT slot/device/method/register-id/read-size/write-size fields, and returns `inner_payload` pointing into the embedded register area. The caller then packs the downstream register into that inner region. `mddq` has three separate query flows for slot info, device info, and slot name, all funneled through `__mlxsw_reg_mddq_pack()`.

PTP timestamping is another multi-register flow. `mtpppc` selects message types to timestamp, `mtptpt` maps message types to trap IDs, `mtpcpc` enables traps and correction-field updates globally or per port, and `mtpptr` reads records from per-port ingress/egress timestamp FIFOs. `mlxsw_reg_mtpptr_unpack()` reconstructs the 64-bit timestamp from high/low fields and returns the PTP message type, domain, and sequence ID used to match trapped packets.

Tunnel setup is staged. `tngcr` establishes NVE tunnel type and global VTEP behavior; callers then set underlay VRF/RIF/source addresses and group sizes as needed. `tnumt` populates underlay multicast/flood lists, `tnqcr`/`tnqdr` define DSCP policy, `tneem` and `tndem` define ECN encapsulation/decapsulation matrices, and `tnpc` controls tunnel-port learning on Spectrum-2 style devices. IP-in-IP has a smaller parallel set: `tigcr` for TTL copy/default, `tieem` for encapsulation ECN, and `tidem` for decapsulation ECN and optional traps.

Shared-buffer control is split between configuration and observation. `sbpr`, `sbcm`, `sbpm`, `sbmm`, and `sbib` pack one selected pool/port/class/priority object per payload. `sbpm_unpack()` reads one port-pool occupancy pair. `sbsr` is a bulk read mechanism: callers set ingress/egress port masks and priority/tclass masks after `mlxsw_reg_sbsr_pack()`, then iterate `mlxsw_reg_sbsr_rec_unpack()` records. The comment explicitly warns that too many requested records can exceed the transport MTU and be silently truncated.

## State and Persistence Behavior

This header owns no runtime state beyond compile-time constants and generated inline functions. Persistent state lives in hardware or firmware registers after successful register writes, and in higher-level driver objects that decide when to replay those writes after reload, reset, line-card provisioning, or feature toggles.

Several hardware-persistent domains are represented:

- Router state: ECMP hash seeds and fields, multicast forwarding entries, RIF group membership, egress VID mappings, and multicast action sets persist in switch/router tables until changed or invalidated.
- Environmental state: fan PWM frequency/duty cycle, tachometer thresholds, temperature event thresholds, max-temperature enable/reset behavior, sensor warning state, and fan-under-limit status are firmware/hardware managed and queried by health and hwmon paths.
- Module and peripheral state: EEPROM reads are transient, but module low-power/presence notifications, slot/device topology, INI provisioning state, downstream-device enable/reset state, and binary-transfer FSM state persist in management firmware.
- Firmware update state: MCQI/MCC/MCDA and MBCT flows use update handles, FSM states, status codes, and transfer offsets. The header encodes the fields, while callers must serialize operations and honor alignment, component size, max-write-size, and status transitions.
- Monitoring/mirroring state: analyzer table entries, per-port analyzer enables, sampling rates, parser depth, mirror trigger mappings, mirror trigger enable masks, PTP timestamp/trap configuration, and general-purpose counters remain active until reconfigured.
- Tunnel state: NVE/IP-in-IP global settings, underlay multicast table records, QoS and ECN mappings, tunnel-port learning flags, source addresses, and TTL behavior define packet-processing behavior in hardware.
- Shared-buffer state: pool sizes/modes, class/port/priority quotas, dynamic alpha values, infinite flags, occupancy max tracking, and clear bits are maintained in switch buffer hardware.

The pack helpers mostly zero entire payloads, which is a deliberate safety pattern for reserved fields. Helpers that only set a subset of a register rely on callers to fill additional fields before write, or on hardware defaults/ignored fields. Unpack helpers often tolerate optional output pointers, but not consistently: some helpers check pointers before assignment, while others such as `mlxsw_reg_mgir_unpack()`, `mlxsw_reg_mcqi_unpack()`, `mlxsw_reg_mtpptr_unpack()`, and several `mddq` unpack helpers assume non-NULL outputs.

## Dependencies and Integration Points

The chunk depends on the core mlxsw register-description macros defined earlier in the same header or adjacent headers: `MLXSW_REG_DEFINE`, `MLXSW_REG_ZERO`, `MLXSW_REG`, `MLXSW_ITEM32`, `MLXSW_ITEM32_INDEXED`, `MLXSW_ITEM64`, `MLXSW_ITEM_BUF`, `MLXSW_ITEM_BIT_ARRAY`, and `MLXSW_ITEM32_LP`. These macros generate the typed setters/getters/memcpy helpers used throughout the inline functions.

Kernel dependencies visible in this span include fixed-width integer types, `bool`, `BIT()`, `GENMASK()`, `BITS_PER_BYTE`, `ARRAY_SIZE()`, `WARN_ON()` / `WARN_ON_ONCE()`, and `struct in6_addr`. The code also references mlxsw-specific enums or register concepts defined elsewhere, such as `enum mlxsw_reg_flow_counter_set_type`, `enum mlxsw_reg_tunnel_port`, `struct mlxsw_reg_info`, and `MLXSW_REG_FLEX_ACTION_SET_LEN`.

Major integration points by driver area:

- Router and Spectrum L3 code uses `rigr2`, `recr2`, `rmft2`, and `reiv` to build ECMP, multicast routing, and egress VLAN behavior.
- Hwmon and thermal drivers use fan/temperature registers for PWM, RPM, tach thresholds, sensor names, temperature readings, and warning/fault event decoding.
- Ethtool/module code uses MCIA and MCION to implement EEPROM reads, module page/bank selection, SFP/QSFP/CMIS handling, and module status reporting.
- Devlink, firmware flashing, and line-card management use MGIR, MRSR, MCQI/MCC/MCDA, MCAM, MGPIR, MBCT, MDDT/MDDQ/MDDC, MFGD, and MFDE.
- Mirroring, sampling, ACL/actions, and telemetry code use MPAT/MPAR/MPAGR/MOMTE/MPSC/MGPC/MPRS/MOGCR.
- PTP support uses MTPPS, MTUTC, MTPPPC, MTPPTR, MTPTPT, and MTPCPC alongside trap handling and timestamp FIFO reads.
- VXLAN/NVE/IP-in-IP offload code uses TNGCR/TNUMT/TNQCR/TNQDR/TNEEM/TNDEM/TNPC/TIGCR/TIEEM/TIDEM.
- Devlink shared-buffer and QoS code uses SBPR/SBCM/SBPM/SBMM/SBSR/SBIB for pool, threshold, and occupancy configuration/reporting.
- Core register transport and diagnostics use `mlxsw_reg_infos[]` and `mlxsw_reg_id_str()` to validate/register supported IDs and print readable names in errors/logs.

## Risks and Edge Cases

- These definitions are layout-critical. A wrong offset, width, index stride, record count, or length constant silently corrupts firmware commands because generated accessors will write the wrong payload bits.
- Several helpers set only a safe baseline. For example, `mlxsw_reg_recr2_pack()` sets seed and symmetric hash but does not enable hash fields; `mlxsw_reg_tngcr_pack()` sets default TTL/hash/group behavior but not underlay VRF/RIF/source addresses; `mlxsw_reg_sbsr_pack()` only sets `clr`, leaving masks to callers. Tests must verify full caller-side payload completion.
- Access qualifiers matter. Some fields are `Index`, `OP`, `WO`, or `RO`, but the C accessors do not enforce register-operation legality. Callers can accidentally set read-only fields or omit required index fields unless reviewed against the hardware spec.
- `mlxsw_reg_mddt_pack()` truncates the nested transfer length after `WARN_ON()` if the embedded register would exceed the MDDT payload. That prevents overflow, but a caller that ignores the warning could send a partial downstream register.
- `mlxsw_reg_mbct_dt_pack()` returns early on `data_size > 1024`, leaving an already-packed MBCT opcode payload without updated data fields. Callers must treat the warning as a hard failure.
- `mlxsw_reg_mcda_pack()` copies `size / 4` words by casting `&data[i * 4]` to `u32 *`. Callers must honor MCQI word-size and DWORD-alignment constraints; unaligned or non-DWORD trailing data is not copied by this helper.
- Temperature conversion is subtle for negative signed 16-bit firmware values. `MLXSW_REG_MTMP_TEMP_TO_MC()` relies on sign handling and two's-complement reconstruction; regressions here affect hwmon readings and threshold comparisons.
- `mtbr` declares `REC_MAX_COUNT` as 1 in this source, despite register comments allowing a range up to 255 records. Callers expecting bulk reads of many sensors must use the actual declared mlxsw payload length or update the length/record constants consistently.
- `sbsr` can return truncated responses when masks request too many records. Because the hardware gives no special truncation notice, callers must bound mask breadth and record iteration against the requested response size.
- Many unpack helpers assume non-NULL output pointers. Passing optional NULLs inconsistently can crash in inline code, especially in firmware/device query paths.
- Register support varies by ASIC generation. Comments mark fields or whole registers as reserved on Spectrum, Spectrum-1, Spectrum-2, SwitchX, IB switches, or Quantum. Higher layers must gate writes with capability bits such as MCAM or device-family checks.
- The `mlxsw_reg_infos[]` table must stay synchronized with new register definitions. A missing entry can break generic lookup/validation or reduce diagnostic quality even if the accessor macros compile.
- ECN and trap mappings are matrix-like. NVE/IP-in-IP encapsulation and decapsulation mappings must cover all relevant overlay/underlay ECN combinations, and trap IDs must match the trap subsystem definitions.
- Shared-buffer dynamic threshold values use encoded alpha values with a documented range of 1..14 plus infinity forms. Treating these fields as raw cells when the pool is dynamic will misconfigure congestion behavior.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage of all generated accessors and inline helpers under mlxsw configurations that include Spectrum routing, hwmon, devlink flash, line cards, PTP, tunneling, mirroring, and shared-buffer support.
- Register payload unit tests or debug assertions that pack representative payloads and compare byte-level layouts for `rmft2`, `mcia`, `mcqi/mcc/mcda`, `mddt/mddq`, `tngcr/tnumt`, `tndem/tidem`, and shared-buffer registers against hardware-spec fixtures.
- ECMP and multicast routing tests that verify RECR2 hash-field enable masks, RIGR2 next-group chaining, RMFT2 IPv4/IPv6 address/mask/action programming, and REIV egress VID mapping.
- Hwmon/thermal tests that cover positive and negative MTMP readings, max-temperature reset/enable, sensor names, MTWE warning bits, MTBR error-status values, fan PWM duty cycle, tachometer limits, and FORE fault extraction.
- Module EEPROM tests for SFP, QSFP, QSFP-DD, OSFP, CMIS flat memory, high/low I2C addresses, page/bank selection, 48-byte versus 128-byte MCIA capability, no-module/no-EEPROM/I2C-error statuses, and MCION presence/low-power bits.
- Firmware flashing tests that exercise MCQI capability discovery, MCC lock/update/verify/activate/cancel transitions, MCDA alignment and max write sizes, update-handle propagation, MBCT erase/data/activate/status flows, and error-state cleanup.
- Line-card/downstream-device tests for MGPIR topology discovery, MDDQ slot/device/name multi-message sequencing, MDDC reset/device-enable behavior, and MDDT nested register tunneling with oversized-register warning coverage.
- Mirroring/sampling tests for local and remote SPAN, RSPAN VLAN/L2/L3 encapsulation, IPv4/IPv6 mirror tunnel fields, per-port MPAR enables, MPAGR trigger mapping, MOMTE trigger masks, MPSC sampling rate bounds, and MGPC clear/read behavior.
- PTP tests for UTC set/immediate adjust/frequency adjust bounds, virtual PPS programming, ingress/egress timestamp message masks, trap IDs, timestamp FIFO clear and record count handling, and correction-field enablement.
- Tunnel offload tests for NVE type selection, underlay source IPv4/IPv6 programming, UDP source-port hash prefix, flow-label copy/hash modes, multicast/flood TNUMT chains, DSCP defaults, all ECN map combinations, tunnel-port learning, and IP-in-IP TTL/ECN behavior.
- Shared-buffer tests through devlink/SB APIs for static versus dynamic pool modes, infinity flags, alpha range validation, per-port and per-PG quotas, multicast priority quotas, SBSR bulk occupancy masking/truncation bounds, max-occupancy clear semantics, and SBIB egress-mirroring headroom.
- Event and diagnostic tests that decode PUDE port events and MFDE firmware debug events, and that verify `mlxsw_reg_id_str()` returns expected names for every register listed in `mlxsw_reg_infos[]` and `*UNKNOWN*` for unmapped IDs.
