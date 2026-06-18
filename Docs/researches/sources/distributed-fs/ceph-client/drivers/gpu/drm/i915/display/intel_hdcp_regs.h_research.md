# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_regs.h

## Purpose

`intel_hdcp_regs.h` centralizes HDCP-related i915 display MMIO register definitions and bit fields. It supports both older port-addressed HDCP registers and display version 12+ transcoder-addressed registers through selection macros.

## Important APIs, Types, And Functions

The header defines no functions. Its important macro groups are HDCP key registers (`HDCP_KEY_CONF`, `HDCP_KEY_STATUS`, Aksv registers and key/fuse bits), repeater SHA-1 registers (`HDCP_REP_CTL`, `HDCP_SHA_V_PRIME()`, `HDCP_SHA_TEXT`, repeater-present and SHA state bits), HDCP 1.4 auth registers (`HDCP_CONF()`, `HDCP_ANINIT()`, `HDCP_ANLO/HI()`, `HDCP_BKSVLO/HI()`, `HDCP_RPRIME()`, `HDCP_STATUS()`), and HDCP 2.2 registers (`HDCP2_AUTH()`, `HDCP2_CTL()`, `HDCP2_STATUS()`, `HDCP2_STREAM_STATUS()`, `HDCP2_AUTH_STREAM()`).

`TRANS_HDCP(display)` selects transcoder-based register addressing for display version 12 and newer; otherwise macros pick per-port register bases. Status bits such as `HDCP_STATUS_ENC`, `HDCP_STATUS_RI_MATCH`, `LINK_AUTH_STATUS`, and `LINK_ENCRYPTION_STATUS` are consumed directly by enable, disable, and link-check paths.

## Control Flow

The register macros are used by `intel_hdcp.c` to load/clear keys, capture An, program BKSV/Ri, drive repeater SHA-1 validation, enable/disable encryption, and poll hardware status. They are also used by HDMI HDCP link checks to write Ri prime and test hardware match status. The macros themselves are pure compile-time address and bit definitions.

## State And Persistence Behavior

State represented here is hardware state, not software persistence. Register bits reflect key-load completion, fuse status, active encryption, authentication status, stream encryption, and SHA engine progress. These values persist in display hardware until changed by driver writes, hardware reset, or power transitions.

## Dependencies And Integration Points

The header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_TRANS`, `_MMIO_PORT`, `_PICK`, and bit helpers. It is tightly coupled to `intel_hdcp.c`, `intel_hdmi.c`, and DDI/DP code that manipulates HDCP signalling and stream state.

## Risks And Edge Cases

Incorrect register selection across port/transcoder generations is the core risk. A wrong base address or bit mask can break authentication, leave encryption enabled, or misreport link status. The comment on `HDCP_DDIE_SHA1_M0` notes a possible bspec inconsistency, which makes repeater validation for that port sensitive. Register definitions must be kept in sync with platform display version behavior.

## Test Signals

Signals include successful HDCP 1.4 and 2.2 enable/disable on pre-Gen12 and Gen12+ platforms, repeater SHA-1 validation, status polling without timeout, correct stream encryption status for MST, and no register access warnings on unsupported transcoders or ports.
