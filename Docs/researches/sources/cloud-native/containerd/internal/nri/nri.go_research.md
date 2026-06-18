# sources/cloud-native/containerd/internal/nri/nri.go

## Purpose
Implements containerd's generic NRI API adapter, forwarding pod/container lifecycle events to NRI plugins and applying plugin-requested updates or evictions through registered domains.

## Important APIs, Types, And Functions
`API` defines lifecycle methods. `local` owns config, adaptation instance, mutex, and per-ID state map. `New`, `Start`, `Stop`, lifecycle methods, `syncPlugin`, `updateFromPlugin`, `applyUpdates`, `evictContainers`, and state helpers implement the adapter.

## Control Flow
If disabled, most methods no-op. Enabled methods serialize under `local.Lock`, convert pod/container metadata to NRI requests, call adaptation APIs, update local state, and apply/evict additional plugin requests. Plugin sync lists all domains, seeds state, calls the plugin sync callback, and applies returned updates.

## State And Persistence
In-memory `state` tracks Created/Running/Stopped/Removed to avoid duplicate stop/remove events. No state persists across restart; plugin sync rebuilds from domains.

## Dependencies And Integration Points
Integrates containerd version info, logging, NRI adaptation, domain registry, metrics/config options, and namespace-specific domain implementations.

## Risks
All lifecycle calls are serialized, so slow plugins or domain updates can block other NRI events. Several update/eviction failures are logged and ignored by design. `NotifyContainerExit` launches a goroutine using the caller context.

## Test Signals
No direct tests in this subset. Metrics tests and domain/conversion integration elsewhere provide indirect coverage.
