# sources/cloud-native/containerd/core/runtime/v2/logging/logging.go

## Purpose
Defines the common runtime v2 external logging driver contract used by platform-specific launcher helpers.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Config` carries container ID, namespace, stdout reader, and stderr reader. `LoggerFunc` is the callback signature implemented by a logging binary; it receives a context, config, and `ready` callback that must be invoked once setup is complete so the container can start.

There is no control flow or persistence in this common file. State is caller-provided stream handles and identity fields. Platform files implement `Run`.

Dependencies are only `context` and `io`. Integration points are external logging binaries and shim code that launches them with container IO and wait synchronization.

Risks include logger implementations forgetting to call `ready`, mishandling stream lifetime, or blocking startup. Test signals come from platform-specific `Run` tests and integration tests launching a logger binary through the shim.
