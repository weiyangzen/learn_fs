# sources/distributed-fs/ceph/src/mon/FSCommands.cc

## Purpose
`FSCommands.cc` implements CephFS monitor command handlers used by `MDSMonitor` to mutate `FSMap` and related OSD pool application metadata. It covers filesystem creation/removal/reset/rename/swap, pool attachment/removal, filesystem option updates, compatibility bits, required client features, mirroring flags/peers, and destructive fail paths.

## Important APIs, Types, and Functions
The file defines concrete `FileSystemCommandHandler` subclasses for `fs new`, `fs set`, `fs fail`, `fs rm`, `fs reset`, `fs rename`, `fs swap`, data-pool add/remove, compat changes, required client features, default FS selection, global flags, and mirroring. Shared helpers are `FileSystemCommandHandler::load`, `_check_pool`, `is_op_allowed`, `set_val`, and local `modify_filesystem`.

## Control Flow
`MDSMonitor::prepare_command()` iterates handlers returned by `load()`. `can_handle()` matches the prefix and validates per-filesystem write caps except for global `fs new` and `fs flag set`. Handler methods validate arguments, mutate pending `FSMap`, and sometimes request OSDMonitor proposals. Pool-affecting and blocklisting paths wait for OSDMap writeability and retry with `-EAGAIN`.

## State and Persistence
The file does not persist directly. It mutates pending `FSMap` state later encoded by `MDSMonitor`, and delegates OSD pool application tags, metadata-pool options, and blocklists to `OSDMonitor`.

## Dependencies and Integration Points
It integrates with `Monitor`, `MDSMonitor`, `OSDMonitor`, `MgrStatMonitor`, `Paxos`, `FSMap`, `Filesystem`, `MDSMap`, `OSDMap`, command parsing, and CephFS feature conversion.

## Risks
Destructive operations depend on confirmation flags and correct offline/refuse-client/mirroring checks. `_check_pool()` is safety-critical for rejecting unsafe pool reuse or unsuitable EC/cache-tier layouts. `set_val()` spans many MDSMap fields and must preserve old snapshot, standby replay, and deprecated-setting semantics.

## Test Signals
Cover every command prefix, cap filtering, idempotency, OSD writeability retry, pool validation, confirmation gates, `fs new` option setting, app-tag updates, feature add/remove, mirror peer duplicate handling, and health-warning refusal.
