# Research: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset.go

Purpose: implements an address set over `netip.Prefix` using one or more bitmaps, including huge IPv6 ranges. Important types/APIs are `AddrSet`, `New`, `Add`, `AddAny`, `AddAnyInRange`, `Remove`, `Len`, `AddrsInPrefix`, `String`, and errors `ErrNotAvailable`/`ErrAllocated`.

Control flow: `New` masks the pool and initializes bitmap storage. `Add` validates containment, locates/creates the relevant bitmap, computes host offset, and sets the bit. `AddAny` allocates from the first bitmap; `AddAnyInRange` validates the requested subrange and allocates either whole-bitmap or subrange bits. `Remove` unsets the bit and deletes empty bitmaps. `Len` returns a 128-bit count split into high/low uint64 values; `AddrsInPrefix` counts selected bits that overlap a prefix.

State/dependencies: state is in-memory bitmap maps keyed by prefix. Dependencies include internal `bitmap`, `ipbits`, `netiputil`, and math/bits. Risks include no internal locking, `AddAny` only searching the first bitmap for pools larger than 2^63 addresses, and panic on impossible `OnesCount` errors. Tests cover IPv4, IPv6, full pools, invalid pools, and >64-bit counts.
