# sources/distributed-fs/ceph-client/net/core/timestamping.c

## Purpose
This file supports PHY-level PTP hardware timestamping for transmitted and received skbs. It identifies PTP packets and defers timestamp handling to a PHY/MII timestamper when the netdevice timestamp provider is PHYLIB-backed or the PHY uses default hardware timestamping.

## APIs, Types, and Functions
The internal `classify()` wrapper calls `ptp_classify_raw()` only when the skb has a device, PHY device, and MII timestamper. Exported APIs are `skb_clone_tx_timestamp()` for transmit timestamp cloning and `skb_defer_rx_timestamp()` for receive timestamp deferral.

## Control Flow, State, and Persistence
Transmit flow verifies the skb has both socket and device, resolves the timestamping PHY through `dev->hwprov` under RCU or legacy `dev->phydev`, classifies the packet, clones the skb with socket ownership, and calls `mii_ts->txtstamp()`. Receive flow resolves the PHY similarly, temporarily pushes the Ethernet header if enough headroom exists, classifies the raw packet, restores the skb data pointer, and calls `mii_ts->rxtstamp()` if available.

No persistent state is owned here; it consumes RCU-protected netdevice timestamp provider state and PHY timestamper callbacks.

## Dependencies and Integration
Depends on PHYLIB, PTP classifier logic, skb cloning and headroom manipulation, netdevice hardware timestamp providers, and MII timestamper callbacks. It integrates with driver TX/RX paths that call these helpers when PHY timestamping may own timestamp production.

## Risks and Test Signals
Risks include using a PHY pointer after provider changes, mishandling skb headroom/data pointer restoration, failing to clone TX skbs under pressure, classifying packets without an Ethernet header, and missing timestamp callbacks when providers are non-default. Test signals include PTP over PHY hardware tests, TX clone failure injection, RX headroom boundary tests, provider switch tests under RCU debug, and packet capture/error-queue validation for timestamp delivery.
