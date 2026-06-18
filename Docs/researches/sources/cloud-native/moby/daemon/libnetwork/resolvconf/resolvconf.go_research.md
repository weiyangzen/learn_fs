<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolvconf/resolvconf.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolvconf/resolvconf.go

Purpose: public compatibility wrapper exposing the host `resolv.conf` path helper.

Important APIs/functions: `Path() string` returns `internal/resolvconf.Path()`.

Control flow: direct delegation only.

State and persistence: no state. It reports whichever path the internal resolver-conf package determines for the host.

Dependencies and integration points: used outside the internal package boundary, with a FIXME noting it should eventually be removed or moved. It bridges libnetwork internals to daemon setup code.

Risks and test signals: the file exists to avoid import-boundary problems. Risk is API persistence: consumers may keep depending on this wrapper. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolvconf/resolvconf.go -->
