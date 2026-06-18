<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.c

## Purpose

This file provides Chrome EC USB Power Delivery Vendor Defined Message support for Type-C ports. It fetches pending EC VDM responses/attention messages, forwards them to the matching Type-C altmode, and implements partner altmode operations that send VDM requests through the EC.

## Important APIs, Types, And Functions

`cros_typec_handle_vdm_attention()` repeatedly reads `EC_CMD_TYPEC_VDM_RESPONSE` while attentions remain and calls `typec_altmode_attention()`. `cros_typec_handle_vdm_response()` forwards a fetched VDM to `typec_altmode_vdm()`. `cros_typec_port_amode_enter()` and `cros_typec_port_amode_vdm()` build `TYPEC_CONTROL_COMMAND_SEND_VDM_REQ` payloads. The exported `port_amode_ops` supplies `.enter` and `.vdm` callbacks for port altmodes.

## Control Flow

When the higher-level EC Type-C driver observes VDM-related events, it calls the handler for the affected port. The handler reads the EC response, extracts SVID and object position from the header, finds the registered port altmode with `typec_match_altmode()`, and forwards the event. For AP-originated VDMs, the Type-C core calls `port_amode_ops`, which fills `struct typec_vdm_req` and sends it to the EC.

## State And Persistence

No persistent local state is held. All state lives in the EC pending VDM queue, registered Type-C altmode objects, and partner/port mode state managed elsewhere.

## Dependencies And Integration Points

It depends on `cros_ec_typec.h`, Chrome EC Type-C VDM response/control commands, USB PD VDO helpers, and the Type-C altmode core. The companion header exports the operations and handlers.

## Risks

The attention handler reads `resp.vdm_response[0]` for the header but calls `typec_altmode_attention()` with `resp.vdm_attention[1]`; this relies on the EC response union layout and should be kept aligned with the command ABI. `cros_typec_port_amode_vdm()` sets `vdm_data_objects = cnt` and copies `cnt - 1` payload objects, so callers must pass counts consistent with the header plus payload convention. Unregistered altmodes drop the event.

## Test Signals

Test VDM response forwarding by SVID/OPOS, attention loops with `vdm_attention_left`, EC command errors, unregistered altmode diagnostics, EnterMode request formation, arbitrary VDM payload copying, and SVDM version expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.c -->
