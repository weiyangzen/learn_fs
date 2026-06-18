# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.c

## Purpose

This file implements optional HDCP control for the MHDP8546 DisplayPort bridge using the secure APB mailbox. It negotiates HDCP 2.2 first where allowed, falls back to HDCP 1.4 for Type 0 content, updates connector content-protection state, and periodically checks link authentication.

## Important APIs, Types, And Functions

Public entry points are `cdns_mhdp_hdcp_init()`, `cdns_mhdp_hdcp_enable()`, and `cdns_mhdp_hdcp_disable()`. Internal helpers mirror the core mailbox helpers on `sapb_regs`, then implement status/config commands, receiver-ID validation, KM-stored response, authentication flows, retry checks, and property work.

## Control Flow

Enable takes `hdcp.mutex`, runs `_cdns_mhdp_hdcp_enable()`, tries HDCP 2.2 up to three times, falls back to HDCP 1.4 only for content type 0, marks content protection enabled, schedules property work, and starts delayed link checks. Authentication configures firmware, waits for SW events from the core IRQ path, validates receiver IDs, responds valid, and waits for auth completion. Check work retries authentication when status loses the auth bit. Disable marks content protection undesired, schedules property work, sends disable config, and cancels delayed checks.

## State And Persistence Behavior

State is in `mhdp->hdcp`: delayed work, property work, mutex, current DRM property value, and content type. Pairing/KM data structs exist in the header, but this implementation does not persist keys; it responds with no stored KM.

## Dependencies And Integration Points

It depends on `sapb_regs`, the core `mbox_mutex`, core SW event wait queue, DRM HDCP property values, and `mhdp->connector`. The core calls enable from atomic enable and disable from atomic disable.

## Risks And Test Signals

Risks include fixed-size receiver ID storage versus firmware-provided receiver count, returning `-1` instead of standard errno in many paths, connector lifetime races in work, and remove explicitly ignoring HDCP work cleanup. Test signals include content-protection property transitions, HDCP 2.2/1.4 negotiation logs, forced reauth after sink unplug, and absence of lingering work after bridge disable.
