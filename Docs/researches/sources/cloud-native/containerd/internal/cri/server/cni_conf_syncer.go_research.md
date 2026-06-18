# sources/cloud-native/containerd/internal/cri/server/cni_conf_syncer.go

## Purpose

This file watches the CNI configuration directory and reloads the CNI plugin configuration when relevant filesystem changes occur.

## Important APIs, Types, and Functions

`cniNetConfSyncer` stores a watcher, CNI plugin, load options, config directory, and last sync status protected by an RW mutex. `newCNINetConfSyncer` creates directories, starts watching, loads initial config, and stores initial errors. `syncLoop` processes fsnotify events and reloads CNI config. `lastStatus`, `updateLastStatus`, and `stop` expose status and shutdown.

## Control Flow

Construction creates the parent directory with `0755` for rootless CNI tuning compatibility, creates the config dir with `0700`, adds a watcher, and attempts initial load. `syncLoop` ignores chmod/create events, reloads on other changes, returns an error if the watched directory is removed/renamed, records reload errors, and exits on watcher errors or closed channels.

## State and Persistence Behavior

It creates CNI config directories if missing and stores last reload error in memory. It does not persist status. The watcher is an OS resource closed by `stop`.

## Dependencies and Integration Points

It depends on `github.com/containerd/go-cni`, `fsnotify`, containerd logging, and CRI server networking setup.

## Risks and Edge Cases

Reloading on broad event categories may do redundant work. Ignoring create events means a newly created file may not trigger immediate reload until a write/rename occurs, depending on editor behavior. Removal of the config directory stops the loop. Last status must be read under lock.

## Test Signals

Tests should cover initial load failure recording, reload on write/rename/remove, ignored chmod/create, directory removal exit, watcher error exit, and `stop` closing the watcher.
