# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_pci.c

## Purpose
`fbnic_pci.c` is the driver entry/lifecycle module. It registers the PCI driver, maps BARs, allocates device/devlink/netdev resources, initializes firmware and MAC hardware, owns service work, handles suspend/resume/shutdown, and participates in PCI error recovery.

## Important APIs, Types, And Functions
Externally used helpers include `fbnic_rd32()`, `fbnic_fw_present()`, `fbnic_fw_wr32()`, `fbnic_fw_rd32()`, `fbnic_up()`, `fbnic_down_noidle()`, and `fbnic_down()`. PCI callbacks are `fbnic_probe()`, `fbnic_remove()`, suspend/resume helpers, shutdown, and AER handlers. Service functions include `fbnic_service_task()`, `fbnic_health_check()`, and `fbnic_fw_config_after_crash()`.

## Control Flow
Module init initializes debug support and registers the PCI driver. Probe enables the device, configures DMA mask, maps BAR0/BAR4, allocates devlink state, creates health reporters, sets queue limits and pause storm default, saves PCI state, allocates IRQs, initializes MAC registers, initializes firmware logging/mailbox, registers devlink/debug/hwmon, snapshots stats, creates MDIO, allocates netdev, sets up PTP, and registers netdev. Some late failures enter init-failure mode but return success so devlink remains available for firmware remediation.

`fbnic_up()` enables rings, fills RX buffers, writes RSS/filter state, enables NAPI, wakes TX queues, starts service work, and initializes debug NAPI entries. Down paths stop service work, disable NAPI/TX, clear RX rules, disable RSS and rings, wait for idle when requested, and flush descriptors. The service task runs under RTNL after initial phylink training notification, updates stats, handles pause storm, checks firmware heartbeat/health, syncs BMC RPC requests, and triggers depletion checks when carrier is up.

Suspend stops netdev if running, disables firmware log/mailbox/IRQs, and nulls MMIO pointers. Resume restores BAR pointers, IRQs, MAC registers, mailbox/logging, OTP checks, reopens netdev if running, and attaches device/queues. PCI error recovery uses the same suspend/resume/attach pieces around slot reset.

## State And Persistence
Persistent module state includes `fbnic_driver_name`, PCI ID tables, board info, and the registered `pci_driver`. Per-device state includes MMIO pointers, devlink, firmware mailbox/log, IRQs, service delayed work, netdev/PTP/hwmon/debug objects, and hardware stats. All-ones MMIO reads invalidate `uc_addr0/uc_addr4` and detach the netdev to await reset.

## Dependencies And Integration Points
This file is the top-level integration point for devlink, PCI, netdev, phylink, PTP, firmware mailbox/logging, IRQ allocation, hardware stats, debugfs, hwmon, BMC RPC, MAC, and TX/RX modules.

## Risks
Init-failure mode intentionally returns success after late probe failures; callers must tolerate devices with devlink but no netdev. Defensive MMIO read invalidation can cascade into netif detach and later resume/reset recovery. Service work holds RTNL while doing several health/stat/filter actions, so long firmware paths can affect netdev control latency. Suspend/resume unwind ordering must keep mailbox/logging/devlink locks and netdev locks consistent.

## Test Signals
Test probe success and init-failure probe, BAR all-ones read detection, open/down cycles through `fbnic_up()`/`fbnic_down()`, firmware crash recovery after heartbeat loss, suspend/resume with netdev up and down, PCI AER slot reset, module load/unload, and devlink availability after late probe failure.
