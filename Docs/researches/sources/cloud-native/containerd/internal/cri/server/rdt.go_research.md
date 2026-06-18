# sources/cloud-native/containerd/internal/cri/server/rdt.go

## Purpose

This file implements RDT class selection from container and pod annotations when the build includes RDT support.

## Important APIs, Types, and Functions

`(*criService).rdtClassFromAnnotations` calls `rdt.ContainerClassFromAnnotations`, verifies that RDT is enabled before returning a non-empty class, optionally ignores not-enabled errors based on config, and otherwise returns the selected class.

## Control Flow

Annotation parsing happens first. If a class is requested while RDT is disabled, an error is produced unless `IgnoreRdtNotEnabledErrors` is set and RDT is not enabled.

## State and Persistence Behavior

No state is persisted. The returned class is consumed by container creation resource/runtime configuration elsewhere.

## Dependencies and Integration Points

It integrates with `pkg/rdt`, CRI service config, and container creation paths that apply RDT classes.

## Risks and Test Signals

Risks include silently ignoring RDT requests when the ignore flag is enabled and rejecting container creation when host support is absent. Tests should cover annotation precedence and disabled-host behavior.
