# sources/distributed-fs/ceph-client/drivers/thunderbolt/icm.c

## Purpose

`icm.c` implements the firmware-based internal Thunderbolt connection manager. It detects supported Intel controller generations, starts or communicates with ICM firmware, sends ICM command packets over the control channel, handles firmware topology and XDomain events, manages switch authorization and secure keys, coordinates suspend/runtime-resume rescans, exposes boot ACL operations, and proxies selected USB4 router operations including NVM authentication.

## Important APIs, Types, and Functions

`struct icm` is the connection-manager private state embedded after `struct tb`. It stores request serialization, delayed rescan work, optional upstream PCIe port and vendor capability for PCIe2CIO, safe-mode/runtime-PM/NVM-upgrade flags, protocol version, cached asynchronous NVM auth reply, RTD3 veto state, and generation-specific operation pointers.

Transport helpers include `icm_match()`, `icm_copy()`, `icm_request()`, PCIe2CIO helpers (`pcie2cio_read/write()`), and firmware start/reset helpers (`icm_firmware_running()`, `icm_firmware_reset()`, `icm_firmware_start()`, `icm_firmware_init()`, `icm_driver_ready()`).

Generation-specific implementations cover Falcon Ridge (`icm_fr_*`), Alpine Ridge (`icm_ar_*`), Titan Ridge (`icm_tr_*`), Ice Lake (`icm_icl_*`), and newer TGL/ADL/RPL/MTL/Maple Ridge support. Public entry is `icm_probe()`, which returns a populated `struct tb` or `NULL`.

Topology helpers include `alloc_switch()`, `add_switch()`, `update_switch()`, `remove_switch()`, `add_xdomain()`, `update_xdomain()`, and `remove_xdomain()`. Runtime/resume helpers include `icm_unplug_children()`, `icm_free_unplugged_children()`, `icm_rescan_work()`, `icm_complete()`, `icm_runtime_suspend/resume()`, and switch runtime callbacks.

## Control Flow

Probe allocates a domain with ICM private data, initializes the request lock and rescan work, switches on PCI device ID, installs generation-specific private callbacks and `tb_cm_ops`, checks support, and returns the domain to the NHI driver.

Domain add calls `icm_driver_ready()`. It starts firmware if needed, detects safe mode, validates firmware mode, optionally resets physical links via PCIe2CIO, sends `DRIVER_READY`, waits for root switch config access, records security level, protocol version, boot ACL capacity, and runtime-PM support, then later `icm_start()` allocates and adds the root switch.

ICM commands are serialized by `request_lock` and sent as `TB_CFG_PKG_ICM_CMD`; responses are matched by command code and copied by packet id. Notifications are copied into heap work items and processed on the domain ordered workqueue under `tb->lock`.

Device-connected events reconcile existing switches by UUID, route, link/depth, and dual-link physical port. Stale switches or XDomains are removed before new objects are added. Disconnected events remove matching switches or XDomains. XDomain path approval creates DMA tunnels through firmware and emits tunnel activation/deactivation notifications.

Suspend tells firmware the driver unloads and may save devices. Resume marks children unplugged, re-sends driver-ready, accepts firmware's connected events as the new truth, then delayed rescan removes still-unplugged children. RTD3 veto events hold or release a runtime PM reference on the domain.

USB4 proxy operations require protocol version 3. Synchronous operations return metadata/status/data directly. NVM_AUTH is asynchronous: it submits a request with a completion callback, stores the eventual reply in `last_nvm_auth`, and later status polling matches it by route.

## State and Persistence Behavior

Persistent in-kernel state includes the domain, root switch, switch/XDomain topology objects, ICM private flags, protocol version, boot ACL size, and cached NVM auth reply. Switch objects store route, link/depth, connection id/key, authorization state, security level, boot flag, speed/width, runtime PM capability, UUID, and unplug markers.

Firmware-visible persistent effects include approving switches, adding secure keys, challenge approval, boot ACL reads/writes, disconnecting PCIe paths, XDomain path setup/teardown, saving devices for boot ACL, USB4 router operations, and NVM authentication. Safe mode blocks normal topology creation and instead exposes a safe-mode root switch for NVM recovery.

## Dependencies and Integration Points

The file depends on the control channel, NHI firmware status/mailbox registers, PCI config access, runtime PM, workqueues, Thunderbolt switch/XDomain/device helpers, tunnel notifications, platform Apple detection, USB4 operation definitions, and connection-manager operations consumed by `domain.c`.

It integrates with `domain.c` as a `tb_cm_ops` provider; with `eeprom.c` and NVM code through USB4 switch operation proxy and NVM auth status; with `dma_test.c` and XDomain services through XDomain path approval; and with suspend/runtime PM through domain and switch callbacks.

## Risks and Edge Cases

The ICM protocol has multiple generation-specific packet formats. Reusing Falcon Ridge handlers for Alpine Ridge and Titan Ridge handlers for newer controllers is intentional but brittle if firmware semantics diverge. Topology reconciliation must handle stale UUIDs, dual-link route changes, resume events, and switches replaced by XDomain hosts.

`icm_copy()` copies responses when `packet_id < npackets` and completes when `packet_id == total_packets - 1`; it does not verify `total_packets <= npackets`, so malformed firmware can cause early completion with missing packets or ignored extra packets.

`icm_usb4_switch_op()` uses `tx_data_len` and `rx_data_len` as dword counts in copies but compares `tx_data_len < ARRAY_SIZE(request.data)`. Callers must pass lengths in dwords, not bytes, or data will be over-copied.

Asynchronous NVM auth stores only one `last_nvm_auth`. A second auth completion before status consumption frees the old reply with a warning. Concurrent auth operations on multiple switches can overwrite status.

Several runtime PM calls use `pm_runtime_get_sync()` without checking errors. Resume cleanup relies on completion signaling to avoid deadlock when removing runtime-suspended switches.

## Test Signals

Tests should cover probe selection for each PCI ID family, unsupported Apple/Falcon Ridge behavior, `start_icm` firmware start paths, safe-mode handling, driver-ready timeout, boot ACL get/set, switch approval/key/challenge success and failures, ICM request timeout/retry, multipacket topology responses, device connected/disconnected reconciliation, XDomain connected/disconnected replacement, suspend/resume rescan cleanup, RTD3 veto reference handling, USB4 proxy ops, asynchronous NVM auth status, and disconnecting PCIe/XDomain paths before NVM upgrade.
