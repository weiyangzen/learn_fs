# Research: sources/cloud-native/buildkit/executor/resources/sys.go

## Purpose
Public system sampler constructor wrapper.

## Important APIs, Types, and Functions
`SysSampler` alias and `NewSysSampler` platform-dispatched constructor.

## Control Flow
Returns the platform sampler for host-level resource samples.

## State and Persistence
No state beyond returned sampler.

## Dependencies and Integration Points
Depends on resource system types and platform files. Used by monitoring/reporting code needing host samples.

## Risks and Edge Cases
Availability differs by platform.

## Test Signals
Platform build coverage.
