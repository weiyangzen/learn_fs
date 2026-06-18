# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bus.h

## Purpose
`bus.h` defines the common brcmfmac bus abstraction used between the bus-specific transports (SDIO, USB, PCIe) and the core/cfg80211/protocol layers. It standardizes bus state, firmware vendor identity, protocol type, firmware blob retrieval, msgbuf ring metadata, shared bus statistics, and the callback table that all bus backends expose to the common driver.

The file is a contract header rather than an implementation unit. Its inline wrappers are the normal call surface for upper layers so that most of brcmfmac does not need to know whether the underlying device is SDIO, USB, or PCIe.

## Important APIs, Types, And Functions
- Ring constants:
  - `BRCMF_H2D_MSGRING_CONTROL_SUBMIT`, `BRCMF_H2D_MSGRING_RXPOST_SUBMIT`, and `BRCMF_H2D_MSGRING_FLOWRING_IDSTART` identify host-to-device msgbuf rings.
  - `BRCMF_D2H_MSGRING_CONTROL_COMPLETE`, `BRCMF_D2H_MSGRING_TX_COMPLETE`, and `BRCMF_D2H_MSGRING_RX_COMPLETE` identify device-to-host rings.
  - `BRCMF_NROF_H2D_COMMON_MSGRINGS`, `BRCMF_NROF_D2H_COMMON_MSGRINGS`, and `BRCMF_NROF_COMMON_MSGRINGS` encode the common-ring count.
- Bus identity and mode enums:
  - `enum brcmf_fwvendor` distinguishes WCC, CYW, BCA, invalid, and count values for firmware vendor behavior.
  - `enum brcmf_bus_state` is the global transfer readiness switch: `BRCMF_BUS_DOWN` or `BRCMF_BUS_UP`.
  - `enum brcmf_bus_protocol_type` selects BCDC or MSGBUF host/dongle protocol.
  - `enum brcmf_blob_type` names firmware blob categories such as CLM and TXCAP.
- `struct brcmf_bus_ops` is the bus callback vtable. Mandatory callbacks include `stop`, `txdata`, `txctl`, and `rxctl`; optional callbacks include `preinit`, `gettxq`, `wowl_config`, memory dump, blob retrieval, debugfs setup, reset, and transport-specific remove.
- `struct brcmf_bus_msgbuf` carries ring pointers and msgbuf limits for PCIe/msgbuf operation: common rings, flowrings, RX offset, RX post count, flowring count, and submission/completion ring limits.
- `struct brcmf_bus_stats` currently tracks packet copy-on-write counts through atomics.
- `struct brcmf_bus` is the central bus instance:
  - `bus_priv` stores one of `sdio`, `usb`, or `pcie` private device pointers.
  - `proto_type`, `dev`, `drvr`, `state`, `stats`, `maxctl`, `chip`, `chiprev`, `fwvid`, queue and WoWLAN capability flags, `ops`, `msgbuf`, and `list` connect the bus to common driver state.
- Inline wrappers:
  - `brcmf_bus_preinit()`, `brcmf_bus_stop()`, `brcmf_bus_txdata()`, `brcmf_bus_txctl()`, `brcmf_bus_rxctl()`.
  - `brcmf_bus_gettxq()`, `brcmf_bus_wowl_config()`, `brcmf_bus_get_ramsize()`, `brcmf_bus_get_memdump()`, `brcmf_bus_get_blob()`, `brcmf_bus_debugfs_create()`, `brcmf_bus_reset()`, and `brcmf_bus_remove()`.
- Common-layer entry points declared for bus users include `brcmf_alloc()`, `brcmf_attach()`, `brcmf_detach()`, `brcmf_free()`, `brcmf_dev_reset()`, `brcmf_dev_coredump()`, `brcmf_fw_crashed()`, `brcmf_bus_change_state()`, and bus-specific register/exit stubs for SDIO, USB, and PCIe.

## Control Flow
Bus-specific modules create a `struct brcmf_bus`, populate `ops`, point `dev` and `bus_priv` at their transport device, and call common-layer functions such as `brcmf_attach()`. Once attached, upper layers use the inline wrappers in this header to send data and control messages without branching on transport type.

The typical data path is:
1. Core/network code decides a frame or control message must go to firmware.
2. It calls `brcmf_bus_txdata()`, `brcmf_bus_txctl()`, or `brcmf_bus_rxctl()`.
3. The wrapper dispatches through `bus->ops` to the active SDIO, USB, or PCIe implementation.
4. Completion and RX traffic flow back through common-layer callbacks such as `brcmf_rx_frame()` and `brcmf_rx_event()`.

Optional capability paths have explicit defaults. `preinit()` returns success when absent; `gettxq()` returns `ERR_PTR(-ENOENT)`; WoWLAN config and debugfs creation become no-ops; RAM size returns zero; memory dump and reset return `-EOPNOTSUPP`; `brcmf_bus_remove()` falls back to `device_release_driver()` when no bus remove callback exists.

## State And Persistence Behavior
`struct brcmf_bus` persists for the lifetime of a brcmfmac device and carries global bus state consumed by cfg80211/core paths. The key persistent state is `state`, which upper layers use as a safety check before firmware commands, and metadata such as chip ID, chip revision, firmware vendor, and protocol type. `stats` persist atomic counters across normal packet handling until detach. `msgbuf` persists transport ring topology for msgbuf-capable devices.

No file-backed or firmware-backed persistence is implemented in this header. It defines in-memory structures and wrappers only; hardware and firmware state changes happen in bus-specific callback implementations and common-layer code that call into this interface.

## Dependencies And Integration Points
- Includes Linux kernel device, firmware, and kernel headers plus `debug.h`.
- Depends on forward-declared transport-private types `brcmf_sdio_dev`, `brcmf_usbdev`, and `brcmf_pciedev` through the `bus_priv` union.
- Depends on common driver types such as `struct brcmf_pub`, `struct brcmf_mp_device`, `struct brcmf_commonring`, `struct pktq`, and `struct sk_buff`.
- Integrated by cfg80211 and core code through `drvr->bus_if`; for example cfg80211 checks `drvr->bus_if->state == BRCMF_BUS_UP`, uses `fwvid` for firmware-vendor security behavior, and calls `brcmf_bus_wowl_config()` during suspend/resume.
- Conditional registration helpers (`brcmf_sdio_register()`, `brcmf_usb_register()`, `brcmf_pcie_register()`) isolate core module init/exit from disabled bus build options by returning zero or no-op stubs.

## Risks
- Several inline wrappers dereference mandatory callbacks without null checks. A bus backend that leaves `stop`, `txdata`, `txctl`, or `rxctl` unset will crash callers.
- `brcmf_bus_get_blob()` does not check `ops->get_blob`; it assumes bus implementations that support firmware blobs have wired the callback before use.
- `state` is a shared readiness signal. Incorrect transitions between `BRCMF_BUS_DOWN` and `BRCMF_BUS_UP` can allow cfg80211/core paths to send commands to a halted bus or reject valid operations.
- The msgbuf ring ID constants are part of the transport/protocol ABI. Changing them would misroute control, RX, TX-complete, or dynamic flowring traffic.
- `brcmf_bus_remove()` has two paths: transport-specific remove and generic `device_release_driver()`. Callers must account for both and avoid double-unbind behavior.

## Test Signals
- Build tests across `CONFIG_BRCMFMAC_SDIO`, `CONFIG_BRCMFMAC_USB`, and `CONFIG_BRCMFMAC_PCIE` should verify the conditional stubs and real register functions compile.
- Probe/attach smoke tests should show each bus backend populating mandatory `ops` and transitioning to `BRCMF_BUS_UP` before normal cfg80211 operations.
- Runtime signals include successful control command round trips through `brcmf_bus_txctl()`/`brcmf_bus_rxctl()`, data TX completions through the bus implementation, and RX delivery via `brcmf_rx_frame()`/`brcmf_rx_event()`.
- Suspend/resume tests should verify `brcmf_bus_wowl_config()` is called only when the bus advertises WoWLAN support and that missing optional callbacks degrade cleanly.
- Failure-path tests should cover absent optional callbacks returning `-EOPNOTSUPP` or `ERR_PTR(-ENOENT)` as documented by the wrappers.
