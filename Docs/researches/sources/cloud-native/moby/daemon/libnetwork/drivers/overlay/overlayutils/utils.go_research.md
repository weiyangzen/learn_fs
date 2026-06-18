# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils.go

Purpose: Provides overlay utility functions for configuring the global VXLAN UDP port and parsing VNI CSV lists.

Important APIs and functions: `ConfigVXLANUDPPort` sets the package-global VXLAN port, defaulting zero to 4789 and allowing only 1024-49151. `VXLANUDPPort` reads the value under an RW mutex. `AppendVNIList` parses comma-separated uint32 decimal VNI values and appends them to a caller-provided slice.

Control flow: port configuration validates range before taking the write lock. VNI parsing preserves already-appended values on later parse errors.

State and persistence: global in-memory `vxlanUDPPort`; no datastore.

Dependencies and integration points: used by overlay VXLAN creation, firewall matching, encryption, and VNI allocation paths.

Risks: `AppendVNIList` does not enforce the 24-bit VXLAN VNI maximum; ovmanager enforces allocation bounds separately, but direct callers may accept larger values. Global port affects all overlay networks in process.

Test signals: `utils_test.go` covers parsing behavior and allocation count for VNI parsing, but not port configuration.
