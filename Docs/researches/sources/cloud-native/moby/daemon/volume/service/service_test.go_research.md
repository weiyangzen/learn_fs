# sources/cloud-native/moby/daemon/volume/service/service_test.go

## Purpose
Unit tests for high-level `VolumesService` behavior.

## Important APIs, Types, And Functions
Tests cover `Create`, `List`, `Remove`, `Get`, `Prune`, and test service construction with `dummyEventLogger`.

## Control Flow
Create tests verify unknown driver not-found, idempotent same-driver create, cross-driver name conflict, and recreate after remove. List tests cover driver and dangling filters with references. Remove tests cover normal removal and purge-on-error not-found. Get tests cover missing volumes, status resolution, driver conflict, and correct driver matching. Prune tests cover label/all filters, default local-only behavior, non-local preservation, anonymous-label defaulting, label exclusion, and referenced volume preservation.

## State And Persistence
Uses temporary metadata stores and fake drivers; no real local driver except in Linux-specific test.

## Dependencies And Integration Points
Exercises service, store, filters, options, error classification, event logging interface, and fake drivers.

## Risks
Event logger output is not asserted. Prune size accounting is not deeply validated here; Linux size test covers usage data separately.

## Test Signals
Strong API-level signal for conflict semantics, filter conversion, reference-aware pruning, and status retrieval.
