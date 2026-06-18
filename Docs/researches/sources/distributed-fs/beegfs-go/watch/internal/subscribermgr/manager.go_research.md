# sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/manager.go

## Purpose

This file manages the set of active subscriber handlers and applies dynamic subscriber configuration changes. It adds, removes, restarts, and shuts down handlers while preserving event-buffer cursors when appropriate.

## Important APIs, Types, And Functions

`Manager` stores logger, handler slice, shared metadata event buffer, and wait group. `New` constructs it and tags the logger. `Configurer` defines the app-config view needed for subscriber updates. `UpdateConfiguration` validates new subscribers, evaluates additions/removals/verifications, stops old handlers, removes cursors for deleted subscribers, swaps handlers for changed config, and starts new handler goroutines. `evaluateAddedAndRemovedSubscribers` computes ID maps. `Manage` waits for global shutdown and stops all handlers.

## Control Flow

On every config update, new subscriber configs are fully parsed first. Removed handlers are stopped and locked before cursor removal. Existing handlers with changed subscriber config or handler config are stopped, locked, replaced, and restarted. New subscribers get new handlers and goroutines. Shutdown simply calls `Stop` on all handlers and leaves wait-group completion to each handler.

## State And Persistence

Manager state is the in-memory handler slice. Cursor lifetime is tied to subscriber presence: updated subscribers keep cursors to avoid dropping events during config changes, while removed subscribers have cursors removed. There is no persisted subscriber list beyond the external config source.

## Dependencies And Integration Points

It implements `configmgr.Listener`, receives `config.AppConfig` through the `Configurer` interface, uses `subscriber.NewSubscribersFromConfig`, and coordinates with `types.MultiCursorRingBuffer` plus the shared application wait group from `main.go`.

## Risks And Test Signals

The handler mutex is intentionally locked during replacement/removal and not unlocked because the old handler is discarded; this is unusual but documented. Duplicate subscriber IDs in the new config are not explicitly rejected and map-based diffing would collapse them. `Manage` does not wait itself after stopping handlers; the shared wait group handles that. Unit tests cover diffing, but update/restart/cursor behavior needs integration tests.
