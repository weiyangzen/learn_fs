# sources/control-plane/ceph-csi/internal/nvmeof/tests/nvmeof_test.go

Purpose: Environment-gated integration test for the real NVMe-oF gateway client.

Important APIs/types/functions: `TestRealGateway` uses `nvmeof.NewGatewayRpcClient`, `CreateSubsystem`, `AddHost`, `SubsystemExists`, `CreateListener`, `DeleteListener`, `RemoveHost`, `DeleteSubsystem`, and `Destroy`.

Control flow: The test skips in short mode and skips when required environment variables are missing. It creates a gateway client from env-provided management endpoint, sets up cleanup in reverse order, then exercises subsystem create, host add, subsystem exists, listener create/delete, host remove, subsystem delete, and final absence check. Namespace create/delete are present but commented out.

State and persistence behavior: Mutates a real gateway using fixed test NQN and host NQN. Cleanup attempts to remove host, listener, subsystem, and close the client even if assertions fail.

Dependencies and integration points: Requires live NVMe-oF gateway address/port/hostname/listener port. Uses `testify/require` and production gateway client.

Risks: Fixed test identifiers can collide across concurrent integration runs. The test skips rather than fails without environment, so CI may not cover gateway integration. Namespace behavior, QoS, auto-listeners, DH-CHAP, and RBD-backed namespace creation are not exercised.

Test signals: Useful smoke test for gateway CRUD basics when explicitly configured. Limited default CI signal.
