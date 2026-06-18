# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_pcol.h lines 15706-17204

## Chunk Scope

This chunk is the final range of the Siena copy of the Solarflare/Xilinx SFC
MCDI protocol header. It is generated ABI material rather than executable C:
the file defines Management Controller Diagnostic Interface command IDs,
privilege categories, request/response sizes, field offsets, bit positions,
array length helpers, and enum values. Driver code uses these constants through
the `MCDI_*` accessor macros when composing firmware RPC payloads and parsing
firmware responses.

The range starts with the tail of `MC_CMD_RSS_CONTEXT_GET_FLAGS` output flags,
then covers vPort MAC/VLAN management, EVB port query, clock and interrupt
commands, shmboot/offline BIST/PSU/fuse diagnostics, classic and V3 licensing,
parser-dispatcher configuration, port-mode and workaround queries, privilege
and VF link-state controls, tunnel encapsulation UDP port programming, VNIC
encapsulation rules, and final generic function/personality structures before
the header guard closes.

## Purpose and Responsibilities

- Publish the wire layout for late MCDI commands used by EF10/Medford-era and
  later SFC driver code while preserving the legacy Siena source-tree copy.
- Give host code stable symbolic names for command numbers such as
  `MC_CMD_GET_FUNCTION_INFO`, `MC_CMD_LICENSING_V3`,
  `MC_CMD_SET_TUNNEL_ENCAP_UDP_PORTS`, `MC_CMD_PRIVILEGE_MASK`, and
  `MC_CMD_VNIC_ENCAP_RULE_ADD`.
- Encode SR-IOV privilege requirements with `MC_CMD_0x*_PRIVILEGE_CTG`
  definitions, separating general commands from admin and insecure operations.
- Define variable-length payload calculations for arrays of MAC addresses,
  fuse bytes, license IDs, licensed-app arguments/results, parser-dispatcher
  values, and tunnel encapsulation entries.
- Preserve cross-version protocol compatibility: for example RSS context flags
  expose both old `_EN` bits and newer `_RSS_MODE` fields, licensing exposes
  both pre-V3 and V3 commands, and several responses provide MCDI2 larger
  maximum lengths.

## Important APIs, Types, and Constants

- RSS context flags:
  `MC_CMD_RSS_CONTEXT_GET_FLAGS_OUT_FLAGS_*` defines four legacy Toeplitz
  enable bits and six 4-bit mode fields for TCP/UDP/other over IPv4/IPv6. The
  comment establishes the compatibility rule: new drivers should trust the
  `_RSS_MODE` fields, while old enable bits remain consistent for fresh
  contexts and old-style SET operations.
- vPort MAC and VLAN operations:
  `MC_CMD_VPORT_ADD_MAC_ADDRESS`, `MC_CMD_VPORT_DEL_MAC_ADDRESS`, and
  `MC_CMD_VPORT_GET_MAC_ADDRESSES` operate on a 32-bit vPort handle and 6-byte
  MAC addresses. `GET_MAC_ADDRESSES_OUT` is variable length, with 41 legacy
  entries or 169 MCDI2 entries. `MC_CMD_VPORT_RECONFIGURE` can replace VLAN
  tags and/or up to four MAC addresses on an existing vPort and reports
  `RESET_DONE` if firmware reset the vPort user before applying changes.
- EVB, function identity, clocks, and interrupts:
  `MC_CMD_EVB_PORT_QUERY` returns vPort flags and available VLAN tag count.
  `MC_CMD_GET_CLOCK` returns system and DPCPU frequencies in MHz.
  `MC_CMD_TRIGGER_INTERRUPT` asks firmware to prod a BIU interrupt level
  relative to the function base. `MC_CMD_GET_FUNCTION_INFO` reports PF and VF
  indexes for the calling function.
- Admin, insecure, and diagnostic controls:
  `MC_CMD_SHMBOOT_OP` supports shmboot operations such as pushing Greenport
  slave data. `MC_CMD_ENABLE_OFFLINE_BIST` enters a destructive offline BIST
  mode where queues are torn down and the only exit is reboot.
  `MC_CMD_SET_PSU`, `MC_CMD_READ_FUSES`, and `MC_CMD_FUSE_DIAGS` are marked
  insecure and expose voltage rail programming, OTP fuse reads, and fuse
  mismatch/checksum diagnostics.
- Licensing:
  `MC_CMD_LICENSING` reports classic license key counts and self-test status.
  `MC_CMD_LICENSING_V3` reports V3 key counts, private diagnostic state,
  self-test status, and 64-bit licensed application/feature masks.
  `MC_CMD_LICENSING_GET_ID_V3` returns license type plus a variable-length
  unique license ID. `MC_CMD_GET_LICENSED_APP_STATE`,
  `MC_CMD_GET_LICENSED_V3_APP_STATE`, and
  `MC_CMD_GET_LICENSED_V3_FEATURE_STATES` query current application or feature
  state, with explicit notes that update-license operations or MC reboot can
  invalidate cached state.
- Licensed app operations:
  `MC_CMD_LICENSED_APP_OP` is the classic extensible app operation wrapper with
  validate and mask variants. `MC_CMD_LICENSED_V3_VALIDATE_APP` validates a V3
  app using a 48-byte challenge and returns a 96-byte ECDSA signature, expiry
  information, base NIC MAC address, and current vAdaptor MAC address.
  `MC_CMD_LICENSED_V3_MASK_FEATURES` is an admin command for masking licensed
  features on or off. `MC_CMD_LICENSING_V3_TEMPORARY` installs, clears, or
  polls a temporary V3 license that survives MC reboot but is erased by power
  cycle.
- Parser-dispatcher and port modes:
  `MC_CMD_SET_PARSER_DISP_CONFIG` and `MC_CMD_GET_PARSER_DISP_CONFIG` update
  or read settings keyed by type and entity, including TXQ multicast UDP
  destination lookup and vAdaptor self-TX suppression. `MC_CMD_GET_PORT_MODES`
  returns production/default/current port modes, and V2 adds engineering modes.
  `MC_CMD_OVERRIDE_PORT_MODE` stores an admin override in persistent DMEM for
  subsequent warm MC reboots, with cold reboot clearing the override.
- Workarounds and privileges:
  `MC_CMD_GET_WORKAROUNDS` returns implemented and enabled workaround bitmasks
  for hardware/firmware bug IDs. `MC_CMD_PRIVILEGE_MASK` reads or conditionally
  sets a function's privilege mask when `DO_CHANGE` is present, covering admin,
  link, Onload, PTP, filtering, spoofing, MAC-change, unrestricted VLAN,
  insecure, and TSA-unbound admin groups. `MC_CMD_PRIVILEGE_MODIFY` applies add
  and remove masks to groups of PCIe functions. `MC_CMD_LINK_STATE_MODE`
  reads/sets VF link mode as auto, forced up, forced down, or read-only.
- Tunnel encapsulation:
  `TUNNEL_ENCAP_UDP_PORT_ENTRY` packs a 16-bit UDP port and 16-bit protocol
  selector, with standard VXLAN (`0x12b5`) and Geneve (`0x17c1`) values.
  `MC_CMD_SET_TUNNEL_ENCAP_UDP_PORTS` programs up to 16 entries, can unload
  the parser configuration, and reports whether firmware is resetting
  functions as a consequence.
- VNIC encapsulation rules:
  `MC_CMD_VNIC_ENCAP_RULE_ADD` defines per-VNIC encapsulation detection rules
  for RX checksum validation and inner-packet parsing. Match bits cover
  ethertype, outer VLAN, destination IP, IP protocol, and destination port.
  Fields store network-order IPv4/IPv6 ethertype/IP/port data, optional outer
  VLAN VID, a strip-outer-VLAN action bit, and a MAE encapsulation type. The
  output handle is later passed to `MC_CMD_VNIC_ENCAP_RULE_REMOVE`.
- Final structure definitions:
  `FUNCTION_PERSONALITY` stores a 32-bit personality ID for EF100, virtio-net,
  virtio-blk, acceleration management, and acceleration user functions.
  `PCIE_FUNCTION` stores an 8-byte interface/PF/VF tuple with wildcard and
  null sentinels plus host/AP interface selectors.

## Control Flow and Protocol Flow

This header chunk has no C branches or call graph. Runtime control flow is
encoded as firmware command sequences invoked through `efx_mcdi_rpc()` and
related quiet variants.

- vPort MAC discovery/update flow builds an input payload with the vPort ID,
  sends `VPORT_GET_MAC_ADDRESSES` to learn current MACs, and bounds response
  parsing by both `outlen` and `MACADDR_COUNT`. Adding a MAC uses
  `VPORT_ADD_MAC_ADDRESS`; full replacement uses `VPORT_RECONFIGURE`, after
  which callers must handle possible function reset indicated by
  `RESET_DONE`.
- Function initialization flow commonly calls `GET_FUNCTION_INFO` early to
  determine PF/VF identity. The main SFC tree consumes this in `ef10.c`,
  `mcdi.c`, and `mcdi_functions.c` to populate PF/VF indexes and to handle
  firmware that may not support the command.
- Licensing flow starts with `LICENSING` or `LICENSING_V3` reporting installed
  key/app/feature state. `LICENSING_V3` can return `EAGAIN` while update
  processing is in progress. Individual app/feature state commands then query
  masks, and validation commands exchange challenge/response payloads. Temporary
  license installation is explicitly asynchronous: send SET, then poll STATUS
  until OK, IN_PROGRESS, or ERROR.
- Parser and tunnel flow programs parser-dispatcher state before traffic
  depends on it. `SET_TUNNEL_ENCAP_UDP_PORTS` builds an entries array and may
  trigger function resets; driver code must treat the `RESETTING` output flag
  as a synchronization signal rather than assuming the configuration is a
  local-only update.
- Privilege and VF link management flow addresses target PCIe functions by
  packed PF/VF fields. `PRIVILEGE_MASK` can be read-only or write depending on
  the MSB in `NEW_MASK`; `PRIVILEGE_MODIFY` applies bulk changes to groups.
  `LINK_STATE_MODE` uses `DO_NOT_CHANGE` for read-only queries and otherwise
  writes VF-visible link state policy.
- Workaround flow reads firmware-implemented and enabled masks. The main SFC
  tree uses this to toggle driver behavior for unsafe EVQ writes, broken EVQ
  timer writes, multicast filter chaining, and older firmware that lacks the
  command.
- VNIC encapsulation flow first discovers supported match combinations through
  the parser-dispatcher information command defined earlier in the header, then
  adds non-overlapping rules. Returned handles are the only remove keys, so the
  driver must persist them for cleanup.

## State and Persistence Behavior

- vPort MAC/VLAN configuration is firmware-owned state tied to vPort handles.
  `VPORT_RECONFIGURE` can reset the vPort's user function, so state changes may
  have broader device-visible effects than a local table update.
- Licensing state lives in firmware and NVRAM license partitions. V3 reports
  aggregate key/app/feature masks, but command comments make clear that cached
  app/feature states can be invalidated by license update operations or MC
  reboot. Temporary V3 licenses are stored in MC persistent data, survive MC
  reboot, and are erased on adapter power cycle or explicit clear.
- `OVERRIDE_PORT_MODE` stores override data in the persistent section of DMEM
  and activates it on next warm MC reboot. Cold reboot clears it, and the
  override does not change PF configuration, so invalid port/PF mappings remain
  a host/firmware integration risk.
- Fuse data and fuse diagnostics expose OTP and hardware-programmed state.
  Reads are bounded by requested offset/length and response maximums, while
  diagnostics summarize mismatched or unexpectedly clear bits across fuse
  areas.
- Privilege masks and VF link-state modes are firmware policy state for target
  PCIe functions. Admin functions may observe all privileges, while secure
  adapters can still reject insecure command groups regardless of mask bits.
- Tunnel encapsulation UDP port mappings and VNIC encapsulation rules configure
  parser/VNIC hardware state. Tunnel port programming is global enough to cause
  all functions to see a reset, whereas VNIC encapsulation rules are per-driver
  or per-VNIC and have finite table capacity.
- `FUNCTION_PERSONALITY` and `PCIE_FUNCTION` are reusable value encodings, not
  persistent state by themselves; they are embedded in other MCDI protocols for
  function allocation, discovery, and device personality selection.

## Dependencies and Integration Points

- `mcdi.h` is the immediate consumer layer: its `MCDI_DECLARE_BUF`,
  `MCDI_SET_DWORD`, `MCDI_POPULATE_DWORD_*`, `MCDI_DWORD`,
  `MCDI_QWORD`, `MCDI_PTR`, and `MCDI_ARRAY_*` helpers concatenate field names
  from this header with `_OFST`, `_LEN`, `_LBN`, and `_WIDTH`.
- The main SFC `ef10.c` consumes several definitions from this exact range:
  `GET_FUNCTION_INFO` for PF/VF identity, `LICENSING_V3` for licensed feature
  masks, `GET_CLOCK` for system clock frequency, `VPORT_GET_MAC_ADDRESSES` and
  `VPORT_ADD_MAC_ADDRESS` for vPort MAC handling, workaround bits, and
  `SET_TUNNEL_ENCAP_UDP_PORTS` for VXLAN/Geneve parser offload.
- `mcdi.c` consumes `GET_WORKAROUNDS` and `GET_FUNCTION_INFO`, including
  response length checks and tolerance for older firmware returning
  unsupported-command errors.
- `ef10_sriov.c` consumes `LINK_STATE_MODE` to set or query VF link state,
  using packed PF/VF bitfields and the `DO_NOT_CHANGE` read-only sentinel.
- The VNIC encapsulation rule commands refer to definitions outside this range,
  especially `MAE_MPORT_SELECTOR_ASSIGNED`, `MAE_MCDI_ENCAP_TYPE`, and
  `MC_CMD_GET_PARSER_DISP_INFO` supported-match queries defined earlier in the
  protocol header.
- Privilege categories such as `SRIOV_CTG_GENERAL`, `SRIOV_CTG_ADMIN`,
  `SRIOV_CTG_INSECURE`, and `SRIOV_CTG_ADMIN_TSA_UNBOUND` are defined earlier
  and are used by firmware-side authorization plus host tooling that reasons
  about command availability.
- The Siena subtree carries this protocol copy for compatibility, but not every
  late EF10/Medford/EF100 command is actively used by Siena-specific C files.
  Keeping the ABI in sync still matters because shared code and generated
  protocol tooling can include the Siena header copy.

## Risks and Edge Cases

- This is a firmware ABI. Any changed command number, length, offset, enum
  value, or bit position can create silent host/firmware disagreement and corrupt
  MCDI messages.
- Several response layouts are variable length and have different legacy MCDI
  versus MCDI2 maxima. Callers must validate `outlen`, count fields, and array
  calculations before copying MACs, fuse bytes, license IDs, parser values, or
  tunnel entries.
- Some comments document destructive behavior: `ENABLE_OFFLINE_BIST` tears down
  queues and requires reboot; `VPORT_RECONFIGURE` can reset a function;
  `SET_TUNNEL_ENCAP_UDP_PORTS` can reset all functions; port-mode override only
  activates after warm MC reboot. Treating these as ordinary configuration RPCs
  risks data-path disruption.
- Insecure commands are marked separately and may be rejected on secure
  adapters independent of privilege masks. Callers should not assume that
  `GRP_INSECURE` privilege is sufficient on secure hardware.
- Licensing V3 has asynchronous and invalidation cases. `REPORT_LICENSE` may
  return `EAGAIN`, temporary license SET needs status polling, and app/feature
  state can become stale after update or reboot.
- Network-byte-order fields in VNIC encapsulation rules and tunnel entries must
  be populated consistently. The 12-bit outer VLAN field has both a deprecated
  bit offset and an aligned word wrapper; using the wrong helper can shift the
  VID incorrectly.
- Encapsulation rule overlap is explicitly caller-managed. Firmware may choose
  a random matching rule when overlaps exist, duplicate matches return
  `EALREADY`, unsupported match combinations return `EOPNOTSUPP`, and full
  per-driver tables return `ENOSPC`.
- `PRIVILEGE_MASK` uses the MSB of `NEW_MASK` as the write-enable bit. A caller
  that forgets `DO_CHANGE` will only read, while a caller that accidentally sets
  it can alter privileges.
- `GET_WORKAROUNDS` must tolerate older firmware. The main driver already
  treats absence of the command as non-fatal, so tests should preserve that
  behavior when changing workaround handling.

## Test Signals

- Compile coverage is the primary signal for this generated header: all users
  of `MCDI_*` helper names must still find matching `_OFST`, `_LEN`, `_LBN`,
  and `_WIDTH` macros.
- Unit or static-build checks should cover representative MCDI payloads for
  `GET_FUNCTION_INFO`, `VPORT_GET_MAC_ADDRESSES`, `LICENSING_V3`,
  `LINK_STATE_MODE`, and `SET_TUNNEL_ENCAP_UDP_PORTS`, especially response
  length checks and variable array sizing.
- Runtime smoke tests on supported EF10/Medford hardware should include
  firmware RPC success/failure paths for function identity, clock read, license
  report, workaround query, vPort MAC enumeration, VF link-state query/set, and
  tunnel encapsulation programming where available.
- Negative tests should exercise older firmware or simulated unsupported MCDI
  results for `GET_WORKAROUNDS`, `GET_FUNCTION_INFO`, licensing update in
  progress, unsupported VNIC match flags, duplicate encapsulation rules, full
  rule tables, and secure-adapter rejection of insecure commands.
- Reset-sensitive tests should verify that callers recover when
  `VPORT_RECONFIGURE` reports `RESET_DONE` or tunnel UDP port programming
  reports `RESETTING`.
- ABI regression tests can compare generated offsets, lengths, and command IDs
  against firmware protocol sources, with particular attention to packed PF/VF
  fields, 64-bit app/feature masks, MCDI2 maximum response sizes, and final
  `PCIE_FUNCTION` tuple layout.
