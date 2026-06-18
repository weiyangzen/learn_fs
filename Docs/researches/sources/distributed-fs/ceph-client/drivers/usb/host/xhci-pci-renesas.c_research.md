# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci-renesas.c

## Purpose
Implements a dedicated PCI driver for Renesas xHCI controllers that may require firmware loading before normal xHCI PCI probe. It handles firmware validation, download into volatile controller RAM, optional programming of an external ROM, and fallback to the shared xHCI PCI probe/remove implementation.

## Important APIs, Types, And Functions
The PCI entry point is `xhci_pci_renesas_probe()`, with removal delegated to `xhci_pci_remove()`. Firmware flow uses `renesas_xhci_check_request_fw()`, `renesas_fw_verify()`, `renesas_fw_check_running()`, `renesas_fw_download()`, `renesas_load_fw()`, `renesas_check_rom()`, `renesas_check_rom_state()`, `renesas_rom_erase()`, and `renesas_setup_rom()`. `renesas_fw_download_image()` writes alternating DATA0/DATA1 dwords and polls SET_DATA bits. The firmware name is `renesas_usb_fw.mem`.

## Control Flow
Probe first checks whether an external ROM exists and is already loaded. If not, it examines firmware download status bits to decide whether firmware is already running, blocked by a lock, stale, or absent. When firmware is needed, it requests the firmware image, verifies size/header/version-pointer bounds, then tries ROM programming if a ROM is present and falls back to RAM download otherwise. Only after firmware setup succeeds or a valid ROM fallback exists does it call `xhci_pci_common_probe()`.

## State And Persistence
State is mostly PCI configuration-space state in Renesas-specific registers. RAM firmware download is volatile and must be repeated after power loss. ROM erase/program/reload is persistent in the external ROM when successful. The Linux driver does not keep long-lived private state beyond normal PCI/xHCI objects created by common probe.

## Dependencies And Integration Points
Depends on PCI config accessors, firmware loader APIs, unaligned little-endian helpers, module firmware metadata, and exported functions from `xhci-pci.c` in the `xhci` namespace. It claims Renesas device IDs 0x0014 and 0x0015 so the generic PCI xHCI driver deliberately declines them when this driver is enabled.

## Risks And Test Signals
Risks include bricking or corrupting external ROM contents, timeout constants mismatching hardware behavior, endian mistakes in firmware dword writes, stale FW_DOWNLOAD_ENABLE states requiring power-cycle recovery, and missing firmware on systems without usable ROM. Test signals include cold boot with blank RAM firmware, boot with valid ROM, ROM programming success/failure fallback, missing firmware behavior, PCI config error injection, suspend/resume after power loss, and normal USB enumeration after `xhci_pci_common_probe()`.
