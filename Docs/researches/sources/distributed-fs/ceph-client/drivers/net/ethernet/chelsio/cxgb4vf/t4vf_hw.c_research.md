# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_hw.c

## Purpose
Implements VF firmware/hardware common operations: device readiness, serialized mailbox command transport, adapter/port/resource discovery, SGE parameter queries, BAR2 queue-register mapping, RSS and VI programming, MAC/VLAN ACL/filter commands, statistics collection, queue free commands, link-status interpretation, and asynchronous firmware reply handling.

## Important APIs, Types, And Functions
Core mailbox routines are `t4vf_wait_dev_ready()`, `get_mbox_rpl()`, `t4vf_record_mbox()`, and `t4vf_wr_mbox_core()`. Link capability helpers include `fwcaps16_to_caps32()`, `fwcap_to_cc_pause()`, `fwcap_to_cc_fec()`, `fwcap_to_speed()`, `fwcap_to_fwspeed()`, and `init_link_config()`.

Public hardware APIs include `t4vf_port_init()`, `t4vf_fw_reset()`, `t4vf_set_params()`, `t4vf_fl_pkt_align()`, `t4vf_bar2_sge_qregs()`, `t4vf_get_pf_from_vf()`, `t4vf_get_sge_params()`, `t4vf_get_vpd_params()`, `t4vf_get_dev_params()`, `t4vf_get_rss_glb_config()`, `t4vf_get_vfres()`, RSS VI read/write/range configuration, VI allocate/free/enable/identify, RX mode control, MAC filter allocation/free/change/hash programming, `t4vf_get_port_stats()`, `t4vf_iq_free()`, `t4vf_eth_eq_free()`, `t4vf_update_port_info()`, `t4vf_handle_fw_rpl()`, `t4vf_prep_adapter()`, and VF MAC/VLAN ACL reads.

## Control Flow
Initialization begins with `t4vf_prep_adapter()`, which waits for the VF register aperture, infers chip generation from PCI ID, sets default debug-safe parameters, and records architecture-specific values. Later setup calls parameter discovery routines through mailbox commands. `t4vf_wr_mbox_core()` serializes callers on `adapter->mlist`, waits for the caller to reach the front, verifies driver ownership of the mailbox, writes big-endian firmware command words to VF mailbox data registers, flushes cross-domain writes with readbacks, transfers ownership to firmware, polls with sleep or spin delays, copies replies, logs non-stat commands, and returns negative firmware status.

Port initialization negotiates whether firmware supports 32-bit port capabilities, reads VI information, sets the OS MAC address, optionally reads physical port info when VF read caps allow it, and initializes software link state. Runtime link updates flow through `t4vf_update_port_info()` or asynchronous `t4vf_handle_fw_rpl()`, then `t4vf_handle_get_port_info()` translates firmware fields, detects module/link changes, updates `link_config`, logs link-down reasons, and calls OS notification hooks.

RSS, VI, MAC, and queue helper functions are mostly firmware command builders. They translate host-native structures into firmware command layouts, split large operations where firmware accepts limited entries, and convert replies back into CPU-endian driver state.

## State And Persistence
State is stored in `adapter->params`, `port_info`, the mailbox queue/list/log, VF resource caps, RSS configuration, exact/inexact MAC filter state as known by firmware, and link configuration. The hardware/firmware owns durable state only for the lifetime of the VF or until PF/firmware reset; the driver reconstructs local state during probe/reinit. Mailbox log entries are an in-memory ring useful for debugging recent firmware interactions.

## Dependencies And Integration Points
This file depends on Linux PCI/ethtool headers, Chelsio VF definitions, PF common register/value definitions, and firmware API structs. It is consumed by SGE allocation/free paths, adapter probe/open, ethtool link/stat code, netdev address/RSS/RX-mode operations, and OS callbacks (`t4_os_set_hw_addr()`, `t4vf_os_link_changed()`, `t4vf_os_portmod_changed()`). It also integrates with PF-provisioned VF resources and firmware capability differences across T4/T5/T6.

## Risks
Mailbox serialization and ownership are critical; races or missing flushes can corrupt firmware commands. Several functions assume firmware command ABI limits such as seven params per query/set, 32 RSS table entries per command, and exact MAC command array sizes. Capability translation must correctly handle old 16-bit and new 32-bit firmware formats. BAR2 queue-register calculations are chip and PF-page-layout dependent. Error handling must leave queue/MAC/RSS state consistent when firmware partially accepts operations, especially MAC filter allocation where `-ENOMEM` can still return partial success.

## Test Signals
Strong signals include successful probe against T4, T5, and T6 VFs; mailbox debug logs with sane access/execute timings; correct fallback for old firmware lacking capabilities; successful SGE parameter discovery and BAR2 doorbells; ethtool link/speed/FEC/pause updates; RSS indirection programming; MAC exact/hash fallback behavior; VI allocation/free and RX-mode changes; port statistics reads; and firmware async link event handling.
