# Research: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net.go

Purpose: provides hashable encodings for MAC addresses and IP/MAC tuples so they can be map keys. Important APIs are `MACAddr`, `MACAddrFromSlice`, `MACAddrFrom6`, `ParseMAC`, `MACAddr.AsSlice`, `MACAddr.String`, `IPMAC`, `IPMACFrom`, and accessors.

Control flow: MAC conversion packs six bytes into a uint64, rejecting non-MAC-48 slice lengths. `ParseMAC` delegates to `net.ParseMAC` then rejects parsed hardware addresses that are not six bytes. `AsSlice` reconstructs the six-byte hardware address, and `String` formats it through `net.HardwareAddr`. `IPMAC` stores a `netip.Addr` plus `MACAddr` and exposes string/accessor methods.

State/dependencies: values are immutable by convention and fully comparable. Dependencies include `net` and `netip`. Integration points include deduplicating or indexing neighbor/endpoint records by IP/MAC. Risks include returning a slice backed by a local array whose escape is handled by Go, zero value formatting as `00:00:00:00:00:00`, and only supporting MAC-48. Tests cover hashability, parsing, invalid lengths, string form, and tuple accessors.
