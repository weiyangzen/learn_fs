<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/properties.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/properties.c

## Purpose

This file provides exported helpers for getting and setting Wilco EC properties through the mailbox property command.

## Important APIs, Types, And Functions

`struct ec_property_request` and `struct ec_property_response` encode operation, little-endian property ID, length, and data. `send_property_msg()` wraps a `WILCO_EC_MSG_PROPERTY` mailbox transaction and validates echoed operation and property ID. Exported helpers are `wilco_ec_get_property()`, `wilco_ec_set_property()`, `wilco_ec_get_byte_property()`, and `wilco_ec_set_byte_property()`.

## Control Flow

Get requests set operation `EC_OP_GET` and a property ID, then copy response length/data into the caller message. Set requests include length/data and require the response length to match. Byte helpers enforce one-byte property values.

## State And Persistence

The file keeps no local state. Property values live in the EC and may persist depending on firmware. Request and response buffers are stack local.

## Dependencies And Integration Points

It depends on the Wilco mailbox export, Wilco platform data property limits, unaligned little-endian helpers, and external Wilco feature drivers that use property APIs.

## Risks

There is no explicit bounds check on `rs.length` before copying into `prop_msg->data`; safety depends on EC protocol and `WILCO_EC_PROPERTY_MAX_SIZE`. Set copies `prop_msg->length` bytes into the fixed request data buffer, so callers must respect the maximum.

## Test Signals

Test valid get/set, mismatched echoed operation, mismatched property ID, byte helper length validation, maximum-size properties, EC errors, and caller-side length bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/properties.c -->
