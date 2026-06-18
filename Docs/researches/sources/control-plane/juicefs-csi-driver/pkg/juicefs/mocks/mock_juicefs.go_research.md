# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mocks/mock_juicefs.go

Purpose: generated GoMock implementation of the high-level `juicefs.Interface` used by driver/controller/node tests.

Important APIs and types: `MockInterface` mocks all JuiceFS provider and embedded mount operations, including `AuthFs`, snapshot methods, `CreateTarget`, `GetSubPath`, `JfsCreateVol`, `JfsDeleteVol`, `JfsMount`, `JfsUnmount`, `SetQuota`, `Settings`, `Status`, and Kubernetes mount `Mount`/`Unmount` methods. Recorder methods expose typed expectations for each call.

Control flow: each method calls the GoMock controller with arguments and casts configured return values. There is no business logic.

State and persistence behavior: no external state. Call state is retained in the mock controller.

Dependencies and integration points: used by CSI controller and node tests to decouple service logic from actual JuiceFS, Kubernetes, and mount side effects.

Risks and test signals: generated code must match the current `juicefs.Interface`; if the interface changes, stale mocks can cause compile failures or tests that no longer cover new methods. Mock tests validate call contracts but not real CLI/Kubernetes/mount behavior.
