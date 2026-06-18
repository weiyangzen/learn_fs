<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/named_iplist_opts.go -->
# sources/cloud-native/moby/daemon/internal/opts/named_iplist_opts.go

Purpose: implements a named CLI/config option that appends parsed IP addresses to a referenced `[]netip.Addr`.

Important APIs and types: `NamedIPListOpts`, `NewNamedIPListOptsRef`, `String`, `Set`, `Type`, and `Name`.

Control flow: `Set` parses the value with `netip.ParseAddr` and appends it to the underlying slice. `String` returns `""` for no values or Go's slice formatting otherwise.

State and persistence: mutates the caller-provided slice pointer; no disk persistence.

Dependencies and integration: follows Docker daemon option interfaces and is used for named IP-list settings.

Risks: storing a pointer to a slice means caller lifetime matters. No duplicate filtering or IPv4/IPv6 cardinality validation is applied here.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/named_iplist_opts.go -->
