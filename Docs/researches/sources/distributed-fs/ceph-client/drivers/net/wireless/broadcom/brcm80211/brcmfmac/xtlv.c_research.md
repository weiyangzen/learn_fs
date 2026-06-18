# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/xtlv.c

Purpose: implements helpers for packing Broadcom extended TLV headers with configurable 8-bit or 16-bit id/length fields and optional 32-bit alignment.

Important APIs and functions: `brcmf_xtlv_data_size()` returns header plus data size, rounded to four bytes when `BRCMF_XTLV_OPTION_ALIGN32` is set. `brcmf_xtlv_pack_header()` writes id and length in little-endian or byte-sized forms according to `BRCMF_XTLV_OPTION_IDU8` and `BRCMF_XTLV_OPTION_LENU8`, then copies optional payload. Internal `brcmf_xtlv_header_size()` computes the variable header length from the nominal `struct brcmf_xtlv` layout.

Control flow: option combinations choose among 16/16, 8/8, 8/16, and 16/8 header layouts. Unexpected option combinations warn and return. Length is truncated to 8 bits after a warning when `LENU8` is set.

State and persistence: no persistent state. The caller owns the output buffer and must allocate enough space using the size helper.

Dependencies and integration: depends on Linux unaligned little-endian access, `roundup()`, and option definitions in `xtlv.h`. Used by brcmfmac firmware command/config payload builders.

Risks and test signals: caller buffer sizing is critical because pack does not receive buffer capacity. Data-size and pack-header option handling must agree. Test all four id/len width combinations, alignment rounding, null data payloads, and `LENU8` overflow warnings.
