# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.h

Purpose: exposes the device-tree probe hook and provides a no-op fallback when Open Firmware support is not compiled.

Important APIs/types: declares `brcmf_of_probe(struct device *dev, enum brcmf_bus_type bus_type, struct brcmf_mp_device *settings)` under `CONFIG_OF`; otherwise defines a static stub returning success.

Control flow and state: this header lets common bus setup call `brcmf_of_probe` unconditionally. State mutation happens only in `of.c`; the fallback intentionally leaves platform settings unchanged.

Dependencies and integration: depends on `struct device`, `enum brcmf_bus_type`, and `struct brcmf_mp_device` being visible from including files. It integrates OF platform data with bus-independent driver initialization.

Risks: the fallback returning 0 means builds without OF silently skip DT-derived settings. The header lacks its own include guard, relying on small size and normal include patterns; repeated inclusion is harmless for the declaration but less conventional.

Test signals: compile with and without `CONFIG_OF`, probe on non-DT platforms, and verify bus setup handles unchanged settings.
