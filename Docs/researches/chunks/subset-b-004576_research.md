# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main_regs.h lines 6023-8258

Chunk ID: `subset-b-004576`

## Scope and Purpose

This chunk is the tail of the generated Sparx5/LAN969x main register header. It starts in the 25G Base-R PCS configuration block, then covers 5G/25G PCS signal-detect controls, port hardware-mode muxing, PTP time-of-day and timestamp FIFO registers, queue forwarding/resource/system registers, rewriter registers, VCAP cache/update registers for ES0/ES2/SUPER, RAM initialization hooks, XQS counters and queue-limit sharing, and LAN969x RGMII MAC/device registers. The file ends with the include guard at line 8258.

The code is not executable driver logic by itself. It is a hardware register ABI map: each macro expands to `__REG(...)` address parameters consumed by `spx5_rd()`, `spx5_wr()`, `spx5_rmw()`, and instance variants, while the paired field macros wrap `FIELD_PREP()`, `FIELD_GET()`, or Sparx5 dynamic-width helpers (`spx5_field_prep()`, `spx5_field_get()`). The definitions let higher-level Sparx5 and LAN969x driver code configure switch port datapaths, CPU packet I/O, flow control, timestamping, ACL/VCAP tables, and statistics without open-coding offsets and bit shifts.

Several definitions are explicitly device-family scoped by comments. Some registers are `SPARX5 ONLY`, such as 25G PCS, parts of PTP phase detector controls, and REW two-step PTP FIFO access. Others are `LAN969X ONLY`, including DEVCPU PTP timestamp FIFO registers and `DEVRGMII_*` RGMII MAC/device controls. The common macros use `regs->gaddr`, `regs->gcnt`, `regs->gsize`, `regs->rcnt`, `regs->fpos`, and `regs->fsize` so the same header can serve Sparx5 and LAN969x layouts with different counts, field widths, and base addresses.

## Important APIs, Types, and Macro Families

- `PCS25G_BR_PCS_CFG`, `PCS25G_BR_PCS_SD_CFG`, `PCS5G_BR_PCS_CFG`, and `PCS5G_BR_PCS_SD_CFG` describe Base-R PCS enablement, PMA loopback, sync-header count limits, RX/TX data lane flipping, resync, local-fault generation, scrambler bypass/test modes, autonegotiation link control, and signal-detect source/polarity/enable.
- `PORT_CONF_DEV5G_MODES`, `PORT_CONF_DEV10G_MODES`, and `PORT_CONF_DEV25G_MODES` expose per-device mode bits used to switch ports between low-speed and high-speed device blocks. `PORT_CONF_QSGMII_ENA` and `PORT_CONF_USGMII_CFG(g)` select QSGMII/USGMII behavior, including scrambler/descrambler bypass, lane flipping, hysteresis disable, energy-detect enable, I1 usage, and quad mode.
- `PTP_PTP_PIN_INTR`, `PTP_PTP_PIN_INTR_ENA`, and `PTP_PTP_INTR_IDENT` provide PTP pin interrupt status, enable, and identity fields. `PTP_PTP_DOM_CFG` controls PTP domain enable, hold, time-of-day freeze, and clock-configuration disable bits for the three PTP TOD domains.
- `PTP_CLK_PER_CFG`, `PTP_PTP_CUR_NSEC`, `PTP_PTP_CUR_NSEC_FRAC`, `PTP_PTP_CUR_SEC_LSB`, `PTP_PTP_CUR_SEC_MSB`, and `PTP_NTP_CUR_NSEC` describe current PTP/NTP time values per TOD domain. PTP pin waveform registers (`PTP_PTP_PIN_CFG`, `PTP_PTP_TOD_*`, `PTP_PIN_WF_*`, and `PTP_PIN_IOBOUNCH_DELAY`) configure pin actions, sync source, polarity, selected pin, clock domain, output offset, absolute TOD, high/low waveform periods, and input debounce.
- `PTP_PHAD_CTRL` and `PTP_PHAD_CYC_STAT` describe phase detector enable/failure, Sparx5 reduced resolution, lock accuracy, and cycle status for clock phase alignment.
- `PTP_TWOSTEP_CTRL`, `PTP_TWOSTEP_STAMP_NSEC`, and `PTP_TWOSTEP_STAMP_SUBNS` are LAN969x two-step timestamp FIFO registers. Their fields indicate FIFO validity, overflow, TX/RX stamp type, source port, next-entry pop, overwrite enable, nanosecond stamp, and sub-nanosecond bits.
- `QFWD_SWITCH_PORT_MODE(r)` controls queue-forwarding port enablement, forwarding urgency, yellow reservation, ingress/egress drop modes, sharing disables, egress reservation disable, and learn-all behavior. `QFWD_FRAME_COPY_CFG(r)` maps frame-copy destinations to ports with a device-dependent port-width field.
- `QRES_RES_CFG`, `QRES_RES_STAT`, and `QRES_RES_STAT_CUR` expose queue resource high-watermark configuration, maximum use, and current in-use values.
- `QS_XTR_*` and `QS_INJ_*` define CPU extraction/injection group configuration, extraction reads and flush, data-present status, injection writes, SOF/EOF/abort/valid-byte controls, gap size, FIFO readiness, watermark status, and injection-in-progress status.
- `QSYS_PAUSE_CFG`, `QSYS_ATOP`, `QSYS_FWD_PRESSURE`, `QSYS_ATOP_TOT_CFG`, `QSYS_CAL_AUTO`, `QSYS_CAL_CTRL`, and `QSYS_RAM_INIT` configure per-port pause watermarks, aggressive tail-drop, ATOP tail-drop thresholds, forwarding pressure, total ATOP, auto-calendar slots, calendar mode/grant rate/error status, and QSYS RAM initialization hooks.
- `REW_*` registers configure the rewriter: own UPSID, RTAG/ETAG and ES0 lookup controls, per-port VLAN PCP/DEI/VID defaults, PCP/DEI egress maps for drop precedence 0/1, tag rewrite control, DSCP rewrite/remap enablement, Sparx5 two-step PTP FIFO registers under the REW block, reserved-not-zero PTP words, generated timestamp format, and REW RAM initialization.
- `VCAP_ES0_*`, `VCAP_ES2_*`, and `VCAP_SUPER_*` define the VCAP cache/update interface. Each VCAP family has update control, move configuration, entry/mask/action/counter cache arrays, full-word counter data, type-group data, core index/map registers, capability constants, and in ES0/ES2 sticky row-deleted state. `VCAP_SUPER_RAM_INIT` adds RAM initialization for the SUPER VCAP.
- `VOP_RAM_INIT` initializes VOP RAM. `XQS_STAT_CFG`, `XQS_QLIMIT_SHR_*`, and `XQS_CNT(g)` select XQS statistic views, clear selected stat groups, control counter wrap/service-packet filtering, configure shared queue-limit thresholds, and read queue-system counters.
- `DEVRGMII_DEV_RST_CTRL`, `DEVRGMII_MAC_ENA_CFG`, `DEVRGMII_MAC_TAGS_CFG`, and `DEVRGMII_MAC_IFG_CFG` are LAN969x RGMII-specific controls for device speed, MAC RX/TX enablement, VLAN tag awareness and tag EtherType, provider-bridge mode, and RX/TX inter-frame gaps.

## Control Flow and Sequencing

The register macros are consumed through the generic Sparx5 access helpers in `sparx5_main.h`. A macro such as `QSYS_PAUSE_CFG(port)` expands to target ID, target instance, group base/count/width, register address, register index/count, and register width. `spx5_rd()` and `spx5_wr()` compute the MMIO address with `spx5_addr()` and perform `readl()`/`writel()`. `spx5_rmw()` reads the current word, applies `(old & ~mask) | (val & mask)`, and writes the result back.

Port setup is the most visible consumer path. `sparx5_port_mux_set()` enables QSGMII groups with `PORT_CONF_QSGMII_ENA` and, for selected port groups, configures `PORT_CONF_USGMII_CFG` to bypass scrambling/descrambling and enter quad mode. `sparx5_dev_switch()` uses `PORT_CONF_DEV5G_MODES`, `PORT_CONF_DEV10G_MODES`, or `PORT_CONF_DEV25G_MODES` to select the low-speed versus high-speed device backing a logical port. `sparx5_port_init()` programs QSYS pause start/stop and ATOP thresholds, and later speed configuration enables the port in `QFWD_SWITCH_PORT_MODE` with a speed-derived forwarding urgency.

CPU packet I/O is configured in `sparx5_fdma_injection_mode()`. The driver sets extraction and injection groups to FDMA mode through `QS_XTR_GRP_CFG` and `QS_INJ_GRP_CFG`, chooses status-word placement and byte swapping, configures CPU ports, clears disassembler stop watermark counters, and enables queue forwarding for the internal CPU ports with `QFWD_SWITCH_PORT_MODE`.

The QSYS calendar flow in `sparx5_calendar.c` calculates port bandwidth slots, optionally halts the calendar on Sparx5 by writing a stop mode to `QSYS_CAL_CTRL`, writes `QSYS_CAL_AUTO(idx)` entries, adjusts `QSYS_CAL_CTRL_CAL_AUTO_GRANT_RATE`, enables auto mode, and finally checks `QSYS_CAL_CTRL_CAL_AUTO_ERROR`. This makes `QSYS_CAL_CTRL` both a control register and an error signal for calendar programming.

XQS statistics are view-based. `sparx5_get_queue_sys_stats()` locks `queue_stats_lock`, selects a port with `XQS_STAT_CFG_STAT_VIEW_SET(portno)`, then reads fixed counter offsets through `XQS_CNT(addr)`. `sparx5_config_port_stats()` clears queue-system counters for a selected view by combining `STAT_VIEW` with `STAT_CLEAR_SHOT`.

VCAP operations use a cache-and-shot sequence. `sparx5_vcap_impl.c` writes entry, mask, action, type-group, and counter cache words through `VCAP_*_VCAP_*_DAT()` registers, writes `VCAP_*_CFG` for move/initialize sizing when needed, then writes `VCAP_*_CTRL` with update command, selected entry/action/counter disable bits, target address, optional cache clear, and `UPDATE_SHOT`. It polls until `UPDATE_SHOT` clears. Move operations program `MV_NUM_POS` and `MV_SIZE`; core mapping writes `VCAP_*_IDX` followed by `VCAP_*_MAP`.

Two-step timestamping is FIFO-like. The LAN969x path reads `PTP_TWOSTEP_CTRL`, verifies `PTP_VLD`, checks `PTP_OVFL`, filters TX stamps with `STAMP_TX`, decodes `STAMP_PORT`, reads delay/id words from `PTP_TWOSTEP_STAMP_NSEC` and `PTP_TWOSTEP_STAMP_SUBNS`, advances the FIFO with `PTP_NXT`, and matches the timestamp ID against queued SKBs. The Sparx5 REW block exposes parallel `REW_PTP_TWOSTEP_*` registers for the same style of FIFO control.

LAN969x RGMII port configuration is direct. `lan969x_rgmii.c` enables RX/TX with `DEVRGMII_MAC_ENA_CFG`, programs fixed IFG values through `DEVRGMII_MAC_IFG_CFG`, writes speed selection via `DEVRGMII_DEV_RST_CTRL`, and configures VLAN tag awareness, provider-bridge mode, and tag EtherType with `DEVRGMII_MAC_TAGS_CFG`.

## State and Persistence Behavior

The header keeps no C runtime state. All durable state created by these definitions is hardware state in MMIO registers or hardware memories. Higher-level driver structures, such as `struct sparx5`, `struct sparx5_port`, VCAP admin/cache objects, queued timestamp SKBs, and statistics arrays, decide when to write, read, replay, or clear that hardware state.

Important persistent hardware domains include:

- PCS/port mode state: PCS enable, loopback/test/scrambler options, signal detect controls, 5G/10G/25G device mode bits, and QSGMII/USGMII mux state persist until the port is reconfigured or reset.
- PTP time and pin state: TOD domain enable/freeze/hold, current time registers, pin output waveforms, pin interrupt enables/status, and phase detector configuration affect live timestamping and clock I/O.
- Timestamp FIFO state: `PTP_NXT`/`REW_PTP_TWOSTEP_CTRL_PTP_NXT` consume hardware FIFO entries. Overflow and validity bits are transient diagnostic state and can lose timestamps if the driver cannot drain fast enough.
- Queue and flow-control state: QFWD port enable/urgency, QSYS pause/ATOP/fwd-pressure settings, QSYS calendar slots, QRES watermarks, XQS queue-limit sharing, and RAM initialization flags directly control live packet scheduling, drops, pause generation, and queue accounting.
- QS extraction/injection state: group mode, byte swapping, FIFO readiness, data-present bits, and SOF/EOF/abort writes govern CPU packet ingress/egress paths and can leave partial/in-progress injections if sequencing is wrong.
- Rewriter state: VLAN/PCP/DEI/DSCP rewrite controls and maps are per-port egress behavior. `REW_ES0_CTRL` and `REW_RTAG_ETAG_CTRL` also connect egress ACL/VCAP lookup behavior to rewriter decisions.
- VCAP state: entry, mask, action, counter, type-group cache words are staging storage; `UPDATE_SHOT` commits or reads a row in ES0, ES2, or SUPER VCAP memories. Entry/action/counter disable fields define which portions of the row participate in the operation.
- Statistics state: XQS counters wrap or clear based on `XQS_STAT_CFG`; `STAT_CLEAR_SHOT` can reset observed counters for the selected view. The driver mirrors these into software 64-bit accumulators.
- LAN969x RGMII state: speed select, MAC enable, IFG, tag-awareness, and EtherType choices affect the external RGMII datapath until changed.

Many field widths and counts are dynamic. For example, PTP pin count, QSYS pause register count, REW port count, XQS statistic view width, and queue-limit field widths come from `sparx5_regs` tables. This state indirection is what lets the same generated macros operate on Sparx5 and LAN969x variants.

## Dependencies and Integration Points

This chunk depends on Linux bitfield helpers (`BIT`, `GENMASK`, `FIELD_PREP`, `FIELD_GET`) and Sparx5-specific field helpers for dynamic masks. It depends on the `__REG` expansion convention and on `struct sparx5_regs`, which supplies target bases, group counts, register counts, widths, and field positions/sizes. Device-specific tables in `sparx5_regs.c` and `lan969x/lan969x_regs.c` provide different values for the same symbolic registers.

Key integration points in the source tree are:

- `sparx5_port.c`: port muxing, device switching, pause/ATOP setup, QFWD port enable/urgency, flow-control pressure, PCP/DEI map programming, DSCP rewrite enablement, and device-mode bit selection.
- `sparx5_fdma.c`: QS extraction/injection mode, CPU port setup, and QFWD enablement for internal CPU ports.
- `sparx5_calendar.c`: QSYS auto calendar programming and calendar error detection.
- `sparx5_ethtool.c`: XQS statistic view selection, queue counter reads, and queue-stat clear shots.
- `sparx5_vcap_impl.c`: VCAP ES0/ES2/SUPER cache read/write, initialization, move, core mapping, and update-shot polling.
- `sparx5_vcap_impl.h` and `sparx5_vcap_debugfs.c`: ES0/ES2 key-selection enum names and debug presentation that complement `REW_RTAG_ETAG_CTRL` and EACL key-selection registers from adjacent chunks.
- `lan969x/lan969x.c`: LAN969x PTP timestamp FIFO polling and TX SKB matching.
- `lan969x/lan969x_rgmii.c`: RGMII MAC enablement, IFG, speed, and VLAN tag awareness setup.
- `sparx5_main.c`: RAM initialization sequencing for VCAP/QSYS/VOP-style RAM control registers.

## Risks and Edge Cases

- Register layout drift is high impact. A wrong target, group base, group width, register offset, instance count, or field mask can silently program the wrong MMIO word or corrupt unrelated hardware bits.
- The chunk starts mid-`PCS25G_BR_PCS_CFG` at line 6023. Any final per-file report must merge with the previous chunk to describe the full 25G PCS register without losing fields defined just before this range.
- Device-family comments matter. Sparx5-only definitions such as 25G PCS or REW two-step PTP registers must not be used on LAN969x, and LAN969x-only PTP/RGMII definitions must be gated by family-specific code.
- Dynamic masks rely on `regs->fsize` and `regs->fpos`. If the per-family register tables are wrong, macros such as PTP pin fields, XQS statistic view, QRES watermarks, QSYS pause/ATOP, and frame-copy port fields will compile but access incorrect bits.
- `spx5_rmw()` is a plain read-modify-write against MMIO. Callers touching the same register from different contexts need external serialization when fields can be updated concurrently.
- VCAP update operations are stateful and require polling `UPDATE_SHOT` to clear. Issuing another operation while a shot is active, using the wrong entry/action/counter disable bits, or forgetting to clear/cache-fill staging registers can corrupt VCAP rows or counters.
- VCAP cache masks are represented in hardware cache words and some code reads masks with inversion. Tests must distinguish the logical rule mask from the hardware cache encoding.
- QSYS calendar programming can fail with `CAL_AUTO_ERROR`; ignoring that bit can leave the switch core with invalid scheduling for the active port bandwidth mix.
- QSYS/XQS threshold fields are encoded watermarks, not necessarily raw bytes or frames. Incorrect unit conversion in callers can cause premature pause, tail drop, queue starvation, or buffer overrun.
- XQS stats are view-based and clear-shot based. Reading without holding the driver mutex, selecting the wrong view, or clearing while another reader is accumulating software counters can produce inconsistent ethtool statistics.
- QS injection control requires correct SOF/EOF/valid-byte sequencing. Misuse of abort, gap size, or FIFO readiness can create truncated CPU-injected frames or stuck injection state.
- Two-step timestamp FIFO consumption is destructive. `PTP_NXT` advances entries; continuing after an invalid entry, ignoring overflow, or failing to match the expected TX/RX ID pair can lose hardware timestamps and leak or timeout queued SKBs.
- `REW_PTP_RSRV_NOT_ZERO*` definitions indicate reserved words that must be handled carefully if written. Treating them as normal zeroable registers can violate hardware requirements.
- RGMII configuration is LAN969x-specific and uses only a subset of DEV1G controls in this chunk. Speed select, IFG, and VLAN awareness must remain consistent with delay-line and port-mode code elsewhere in `lan969x_rgmii.c`.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Build coverage for Sparx5 and LAN969x configurations to ensure every generated macro expands with valid `sparx5_regs` table entries and no stale target/count identifiers.
- Port bring-up tests across 1G/2.5G/5G/10G/25G modes, including mode switches through `PORT_CONF_DEV*`, PCS signal-detect polarity/source changes, QSGMII/USGMII quad mode, link up/down, and traffic after speed changes.
- Flow-control tests that verify QSYS pause start/stop, ATOP thresholds, forwarding pressure disable/enable, pause frame generation, aggressive tail-drop behavior, and no regression in per-port queue drops.
- QSYS calendar tests that exercise bandwidth combinations near target/core limits, verify `CAL_AUTO_ERROR` stays clear, and validate traffic scheduling after calendar reprogramming.
- FDMA and CPU packet I/O tests that cover QS extraction/injection group mode, byte swapping, status-word placement, FIFO ready/data-present bits, SOF/EOF/abort handling, and CPU port QFWD enablement.
- Ettool/statistics tests that read XQS per-priority forward/drop/tx counters, clear selected views with `STAT_CLEAR_SHOT`, verify software counter accumulation across wrap, and check concurrent readers under `queue_stats_lock`.
- PTP tests for TOD domain enable/freeze/hold, current time reads, pin waveform generation, pin interrupts, phase detector enable/failure handling, two-step TX timestamp FIFO drain, overflow reporting, and TX SKB timestamp matching on LAN969x and Sparx5 paths.
- VCAP tests for ES0, ES2, and SUPER initialization, rule add/update/delete, cache readback, move operations, counter-only updates, core mapping, row-deleted sticky bits, and timeout behavior when `UPDATE_SHOT` fails to clear.
- Rewriter tests for VLAN PCP/DEI/VID defaults, PCP/DEI map programming for both drop precedence values, tag-control modes, DSCP update/remap enablement, ES0 lookup enablement, and interaction with VCAP egress actions.
- RAM initialization tests that verify QSYS, REW, VCAP SUPER, and VOP RAM init bits are written in the expected boot/reset sequence and do not race with active table programming.
- LAN969x RGMII tests for MAC RX/TX enablement, speed select, IFG values, VLAN tag awareness for no-tag/single-tag/double-tag modes, custom EtherType handling, and traffic at each supported RGMII speed.
