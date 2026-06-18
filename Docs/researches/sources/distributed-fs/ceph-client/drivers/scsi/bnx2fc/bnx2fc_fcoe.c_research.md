# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_fcoe.c

## Purpose

`bnx2fc_fcoe.c` is the lifecycle and integration core of the driver. It registers the FCoE transport and CNIC ULP callbacks, creates/destroys FCoE controllers over bnx2x netdevs, configures libfc/libfcoe and SCSI hosts, handles FIP/FCoE L2 transmit and receive, responds to netdev events, manages NPIV vports, starts/stops firmware, and owns global HBA/interface lists and templates.

## Important APIs, Types, and Functions

Major entry points include `bnx2fc_mod_init()`, `bnx2fc_mod_exit()`, CNIC callbacks (`bnx2fc_ulp_init/exit/start/stop`, `bnx2fc_indicate_netevent()`), FCoE transport operations (`bnx2fc_create()`, `bnx2fc_destroy()`, `bnx2fc_enable()`, `bnx2fc_disable()`, `bnx2fc_ctlr_alloc()`, `bnx2fc_match()`), and SCSI/FC/libfc templates. Helpers include `bnx2fc_xmit()`, `bnx2fc_rcv()`, `bnx2fc_l2_rcv_thread()`, `bnx2fc_recv_frame()`, `bnx2fc_percpu_io_thread()`, `bnx2fc_get_host_stats()`, `bnx2fc_net_config()`, `bnx2fc_interface_setup()`, `bnx2fc_hba_create()`, `bnx2fc_interface_create()`, `bnx2fc_if_create()`, `bnx2fc_fw_init()`, and `bnx2fc_fw_destroy()`.

## Control Flow

Module init attaches FCoE/FC transports, allocates workqueues, starts a global L2 receive thread, registers CPU hotplug callbacks for per-CPU completion threads, and registers with CNIC. CNIC init creates HBAs for supported bnx2x-class devices. Controller creation validates fabric FIP mode and bnx2x backing netdev, creates an interface/FIP controller, registers packet handlers, creates an lport/SCSI host, configures libfc/exchange manager, and starts discovery.

Firmware start allocates DMA resources, sends FCoE init KWQEs, waits for `ADAPTER_STATE_UP`, and marks firmware initialized. Transmit routes selected ELS for offloaded sessions through firmware and encapsulates other frames as Ethernet FCoE. Receive validates FCoE frames, MACs, vports, source FCF, CRC, and drops unsupported FCP data/ABTS before `fc_exch_recv()`. Netdev events update link state, libfcoe state, FC port types, queues, and wait for session upload.

## State and Persistence Behavior

Global state includes `adapter_list`, `if_list`, `adapter_count`, `bnx2fc_dev_lock`, `bnx2fc_wq`, `bnx2fc_global`, per-CPU `bnx2fc_percpu`, and transport templates. Per-HBA, per-interface, lport, vport, packet-handler, and workqueue state persists until teardown. Firmware/link state uses `BNX2FC_FLAG_FW_INIT_DONE`, `ADAPTER_STATE_UP`, `ADAPTER_STATE_READY`, and link-down/going-down bits.

## Dependencies and Integration Points

The file integrates with libfcoe sysfs/transport, libfc exchange/discovery/FCP, SCSI host registration, FC transport attributes, CNIC ULP APIs, bnx2x netdev/ethtool metadata, Linux packet handlers, VLAN helpers, CPU hotplug, kthreads, workqueues, timers, and hardware resource setup in `bnx2fc_hwi.c`.

## Risks and Edge Cases

Lock ordering with RTNL, CNIC, and `bnx2fc_dev_lock` is delicate. `bnx2fc_destroy()` derives `ctlr` before checking `interface`, which would be unsafe on NULL lookup. Link-down waits can be interrupted. Receive path does not check `skb_linearize()` return. Creation has many staged resources requiring exact cleanup. CPU hotplug can process work while target teardown is active.

## Test Signals

Test module/CNIC lifecycle, controller create/destroy on VLAN and non-VLAN netdevs, link up/down with session upload, FIP discovery/FLOGI, L2 CRC/MAC/drop paths, NPIV create/delete/disable including NVRAM entries, host stats, `tm_timeout`, CPU hotplug during completions, and teardown with pending skbs/sessions.
