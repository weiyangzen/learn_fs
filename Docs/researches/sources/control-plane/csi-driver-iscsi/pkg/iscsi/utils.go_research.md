## sources/control-plane/csi-driver-iscsi/pkg/iscsi/utils.go

Purpose: utility constructors and middleware for the iSCSI CSI server.

APIs include `NewDefaultIdentityServer`, `NewControllerServer`, `NewControllerServiceCapability`, `ParseEndpoint`, and `logGRPC`. `ParseEndpoint` accepts `unix://` or `tcp://` prefixes and returns protocol/address when the address is non-empty. `logGRPC` logs method names at V(3), sanitized requests/responses at V(5), and errors.

State is none. Dependencies include CSI types, csi-lib-utils `protosanitizer`, grpc interceptors, klog, and strings/fmt. Risks include endpoint parsing that accepts arbitrary proto case as returned from input, no support for Windows named pipes or bare Unix paths, and possible log volume/noise at high verbosity. Test signal is indirect through server startup and logging behavior.
