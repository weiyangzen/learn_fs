# sources/cloud-native/buildkit/client/client_cdi_test.go

## Purpose

This file tests BuildKit client/LLB integration with CDI devices. It verifies device injection, allow/deny behavior, entitlement-based access, shorthand device selection, wildcard selection, class selection, and CDI spec discovery refresh.

## Important APIs, Types, and Functions

- `cdiTests` lists CDI integration test functions for registration elsewhere.
- `testCDI`, `testCDINotAllowed`, `testCDIEntitlement`, `testCDIFirst`, `testCDIWildcard`, and `testCDIClass` cover CDI behavior variants.
- `cdiSpecFile` describes a temporary CDI spec fixture.
- `writeCDISpecFile` atomically writes CDI spec YAML files and waits for workers to report matching devices.

## Control Flow and State

Each test skips rootless and Windows, requires `FeatureCDI`, creates a client, writes one or more CDI spec files into the sandbox's CDI spec directory, and builds an LLB graph that requests CDI devices via `llb.AddCDIDevice`. Tests export local output files containing environment variables injected by CDI container edits, then assert expected variables are present or absent.

`testCDI` uses autoallowed devices from two vendors plus an optional missing device. `testCDINotAllowed` omits autoallow and expects a denial. `testCDIEntitlement` grants `device=vendor1.com/device` and expects success. `testCDIFirst` requests a kind without a name and expects the first selected device behavior expressed by current CDI ordering. `testCDIWildcard` requests all devices of a kind. `testCDIClass` requests devices by class annotation.

`writeCDISpecFile` writes files using `continuity.AtomicWriteFile`, records expected kinds, and polls `ListWorkers` until reported CDI devices include all kinds or a timeout expires.

## Dependencies and Integration Points

The tests depend on CDI spec YAML semantics, BuildKit LLB CDI device options, worker CDI discovery and caching, integration sandbox CDI directories, local export, `ListWorkers`, and feature-gated worker capabilities.

## Risks and Edge Cases

Spec discovery is asynchronous, so the helper uses polling with a five-second deadline. Rootless and Windows skips mean behavior there is not covered. Autoallow depends on BuildKit-specific `org.mobyproject.buildkit.device.autoallow` annotations. The "first" selection test encodes current ordering expectations and could be sensitive to CDI library ordering changes.

## Test Signals

These tests provide the CDI-specific signal for client solves and worker device reporting. They do not directly test gateway container APIs, but they verify LLB solve behavior through the public client.
