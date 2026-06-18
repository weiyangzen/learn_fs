# sources/control-plane/ceph-csi/internal/nvmeof/controller/controllerserver_test.go

Purpose: Provides unit coverage for small controller helpers that shape the NVMe-oF CSI contract: host NQN derivation, RBD metadata key naming, volume context serialization, and gateway config extraction.

Important APIs/types/functions: Tests target `getHostNQNFromNodeID`, `toRBDMetadataKey`, `populateVolumeContext`, and `getGatewayConfigFromRequest`. It constructs `csi.Volume` and `nvmeof.NVMeoFVolumeData` values and validates serialized listeners with `encoding/json`.

Control flow: Table-driven subtests validate success and failure cases. `TestPolulateVolumeContext` builds a complete volume data object, calls the helper, and asserts all relevant volume context keys plus JSON listener fields. Gateway config tests cover missing address, default port behavior, and explicit port parsing.

State and persistence behavior: Tests do not touch persistent RBD metadata or live gateways. They validate in-memory volume context values that later become CSI response state and input to the node server.

Dependencies and integration points: Uses CSI protobuf types, `nvmeof.ListenerDetails`, and `testify/require`. These tests guard key compatibility between controller output and node-server input.

Risks: Coverage is helper-focused and does not assert cleanup behavior, metadata store/retrieve symmetry, or error-code mappings. There is a duplicate host NQN test case and the test name has a typo (`Polulate`), both low functional risk but signs of narrow coverage.

Test signals: Positive signal for serialization and input validation. Missing signal for gateway RPC orchestration and RBD manager interactions.
