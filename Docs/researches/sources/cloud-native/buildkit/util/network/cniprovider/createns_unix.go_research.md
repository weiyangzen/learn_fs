## sources/cloud-native/buildkit/util/network/cniprovider/createns_unix.go

Purpose: unsupported non-Linux, non-Windows CNI namespace stubs.

Important functions: `createNetNS`, `setNetNS`, `unmountNetNS`, and `deleteNetNS` all return unsupported errors; `cleanOldNamespaces` is a no-op.

State/persistence: none. Dependencies: OCI spec type and `pkg/errors`.

Integration points: compile-time platform fallback for Unix systems without implemented netns support. Risks: selecting CNI provider on these platforms will fail at namespace creation rather than provider construction. Test signals: no local tests.
