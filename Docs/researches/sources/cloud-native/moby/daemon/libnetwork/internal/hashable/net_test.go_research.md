# Research: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net_test.go

Purpose: verifies hashable MAC/IP tuple helpers. Important tests are compile-time map-key assertions, `TestMACAddrFrom6`, `TestMACAddrFromSlice`, `TestParseMAC`, `TestMACAddr_String`, and `TestIPMACFrom`.

Control flow: tests assert MAC packing/unpacking, reject invalid slice lengths, parse valid and too-long MAC strings, check string formatting including zero value, and confirm `IPMAC` stores and returns the given IP and MAC. Compile-time variables ensure `MACAddr` and `IPMAC` remain comparable.

State/dependencies: no external state. Dependencies are `net`, `netip`, and `gotest.tools`. Risks covered include MAC-48 enforcement, stable string formatting, and tuple accessor correctness. Gaps include unusual accepted `net.ParseMAC` formats, invalid textual MACs other than too-long values, and mutation safety of returned slices.
