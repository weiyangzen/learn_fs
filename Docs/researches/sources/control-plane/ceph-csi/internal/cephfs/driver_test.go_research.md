## sources/control-plane/ceph-csi/internal/cephfs/driver_test.go

Purpose: Unit/integration-style test for CSI-Addons server setup.

Important flow: `TestSetupCSIAddonsServer` creates a temporary Unix socket endpoint, builds a minimal `util.Config`, invokes `drv.setupCSIAddonsServer`, asserts no error and non-nil server, checks the socket path exists, then stops the server.

State and dependencies: Uses a temp directory and creates a local Unix socket. Depends on the CSI-Addons server implementation and filesystem socket support; it does not contact Ceph.

Risks and signal: Provides a concrete signal that addon server initialization and service registration are viable with minimal config. It does not validate full `Run`, controller/node setup, or error cases for invalid endpoints. Parallel execution is safe because each test owns a temp socket.
