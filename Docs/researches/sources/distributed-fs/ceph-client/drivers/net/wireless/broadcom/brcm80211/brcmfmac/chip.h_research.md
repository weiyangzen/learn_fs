# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.h

Purpose: Declares the public chip/core abstraction used by bus drivers and firmware loading code to identify hardware, enumerate cores, size RAM, and control core reset/active state.

Important APIs/types/functions: `struct brcmf_chip` stores chip id/revision, enum base, ChipCommon/PMU caps, RAM base/size, retention size, and printable name. `struct brcmf_core` stores core id/revision/base. `struct brcmf_buscore_ops` is the bus MMIO/control contract: `read32`, `write32`, `prepare`, optional `reset`/`setup`, and `activate`. Prototypes expose attach/detach, core lookup, reset/disable/is-up, active/passive, SR detection, name formatting, and enum base lookup.

Control flow: Bus implementations populate ops and call `brcmf_chip_attach()`. Consumers query the returned `brcmf_chip` and call passive/active transitions around firmware upload.

State and persistence behavior: Defines runtime structs only; actual lifetime is owned by `chip.c`. Hardware state changes happen through bus callbacks.

Dependencies and integration points: Uses Linux integer types and `CORE_CC_REG()` for `chipcregs` offsets. Integrated with bus-specific probe and firmware upload.

Risks: Bad bus ops can corrupt hardware state. The header guard closing comment is stale but harmless.

Test signals: Compile all bus users; attach should reject missing mandatory ops; callers should handle NULL/ERR core and chip returns.
