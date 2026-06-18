<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_linux.go -->
# sources/cloud-native/cri-o/server/container_update_resources_linux.go

## Purpose

This Linux-specific file validates memory limit decreases before applying container resource updates.

## Important APIs, Types, and Functions

`validateMemoryUpdate(ctx, c, newMemoryLimit)` checks negative limits, treats zero as unlimited, reads current stats through `StatsForContainer`, and rejects limits below current memory usage.

## Control Flow

Negative limits return an error. Zero returns success. The function resolves the sandbox; if missing, it logs a warning and allows the update. It retrieves stats; if stats or usage bytes are missing, it logs and allows the update. Otherwise it compares the requested limit with current usage and errors if the limit is lower.

## State and Persistence Behavior

No state is mutated. It reads live/container stats and gates the later runtime update in `UpdateContainerResources`.

## Dependencies and Integration Points

It integrates with sandbox lookup, stats generation, CRI memory usage fields, logging, and the main resource update flow.

## Risks and Edge Cases

Validation is best-effort: missing sandbox or stats allows potentially unsafe decreases. Current usage can change after validation before runtime update, so this is not a hard race-free guarantee. Negative limits are always rejected.

## Test Signals

No direct tests in this subset cover memory validation. Resource update tests exercise the caller but not below-current-usage rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_linux.go -->
