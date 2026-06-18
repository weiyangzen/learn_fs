# sources/distributed-fs/ceph-client/drivers/net/ppp/ppp_mppe.h

Purpose: Defines MPPE option constants and macros that convert between internal option flags and the four-octet MPPE CCP configuration information.

Important APIs and constants: `MPPE_PAD` advertises MPPE frame growth, and `MPPE_MAX_KEY_LEN` is 16 bytes. Supported internal flags are `MPPE_OPT_40`, `MPPE_OPT_128`, and `MPPE_OPT_STATEFUL`; unsupported/diagnostic flags include `MPPE_OPT_56`, `MPPE_OPT_MPPC`, `MPPE_OPT_D`, `MPPE_OPT_UNSUPPORTED`, and `MPPE_OPT_UNKNOWN`. Wire-bit constants include C/D/L/S/M/H. `MPPE_OPTS_TO_CI()` builds a four-byte CI, and `MPPE_CI_TO_OPTS()` parses one.

Control flow and state: The header holds no runtime state. Callers use `MPPE_OPTS_TO_CI()` during negotiation and `MPPE_CI_TO_OPTS()` in `ppp_mppe.c` init to select key length and stateful/stateless mode. Reserved or unsupported peer bits are surfaced in the parsed option flags.

Dependencies and integration points: Included by `ppp_mppe.c` and tied to PPP CCP `CI_MPPE` definitions. It assumes callers have already validated option length and provided a four-byte CI buffer.

Risks and test signals: H and C use the same numeric bit in different octets, so edits to masks/macros are easy to get wrong. The macros do not check buffer length. Test 40/128-bit, stateful/stateless conversion, unsupported C/M/D bits, reserved octets, unknown bits, and integration with MPPE option rejection and key-length selection.
