# sources/distributed-fs/ceph-client/drivers/thunderbolt/tb_msgs.h

## Purpose
`tb_msgs.h` defines the packed wire/control-channel message layouts used by Thunderbolt configuration transactions, Intel Connection Manager firmware messages, USB4 router operation proxy messages, and XDomain protocol packets. It is a protocol contract header: it carries no executable logic, but every field definition affects how packets are built, parsed, acknowledged, and routed.

## Important APIs, Types, and Functions
- `enum tb_cfg_space` identifies Thunderbolt config spaces: hops, port, switch, and counters.
- `enum tb_cfg_error` defines control-channel error and notification codes, including hotplug acknowledgement, DP bandwidth, router operation completion, PCIe wake, DP connection change, DPTX discovery, link recovery, and asymmetric link notifications.
- `struct tb_cfg_header`, `struct tb_cfg_address`, `struct cfg_read_pkg`, `struct cfg_write_pkg`, `struct cfg_error_pkg`, `struct cfg_ack_pkg`, `struct cfg_event_pkg`, and `struct cfg_reset_pkg` define base config-channel packet formats.
- `enum icm_pkg_code`, `enum icm_event_code`, `struct icm_pkg_header`, and ICM flag masks define the common Intel firmware message envelope.
- Falcon Ridge, Alpine Ridge, Titan Ridge, Ice Lake, and USB4 ICM structures define generation-specific driver-ready, topology, device connect/disconnect, XDomain, approval, key, challenge, boot ACL, RTD3 veto, and USB4 switch-op messages.
- XDomain packet definitions include `struct tb_xdomain_header`, `enum tb_xdp_type`, `struct tb_xdp_header`, UUID/property/link-state request and response structures, maximum property sizes, and `enum tb_xdp_error`.

## Control Flow
The control channel code uses the config packet structures to issue config-space reads/writes and to receive asynchronous events. `tb.c` consumes `struct cfg_event_pkg` in `tb_handle_event()` for plug/unplug events, and consumes `struct cfg_error_pkg` in `tb_handle_notification()` for notification-style errors such as DP bandwidth changes. Hotplug events are acknowledged with `TB_CFG_ERROR_ACK_PLUG_EVENT` semantics through the control helpers.

Firmware-managed domains use the ICM package definitions to negotiate driver readiness, fetch topology, approve devices, challenge devices with keys, manipulate preboot ACLs, approve or disconnect XDomains, receive device/XDomain events, and proxy USB4 router operations. Hardware generation differences are represented by separate `icm_fr_*`, `icm_ar_*`, and `icm_tr_*` structures because fields such as route, UUID, connection ID/key, security flags, and topology payloads differ across controllers.

XDomain services use the XDP structures to exchange UUIDs, properties, property-change notifications, and link-state status/change messages over DMA paths between host domains. The `length_sn` field combines length and sequence number bits; typed packet payloads then follow a common UUID/type header.

## State and Persistence Behavior
This header defines transient packet formats and constants only. It stores no persistent runtime state. Persistence is external: ICM firmware may keep ACLs, connection keys, topology state, and approval state; the Linux driver stores parsed results in `struct tb_switch`, `struct tb_xdomain`, and domain data structures defined elsewhere.

The packed structures are stateful only in the sense that they are ABI contracts. Any value written to a field is interpreted by hardware firmware, the control channel, or a peer domain according to these layouts.

## Dependencies and Integration Points
The header depends on `linux/types.h` and `linux/uuid.h`, and uses bit macros such as `BIT()` and `GENMASK()` from the broader kernel include environment. It integrates with `ctl.h` and control-channel transaction code, ICM implementation files, USB4 switch operation proxying, XDomain services, and the software CM's event path in `tb.c`.

The `tb_cfg_space` and packet structures pair with register definitions in `tb_regs.h`: config read/write packets select the config space and offsets of the register layouts defined there. ICM USB4 switch-op messages carry opcodes that correspond to USB4 router operation constants in `tb_regs.h`.

## Risks
- The structures are `__packed` and use C bitfields. Endianness, compiler bitfield layout assumptions, and ABI changes are high-risk for hardware protocol correctness.
- Multiple controller generations use similar but not identical messages. Accidentally parsing an Alpine Ridge or Titan Ridge event with the wrong structure would corrupt route, UUID, or connection fields.
- `cfg_write_pkg::data` has a fixed 64 dword maximum while `tb_regs.h` notes a smaller practical config frame limit. Callers must still respect control-channel length limits.
- XDomain property responses have variable-length trailing data and a maximum total property size. Length validation is critical before parsing.
- Error enum values include both failures and asynchronous notifications. Treating notification-style errors as fatal transaction errors would break hotplug, DP bandwidth changes, and wake handling.

## Test Signals
Protocol tests should verify structure sizes and offsets against the Thunderbolt/USB4/ICM specifications, especially packed bitfield fields. Runtime tests should cover config read/write round trips, hotplug event acknowledgement, DP bandwidth notification acknowledgement and queued handling, ICM driver-ready/topology parsing on each supported generation, device approval/challenge/key messages, boot ACL transfer, USB4 switch operation proxy messages, XDomain UUID/property/link-state request-response sequences, and rejection of malformed lengths or unknown XDP packet types.
