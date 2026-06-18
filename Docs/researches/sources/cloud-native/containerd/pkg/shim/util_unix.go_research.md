<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix.go -->
# sources/cloud-native/containerd/pkg/shim/util_unix.go

## Purpose
Unix shim socket and dial utility implementation.

## Important APIs, Types, And Functions
getSysProcAttr, AdjustOOMScore, SocketAddress, CreateSocketAddress, AnonDialer, AnonReconnectDialer, NewSocket, RemoveSocket, SocketEaddrinuse, CanConnect, vsock/hybrid-vsock dialers, writeSocketDir, and cleanupSockets are key APIs.

## Control Flow
Addresses are parsed as unix, vsock, hybrid-vsock, or abstract Unix. Socket addresses are hashed from namespace/socketPath/id/debug. NewSocket creates directories and chmods filesystem sockets. cleanup removes recorded and derived sockets.

## State And Persistence
Creates socket files, socket directory symlink s, and may adjust kernel OOM score. Uses hashed socket names under state dir to avoid path length issues.

## Dependencies And Integration Points
Depends on defaults, namespaces, pkg/sys OOM helpers, mdlayher/vsock, net, and filesystem APIs. Used by daemon/shim connection setup.

## Risks And Edge Cases
Abstract socket detection treats unprefixed addresses as abstract. Hybrid-vsock handshake retries EOF until timeout. cleanup falls back to default state dir if symlink is missing.

## Test Signals
util_unix_test and util_abstract_test cover filesystem and abstract sockets; OOM behavior is covered in pkg/sys tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix.go -->
