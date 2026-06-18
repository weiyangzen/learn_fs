# `sources/distributed-fs/ceph-client/include/linux/usb/phy_companion.h`

## Purpose

`phy_companion.h` defines a minimal companion object for PHY comparator/OTG helper hardware that handles VBUS and SRP capabilities alongside a USB PHY.

## Important APIs, Types, and Constants

- `struct phy_companion` exposes `set_vbus()` for A-peripheral VBUS control and `start_srp()` for B-device session request protocol.

## Control Flow and Lifetimes

An OTG/PHY driver attaches a companion object when external comparator hardware owns VBUS or SRP signaling. Role or session changes call the companion callbacks while the parent PHY remains registered.

## State and Persistence Behavior

The header defines callback shape only. Runtime state is owned by the companion driver/hardware.

## Dependencies and Integration Points

It depends on `usb/otg.h` and integrates legacy PHY code with external VBUS/ID/SRP support hardware.

## Risks and Edge Cases

Callbacks are optional by structure convention but consumers must check before use. VBUS control must match board power topology. SRP calls are valid only in B-device contexts.

## Test Signals

Test VBUS enable/disable through companion hardware, SRP initiation, missing-callback paths, role switching, and suspend/resume with external comparator state.
