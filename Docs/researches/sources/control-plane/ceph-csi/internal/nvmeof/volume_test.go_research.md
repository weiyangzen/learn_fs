# sources/control-plane/ceph-csi/internal/nvmeof/volume_test.go

Purpose: Unit tests for NVMe-oF volume data parsing, listener validation, defaults, and DH-CHAP KMS defaulting.

Important APIs/types/functions: Tests `SetListenersWithDefaults`, `SetupListeners`, and `NVMeoFVolumeData.SetFromParameters`.

Control flow: Listener default tests cover combinations of missing address and port. Listener setup tests cover valid JSON, invalid JSON, missing hostname, empty array, and absent listeners. Parameter tests cover explicit subsystem/gateway/listeners, DH-CHAP with explicit KMS, DH-CHAP with default metadata KMS, invalid port, invalid listeners JSON, and default subsystem NQN from volume ID.

State and persistence behavior: Pure in-memory tests for values later persisted by controller.

Dependencies and integration points: Uses `testify/require`. Guards StorageClass parameter semantics used by controller create.

Risks: Tests do not cover `networkMask` validation, XOR listeners/networkMask validation, or node-side resolution of default `0.0.0.0` listeners.

Test signals: Good coverage for volume parameter model and defaults.
