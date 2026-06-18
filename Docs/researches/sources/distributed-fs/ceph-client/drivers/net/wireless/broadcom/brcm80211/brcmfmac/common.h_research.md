# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.h

Purpose: Defines common module-global and per-device settings shared by bus probes, firmware loading, and core attach code.

Important APIs/types/functions: `struct brcmf_mp_global_t` stores the alternate firmware path. `struct brcmf_mp_device` stores P2P enable, feature-disable mask, FWS flow-control mode, roamoff, IAPP enable, debug probe bypass, country-code map, board type, MAC override, antenna SKU, calibration blob, and bus-specific SDIO platform data. Prototypes cover settings allocation/release, join preference, preinit dcmds, MAC programming, DMI/ACPI probing, and priority mapping.

Control flow: Bus/device probe calls `brcmf_get_module_param()` before core attach. Later preinit and cfg80211 paths consume these settings.

State and persistence behavior: Settings are heap allocated per device; some pointer fields are references to platform/firmware data. Global alternate path is copied once at module init.

Dependencies and integration points: Includes Linux brcmfmac platform data and `fwil_types.h`. Conditional DMI/ACPI stubs allow builds without those subsystems.

Risks: Precedence between module params, platform data, DMI, OF, and ACPI matters. Pointer fields require provider lifetime discipline.

Test signals: Build with and without CONFIG_DMI/CONFIG_ACPI; verify OF `-EPROBE_DEFER`, settings release, and board-type propagation.
