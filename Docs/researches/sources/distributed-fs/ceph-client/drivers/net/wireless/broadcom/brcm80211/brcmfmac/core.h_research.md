# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.h

Purpose: Declares central brcmfmac driver state, interface state, constants, and APIs shared across bus, protocol, cfg80211, firmware, feature, event, and vendor modules.

Important APIs/types/functions: Defines max interfaces, dcmd sizes, TX ioctl max, firmware version length, ND table size, and namespace export helper. `struct brcmf_pub` is the driver instance. `struct brcmf_if` is per-interface state. `struct brcmf_rev_info` stores decoded firmware revision info. `struct brcmf_ampdu_rx_reorder` tracks receive reordering. `enum brcmf_netif_stop_reason` defines queue-stop bits.

Control flow: Other modules receive `brcmf_pub`/`brcmf_if` from `core.c` and operate through these shared structs and declared APIs.

State and persistence behavior: Runtime-only state. `proto_buf` is protected by `proto_block`; `iflist` and `if2bss` are authoritative interface maps; 802.1X counters/waitqueues live until interface removal.

Dependencies and integration points: Includes cfg80211 and FWEH. Enables namespaced exports when brcmfmac is modular.

Risks: Shared mutable fields require careful ordering and locking. `netif_stop` is 8-bit, so new stop reasons must fit. All `proto_buf` users must hold the mutex.

Test signals: Built-in vs module builds, interface mapping, command serialization, and multi-reason queue blocking.
