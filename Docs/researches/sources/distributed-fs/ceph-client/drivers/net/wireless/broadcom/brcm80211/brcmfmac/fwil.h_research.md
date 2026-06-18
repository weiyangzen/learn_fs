# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.h

Purpose: Declares firmware command IDs and typed helpers for FWIL command, iovar, bsscfg, and XTLV access.

Important APIs/types/functions: Defines Broadcom command constants for get/set var, revinfo, scan timing, monitor, promisc, country, keys, PM, AP, and others. Declares data set/get APIs and inline scalar wrappers with little-endian conversion.

Control flow: Callers use inline int helpers for scalar operations or data helpers for structured payloads; all route to `fwil.c`.

State and persistence behavior: No state. Inline query helpers mutate caller-provided scalar buffers for endian conversion.

Dependencies and integration points: Includes `debug.h`; used throughout brcmfmac control paths.

Risks: Inline helpers cast `u32 *` to little-endian storage and require aligned buffers. Command IDs must match firmware ABI. XTLV int get initializes a local from input value even though get generally ignores it.

Test signals: Command constant compile coverage; int set/get endianness; bsscfg index wrapping; XTLV alignment.
