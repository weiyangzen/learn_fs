# sources/distributed-fs/ceph-client/net/ncsi/internal.h

## Purpose
This header defines the private NCSI subsystem model: package/channel topology, capabilities, modes, statistics, request tracking, state-machine values, OEM constants, and internal function prototypes shared by the NCSI implementation files.

## APIs, Types, and Functions
Important enums define capability indexes and bit masks (`NCSI_CAP_*`), mode indexes (`NCSI_MODE_*`), Mellanox media bits, and `ncsi_dev_state_*` probe/config/suspend states. OEM constants cover Mellanox, Broadcom, and Intel manufacturer IDs, command IDs, payload lengths, and MAC offsets. Core structs include `ncsi_channel_version`, `ncsi_channel_cap`, `ncsi_channel_mode`, MAC/VLAN filter structs, `ncsi_channel_stats`, `ncsi_channel`, `ncsi_package`, `ncsi_request`, `vlan_vid`, `ncsi_dev_priv`, and `ncsi_cmd_arg`. Prototypes cover device reset, monitor control, topology lookup/allocation, request allocation, command transmission, response receipt, and AEN handling.

## Control Flow
The header has no executable flow, but it encodes the state machine used by `ncsi-manage.c`: probe states enumerate packages/channels and gather version/capability/link data; config states select packages, clear state, program filters, enable TX/channel/AEN, and read link status; suspend states disable TX/channel and optionally deselect packages. The `ncsi_request` flags distinguish event-driven management commands from netlink-driven user commands.

## State and Persistence
`ncsi_dev_priv` is the persistent per-netdev private object. It tracks global flags (`PROBED`, `HWA`, `RESHUFFLE`, `RESET`), discovered packages, active package/channel, pending request count, request ID cursor, queue of channels awaiting config/suspend, packet receive registration, VLAN list, whitelist/multi-package settings, and Mellanox multi-host state. `ncsi_package` persists channel lists, whitelists, preferred channel, UUID, and multi-channel mode. `ncsi_channel` persists capabilities, modes, filters, statistics, monitor timer state, and active/inactive/invisible state.

## Dependencies and Integration
The header depends on kernel networking types, generic netlink request metadata, timers, spinlocks, lists, and the public `struct ncsi_dev`. It is included by command, response, AEN, management, and netlink code and forms their shared ABI boundary inside `net/ncsi`.

## Risks
Many fields are shared across IRQ, timer, workqueue, packet receive, and netlink contexts. Correct lock use around `ndp->lock`, package locks, channel locks, RCU list traversal, and request timer state is critical. OEM constants and packet offsets must match vendor firmware formats. State enum values are used by bitmasking major/minor state, so accidental renumbering can break dispatch.

## Test Signals
Compile-time consumers exercise structure visibility. Runtime signals are successful discovery of packages/channels, correct channel state transitions, stable request allocation/freeing, VLAN and MAC filter persistence, and netlink reporting matching internal topology.
