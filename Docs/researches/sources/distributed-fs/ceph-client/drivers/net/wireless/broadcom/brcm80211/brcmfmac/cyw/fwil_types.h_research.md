# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/fwil_types.h

Purpose: Declares CYW-specific firmware-interface structures and constants used by the vendor plugin.

Important APIs/types/functions: `enum brcmf_event_msgs_ext_command`, `EVENTMSGS_VER`, `struct brcmf_eventmsgs_ext`, external auth flags, `struct brcmf_auth_req_status_le`, and `struct brcmf_mf_params_le`.

Control flow: CYW code fills these structures for `event_msgs_ext`, `auth_status`, and `mgmt_frame` iovar calls, and decodes external-auth event payloads from firmware.

State and persistence behavior: Wire-format little-endian transient payloads only.

Dependencies and integration points: Includes shared `fwil_types.h` and relies on 802.11/Ethernet constants through included headers.

Risks: Layout and endianness must match firmware. Flexible arrays require correct allocation sizes. `EVENTMSGS_EXT_STRUCT_SIZE` references `struct eventmsgs_ext`, which appears stale and would fail if used.

Test signals: Sparse/endian checks; runtime CYW event mask setting and SAE auth exchange validate ABI layout.
