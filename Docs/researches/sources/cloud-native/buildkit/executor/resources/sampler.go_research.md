# Research: sources/cloud-native/buildkit/executor/resources/sampler.go

## Purpose
Generic adaptive sampling utility.

## Important APIs, Types, and Functions
`WithTimestamp`, `Sampler[T]`, `Sub[T]`, `NewSampler`, `Record`, `run`, `Sub.Close`, `Sampler.Close`.

## Control Flow
A goroutine ticks at a minimum interval, calls a callback once per active tick, appends samples, and increases subscriber intervals to bound sample count; close downsamples and can capture a final sample.

## State and Persistence
In-memory subscriber map and sample/error fields.

## Dependencies and Integration Points
Depends on sync/time only. Used by cgroup and system resource samplers.

## Risks and Edge Cases
Concurrency around close vs sample callback and error propagation is important.

## Test Signals
Indirect tests through resource monitor behavior.
