# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c

## Purpose
`pcie.c` is the Broadcom/Cypress `brcmfmac` PCIe bus backend. It registers the PCI driver, enumerates supported PCIe chip IDs, requests firmware/NVRAM/CLM/TXCAP blobs, downloads firmware into device RAM, discovers firmware shared RAM, builds MSGBUF common and flow rings, wires those rings into the core `brcmf_bus`/protocol layer, handles PCIe mailbox interrupts, and implements reset, suspend/resume, firmware console, coredump, and blob handoff behavior.

## Important APIs, types, and functions
- `struct brcmf_pciedev_info` is the main persistent bus state: PCI device, firmware names/blobs, MMIO mappings, chip metadata, shared RAM/ring metadata, IRQ state, mailbox wait queue, DMA index buffers, OTP parameters, WoWL flag, and debug console timer state.
- `struct brcmf_pcie_shared_info` mirrors firmware shared RAM fields: protocol version/flags, common rings, flow rings, ring counts, rx offsets, mailbox data addresses, firmware console address, scratch DMA buffers, and DMA ring-update buffers.
- `struct brcmf_pcie_ringbuf` wraps `struct brcmf_commonring` with DMA handle, device index locations, ring id, and backpointer. Its callbacks are registered with `brcmf_commonring_register_cb()`.
- `brcmf_pcie_probe()` allocates bus/private state, attaches the chipcore, selects PCIe register layout, loads module settings, reads OTP where needed, allocates common driver state, and starts async firmware loading through `brcmf_fw_get_firmwares()`.
- `brcmf_pcie_setup()` is the firmware callback. It attaches PCIe quirks, gets/adjusts RAM info, downloads firmware/NVRAM, initializes shared RAM, allocates rings/scratch buffers, requests IRQs, exposes rings to `bus->msgbuf`, calls `brcmf_attach()`, and starts firmware console polling.
- `brcmf_pcie_download_fw_nvram()` enters download state, writes firmware at `ci->rambase`, writes NVRAM and optional random seed near the top of RAM, releases the ARM core, waits for firmware to publish the shared RAM pointer, validates it, and initializes shared state.
- `brcmf_pcie_init_ringbuffers()` reads `brcmf_pcie_dhi_ringinfo`, decides whether indices live in TCM or host DMA memory, allocates common rings, creates flow-ring wrappers, and records firmware limits.
- `brcmf_pcie_quick_check_isr()` and `brcmf_pcie_isr_thread()` implement the threaded interrupt path: mask, acknowledge, handle mailbox data, trigger MSGBUF RX, read console, and re-enable interrupts when the bus is up.
- `brcmf_pcie_reset()`, `brcmf_pcie_remove()`, `brcmf_pcie_pm_enter_D3()`, and `brcmf_pcie_pm_leave_D3()` cover driver reset, teardown, D3 entry, and hot/cold resume.

## Control flow
The PCI driver registers through `brcmf_pcie_register()`. Probe allocates `brcmf_pciedev_info`, maps BAR resources through the chip attach path, chooses register offsets based on PCIe core revision, creates `brcmf_bus` with `BRCMF_PROTO_MSGBUF`, obtains module parameters, optionally parses OTP for Apple/WCC/BCA firmware board-type selection, and requests firmware. The firmware callback downloads the image, waits for the firmware shared-memory handshake, configures DMA rings and scratch buffers, enables mailbox IRQs, attaches the common driver, and leaves the bus in `BRCMFMAC_PCIE_STATE_UP`.

Runtime TX/RX data transport is delegated to MSGBUF through common-ring callbacks. Ring callbacks write/read host or TCM indices and ring the H2D mailbox. PCIe D2H doorbells wake the threaded ISR, which acknowledges the mailbox register, processes function-zero mailbox data such as D3 ACK/deep-sleep/FW halt, and calls `brcmf_proto_msgbuf_rx_trigger()` when D2H ring doorbells arrive.

Reset and resume deliberately tear down high-level state before reusing the firmware path. `brcmf_pcie_reset()` disables interrupts, drains console logs, detaches core driver state, releases IRQs/DMA rings/scratch buffers, watchdog-resets the device, and reloads firmware. Resume first attempts a hot D0 mailbox handshake; if the intmask indicates the device is not alive, it removes and reprobes the PCI function.

## State and persistence behavior
Persistent state is in heap allocations owned by the PCI device lifetime: `brcmf_pciedev_info`, `brcmf_pciedev`, `brcmf_bus`, `bus->msgbuf`, DMA common rings, optional host index DMA buffer, scratch/ring-update DMA buffers, firmware blobs retained until common code requests them, module settings, and chip metadata. Firmware/NVRAM contents are not persisted by the driver beyond download; firmware names and optional CLM/TXCAP firmware pointers are kept for later handoff. Device state is represented by `BRCMFMAC_PCIE_STATE_DOWN/UP`, `irq_allocated`, `mbdata_completed`, `in_irq`, `wowl_enabled`, and debug console timer flags.

The file also maintains shared hardware state: BAR0 window selection, PCI config registers restored around reset, mailbox data fields in TCM, DMA ring index host addresses in the firmware ring-info block, and D3/D0/deep-sleep mailbox protocol bits.

## Dependencies and integration points
This backend depends on Linux PCI/MSI/firmware/DMA APIs, Broadcom chipcore helpers (`chip.c`, `soc.h`, `chipcommon.h`), `firmware.h`, `commonring.h`, `msgbuf.h`, `bus.h`, `core.h`, `common.h`, module parameter handling, and debug/trace helpers. It integrates upward through `struct brcmf_bus_ops` (`preinit`, `stop`, `wowl_config`, `get_ramsize`, `get_memdump`, `get_blob`, `reset`, `debugfs_create`) and through `bus->msgbuf` common/flow ring pointers consumed by the MSGBUF protocol layer.

## Risks and edge cases
- Shared RAM version and address validation are critical; unsupported versions or bad pointers abort setup.
- Ring initialization depends on firmware-provided counts and offsets. The code rejects `max_flowrings > 512`, but many other ring-info fields are trusted after endian conversion.
- Host index DMA mode switches pointer accessors from TCM to host memory; lifetime and cache coherency rely on coherent allocation and correct firmware address publication.
- `brcmf_pcie_send_mb_data()` waits up to about one second for an existing mailbox transaction to clear; stuck firmware can block reset/suspend paths.
- `brcmf_pcie_release_irq()` frees IRQ then polls `in_irq`, so races around threaded IRQ completion are explicitly handled but still timing-sensitive.
- Firmware download places NVRAM and optional random seed at top-of-RAM; bad RAM sizing or seed placement can corrupt firmware-owned memory.
- OTP parsing rejects malformed Apple board parameters and can fail probe for WCC/BCA paths.
- Resume has two distinct paths. Hot resume depends on firmware still responding; cold resume removes and reprobes, increasing teardown/reentry risk.

## Test signals
Useful validation signals include successful PCI probe, firmware request names/board-type selection, `PCIe protocol version` log, shared RAM address log, ring count logs, IRQ request success, `brcmf_attach()` success, MSGBUF traffic, D3 ACK wait completion, hot resume logs, firmware coredump/memdump availability, debugfs `console_interval`, and negative tests for missing firmware, invalid shared RAM version/address, unsupported OTP data, IRQ request failure, ring allocation failure, and resume fallback reprobe.
