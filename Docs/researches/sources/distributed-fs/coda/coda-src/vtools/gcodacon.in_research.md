# sources/distributed-fs/coda/coda-src/vtools/gcodacon.in

## Purpose

`gcodacon.in` is a Python/GTK graphical monitor for Coda client volume and reintegration state. It listens to Venus mariner `volstate` events, displays per-volume state in a GTK tree, changes the application icon, and optionally emits desktop notifications.

## Important APIs, Types, and Functions

`State` defines state descriptions, notification urgency, colorized XPM icon variants, and predicates over CML count plus flags. `parse_codaconf()` reads `/etc/coda/venus.conf`. `MarinerListener` connects to the mariner socket or TCP service, sends `set:volstate`, and dispatches complete lines. `VolumeList` wraps `Gtk.ListStore` with state lookup/update helpers. `VolumeView` renders icon, realm, volume, and state columns. `GlobalState` throttles notifications via `NOTIFICATION_INTERVAL`. `App` wires the mariner listener to GTK widgets, filters clean volumes, handles context menu actions, parses `volstate::...` messages, and computes aggregate status.

## Control Flow

Startup parses CLI options, builds the GTK UI, optionally starts a test timer, otherwise initializes the mariner connection. Mariner reconnect attempts run through GLib timeouts. Readable socket events append bytes to `self.buf`, split newline-delimited messages, update volume rows, then recompute global state and notifications. Right-click opens a menu for dirty-only filtering, notifications, about, and quit.

## State and Persistence Behavior

Runtime state lives in GTK models, the current global state, pending notification messages, and the socket buffer. There is no durable persistence. It reads `venus.conf` to locate the Unix socket and consumes live mariner data.

## Dependencies and Integration Points

It depends on Python GI bindings for Gtk 3, Gdk, GdkPixbuf, GLib, GObject, and Notify; Venus mariner protocol; `/etc/coda/venus.conf`; and service name `venus` for TCP mode. The script template uses `@PYTHON@` substitution.

## Risks

`VolumeList.values()` uses `STATES(row[1])` instead of indexing and appears broken if called. In `App.data_ready()`, `self.vols.__delitem__(vol)` is subject to Python name mangling inside the `App` class and should be `del self.vols[vol]`; deleted-volume events can fail. `parse_codaconf()` does not close files explicitly and handles only simple unescaped quoted values. Mariner bytes are decoded as ASCII, so non-ASCII paths can fail. Socket reconnects do not close failed sockets in all paths. The deprecated status-icon menu callback code suggests GTK API drift risk.

## Test Signals

Tests should cover state-priority ordering, each `volstate` regex branch, dirty-only filtering, deleted-volume handling, mariner reconnect behavior, notification throttling, config parsing, ASCII decode failures, and `--test` state cycling. Manual tests need a running Venus and desktop notification daemon.
