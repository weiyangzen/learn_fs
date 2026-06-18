# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/vendor.c

Purpose: exposes a Broadcom cfg80211 vendor command that tunnels a firmware dongle command (`dcmd`) through nl80211 vendor command infrastructure.

Important APIs and functions: `brcmf_cfg80211_vndr_cmds_dcmd_handler()` is the sole handler. It parses `struct brcmf_vndr_dcmd_hdr`, obtains the `brcmf_if` from the wireless device, copies optional payload into a vmalloc buffer, calls `brcmf_fil_cmd_data_set()` or `brcmf_fil_cmd_data_get()`, and returns response data in one or more vendor reply skbs with `BRCMF_NLATTR_DATA` and `BRCMF_NLATTR_LEN`. `brcmf_vendor_cmds[]` registers subcommand `BRCMF_VNDR_CMDS_DCMD` under `BROADCOM_OUI`.

Control flow: input validation checks header length and payload offset, clamps input and return lengths to `BRCMF_DCMD_MAXLEN`, allocates `max(ret_len, len) + 1`, null terminates copied payloads, performs get/set, then chunks replies to `PAGE_SIZE - 0x100`.

State and persistence: no persistent state. It temporarily allocates `dcmd_buf` and reply skbs. Device-visible state may change when the vendor command is a set operation.

Dependencies and integration: depends on cfg80211 vendor command APIs, netlink attributes, brcmf cfg80211 VIF layout, and firmware interface (`fwil`). It is a userspace escape hatch into firmware command handling.

Risks and test signals: risks include malformed offsets, excessive lengths, firmware commands with mismatched set/get semantics, partial multi-skb replies, and exposing broad firmware controls to privileged userspace. Test with short headers, offset boundary cases, max-length input/output, failing firmware commands, and multi-page return buffers.
