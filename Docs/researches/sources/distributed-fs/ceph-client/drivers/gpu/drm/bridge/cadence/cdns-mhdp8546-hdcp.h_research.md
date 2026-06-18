# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.h

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.h

## Purpose

This header defines the MHDP8546 HDCP mailbox protocol constants, status helpers, pairing/public-key data shapes, and public HDCP entry points.

## Important APIs, Types, And Functions

It defines receiver/status sizes, status bit extraction through `GET_HDCP_PORT_STS_LAST_ERR()`, HDCP configuration bits, HDCP transaction opcodes, content types, the periodic check interval, `struct cdns_hdcp_pairing_data`, `struct cdns_hdcp_tx_public_key_param`, and prototypes for `cdns_mhdp_hdcp_enable()`, `cdns_mhdp_hdcp_disable()`, and `cdns_mhdp_hdcp_init()`.

## Control Flow

There is no executable flow. The enums encode firmware message IDs used by the secure mailbox implementation; the public prototypes are called by the MHDP core during bridge enable, disable, and probe initialization.

## State And Persistence Behavior

The header describes key/pairing data layouts but does not store data. Runtime state lives in `struct cdns_mhdp_hdcp` from the core header.

## Dependencies And Integration Points

It includes `cdns-mhdp8546-core.h` for the device type and shared mailbox constants. It also implicitly depends on DRM HDCP content type constants consumed by the C file.

## Risks And Test Signals

Protocol enum ordering is firmware ABI sensitive. A mismatch can make HDCP commands syntactically valid but semantically wrong. Build coverage of HDCP-enabled MHDP and runtime authentication against HDCP 1.4 and 2.2 sinks are the key signals.
