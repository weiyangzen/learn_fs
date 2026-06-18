<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.h

## Purpose

This header exposes the Chrome EC Type-C VDM helpers to the rest of the Chrome EC Type-C driver.

## Important APIs, Types, And Functions

It declares `extern const struct typec_altmode_ops port_amode_ops`, `cros_typec_handle_vdm_attention()`, and `cros_typec_handle_vdm_response()`. The functions operate on `struct cros_typec_data` and a port number, while the altmode ops are attached to Type-C port altmodes.

## Control Flow

Event-handling code includes this header to dispatch EC VDM events into the VDM implementation. Altmode registration code uses `port_amode_ops` so Type-C core callbacks can send VDMs through the EC.

## State And Persistence

The header has no state. It provides only declarations and include guards.

## Dependencies And Integration Points

It includes `linux/usb/typec_altmode.h` and expects `struct cros_typec_data` to be visible to including translation units through `cros_ec_typec.h` or equivalent local context.

## Risks

There is no forward declaration for `struct cros_typec_data` in the header, so include ordering matters. If used outside the existing Chrome EC Type-C source pattern, compilation may fail.

## Test Signals

Compile all Chrome EC Type-C files that include this header and verify unresolved-symbol coverage when the VDM implementation is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.h -->
