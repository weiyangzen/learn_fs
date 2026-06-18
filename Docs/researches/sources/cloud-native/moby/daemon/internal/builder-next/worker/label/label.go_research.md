# sources/cloud-native/moby/daemon/internal/builder-next/worker/label/label.go

## Purpose
Defines Moby BuildKit worker label keys.

## APIs, Control Flow, and Integration
The package exposes `HostGatewayIP`, under prefix `org.mobyproject.buildkit.worker.moby.`, mirroring BuildKit-style worker labels. It has no functions; callers use the constant to advertise host-gateway IP capability/configuration.

## State, Dependencies, and Risks
No state or dependencies beyond package constants. Compatibility risk is label-key stability, since labels may be consumed by frontends or diagnostics. Tests are not present; correctness is by convention and integration.
