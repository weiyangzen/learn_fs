# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_common.h

## Purpose
Defines the VF common interface between cxgb4vf OS-specific code, SGE code, and firmware/hardware access code. It centralizes chip identity encoding, adapter parameter structures, link state representation, RSS/VF resource models, mailbox logging structures, and prototypes for firmware mailbox operations.

## Important APIs, Types, And Functions
The header defines chip helpers (`CHELSIO_CHIP_CODE`, `CHELSIO_CHIP_VERSION`, `CHELSIO_PCI_ID_VER`, `is_t4()`), firmware length macro `FW_LEN16()`, and public data structures: `t4vf_port_stats`, `link_config`, `dev_params`, `sge_params`, `vpd_params`, `arch_specific_params`, `rss_params`, `rss_vi_config`, `vf_resources`, `adapter_params`, `mbox_cmd`, and `mbox_cmd_log`.

Inline utilities include `is_x_10g_port()`, `mbox_cmd_log_entry()`, `for_each_port`, core-clock conversion helpers, `t4vf_wr_mbox()`, `t4vf_wr_mbox_ns()`, and `hash_mac_addr()`. Function declarations expose the hardware layer implemented primarily in `t4vf_hw.c` and consumed by adapter setup, SGE, MAC/VLAN/RSS operations, and link handling.

## Control Flow
This header has no executable control flow beyond inlines, but it shapes driver initialization. Adapter setup fills `adapter_params`; SGE init reads `params.sge`; port init fills `link_config`; mailbox users call `t4vf_wr_mbox()` or the non-sleeping wrapper; address-filter management uses `hash_mac_addr()` when exact filters are unavailable. The declared functions form the VF lifecycle: wait for readiness, prepare adapter, query resources/SGE/VPD/device/RSS, allocate/enable/free VIs, configure RX mode/MAC filters/RSS, allocate/free queues, and process firmware replies.

## State And Persistence
The state modeled here is per-adapter runtime state stored inside `struct adapter` after including `adapter.h`. It is not persisted externally. The mailbox log is a ring buffer in memory with host-endian command snapshots, jiffies timestamps, sequence numbers, and access/execute times. Link state tracks capabilities, advertised capabilities, peer capabilities, actual speed/FEC/pause, autonegotiation, and link-down reason.

## Dependencies And Integration Points
The header includes PF common `t4_hw.h` and firmware API definitions from `t4fw_api.h`, then includes local `adapter.h`, making it a cross-module contract. Its structures are consumed by `sge.c`, `t4vf_hw.c`, adapter management, ethtool-style statistics, and OS notification hooks such as `t4vf_os_link_changed()`. It also encodes VF-specific constraints such as PF-provisioned SGE parameters and VF resource caps.

## Risks
Because this is a shared contract header, field layout or semantic changes can break multiple compilation units. `hash_mac_addr()` must match hardware inexact-filter hashing. Clock conversion helpers depend on valid `vpd.cclk`. `is_x_10g_port()` and link capability masks assume firmware capability encodings. Mailbox command logging assumes `MBOX_LEN` matches firmware mailbox size expectations.

## Test Signals
Compilation across cxgb4vf files is the first signal. Runtime signals include successful parameter discovery, correct ethtool link reporting, correct MAC hash fallback behavior, stable mailbox debug output, and working T4/T5/T6 probe paths using the same `adapter_params` contract.
