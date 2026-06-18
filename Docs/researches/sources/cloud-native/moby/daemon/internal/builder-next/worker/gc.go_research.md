# sources/cloud-native/moby/daemon/internal/builder-next/worker/gc.go

## Purpose
Defines default BuildKit cache garbage-collection policy for the Moby worker.

## APIs, Control Flow, and Integration
`DefaultGCPolicy` fills reserved/max/min free-space defaults from disk stats when caller values are zero, falls back to 2GB reserved when disk stats fail, computes a small temporary cache cap, and returns four ordered `client.PruneInfo` rules: prune reproducible local/cache/git entries after 48h over temp cap, prune old unused entries after 60 days, keep unshared cache under the cap, then allow pruning all internal data if needed. `diskPercentage` rounds disk percentage to GB-ish decimal bytes.

## State, Dependencies, and Risks
It reads filesystem disk stats but persists nothing. Risks include surprising `tempCachePercent` value and decimal/gibibyte rounding. The policy directly affects build cache retention and disk pressure behavior; coverage is indirect through daemon/build cache tests.
