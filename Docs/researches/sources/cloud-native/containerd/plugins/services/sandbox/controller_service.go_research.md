# sources/cloud-native/containerd/plugins/services/sandbox/controller_service.go

## Purpose
This file implements the gRPC service for sandbox controllers. It multiplexes requests to named sandbox controller plugins and publishes lifecycle events.

## Important APIs, Types, And Functions
The plugin registers gRPC ID `sandbox-controllers` and gathers controllers from both `plugins.PodSandboxPlugin` and `plugins.SandboxControllerPlugin`. `controllerService` implements `api.ControllerServer`. Key RPCs are `Create`, `Start`, `Stop`, `Wait`, `Status`, `Shutdown`, `Metrics`, and `Update`; `getController` validates controller names.

## Control Flow
Initialization builds a map of controller name to `sandbox.Controller`, tolerating missing controller plugin groups but failing if none exist. RPCs validate `Sandboxer`, call the selected controller, translate protobuf values to core `sandbox` and `mount` structures, and convert errors through `errgrpc`. `Create`, `Start`, and `Wait` publish `/sandboxes/create`, `/sandboxes/start`, and `/sandboxes/exit`.

## State And Persistence
The service itself is stateless except for the controller map and event publisher. Durable sandbox state belongs to individual controllers and the sandbox store service.

## Dependencies And Integration Points
It integrates plugin discovery, sandbox core interfaces, protobuf conversion, mount conversion, events exchange, logging, and gRPC registration.

## Risks
Event publication after successful controller operations can return errors after side effects have already happened. `Update` returns a plain error for nil sandbox instead of `errgrpc` conversion. The service trusts controller implementations for persistence, cleanup, metrics shape, and concurrency safety.

## Test Signals
`controller_service_test.go` covers controller lookup errors, request-to-controller option mapping, returned start/status/wait fields, metrics/update delegation, and nil `Extra` normalization.
