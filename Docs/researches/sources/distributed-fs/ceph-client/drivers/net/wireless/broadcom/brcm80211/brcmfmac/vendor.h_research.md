# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.h

Purpose: defines the Broadcom nl80211 vendor command identifiers, reply attributes, and command header used by `vendor.c`.

Important APIs and types: `BROADCOM_OUI` is `0x001018`. `enum brcmf_vndr_cmds` currently defines only `BRCMF_VNDR_CMDS_DCMD` besides unspecified/last markers. `enum brcmf_nlattrs` defines `BRCMF_NLATTR_LEN` and `BRCMF_NLATTR_DATA`. `struct brcmf_vndr_dcmd_hdr` contains firmware command id, expected return length, payload offset, get/set selector, and a magic field. `brcmf_vendor_cmds[]` is exported for cfg80211 registration.

Control flow: this header has no executable flow; it fixes the wire contract parsed by the vendor command handler.

State and persistence: no local state. Fields influence temporary command buffers and firmware state changes when userspace issues set commands.

Dependencies and integration: consumed by brcmfmac cfg80211 setup and `vendor.c`; externally, userspace tools must match this structure and attributes.

Risks and test signals: ABI drift would break userspace. The `magic` field is documented but not validated by the implementation, so tests should confirm current behavior rather than assume authentication. Attribute IDs and struct packing should be checked on 32-bit and 64-bit builds.
