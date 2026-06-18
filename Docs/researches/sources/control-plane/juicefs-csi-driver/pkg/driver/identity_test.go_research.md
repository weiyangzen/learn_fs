# sources/control-plane/juicefs-csi-driver/pkg/driver/identity_test.go

Purpose: unit-tests the CSI Identity methods.

Important APIs and functions: `TestDriver_GetPluginInfo` checks that the response contains `config.DriverName` and the default empty vendor version in test builds. `TestGetPluginCapabilities` asserts the single `CONTROLLER_SERVICE` plugin capability. `TestDriver_Probe` asserts an empty successful `ProbeResponse`.

Control flow: each test constructs a minimal `Driver` value and calls the identity method directly without a gRPC server.

State and persistence behavior: no persistent state. Tests read package globals such as `driverVersion`.

Dependencies and integration points: depends on CSI protobufs, `grpc.Server` type only for struct field shape, Go's `reflect.DeepEqual`, and `config.DriverName`.

Risks and test signals: good regression signal for advertised identity constants. It does not cover logging, nil request handling beyond the tested values, or build-time version injection.
