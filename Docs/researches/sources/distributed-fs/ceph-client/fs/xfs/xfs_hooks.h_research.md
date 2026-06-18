# sources/distributed-fs/ceph-client/fs/xfs/xfs_hooks.h

## Purpose
`xfs_hooks.h` declares the optional XFS live hook abstraction and its compile-time no-op fallback. The complete 65-line header was read.

## Important APIs, Types, and Functions
When `CONFIG_XFS_LIVE_HOOKS` is enabled, `struct xfs_hooks` wraps `struct blocking_notifier_head`, and `struct xfs_hook` embeds `struct notifier_block` as its first member. `xfs_hook_setup` initializes the callback and priority. The header declares `xfs_hooks_init`, `xfs_hooks_add`, `xfs_hooks_del`, and `xfs_hooks_call`.

The static-key helpers `DEFINE_STATIC_XFS_HOOK_SWITCH`, `xfs_hooks_switch_on`, `xfs_hooks_switch_off`, and `xfs_hooks_switched_on` let hook sites skip notifier overhead when no hooks are active. Without the config option, hooks are empty/no-op and calls return `NOTIFY_DONE`.

## Control Flow
Feature code can guard hook calls with the static branch and then dispatch a notifier chain. Registration paths can turn the branch on and off around adding or removing hooks. In no-op builds the same call sites compile away to minimal code.

## State and Persistence Behavior
All state is runtime-only: notifier heads, hook objects, and static keys. The file defines no persistent XFS data format.

## Dependencies and Integration Points
The header integrates with Linux static keys, jump labels, blocking notifier chains, and XFS live hook users. The comment explicitly warns that static key patching takes the CPU hotplug lock, so callers must consider memory reclaim/writeback lock interactions when enabling/disabling hooks.

## Risks and Edge Cases
The first-member layout of `struct xfs_hook` is part of the ABI between XFS wrappers and notifier code. Static key toggling in the wrong lock context can deadlock with CPU hotplug or memory reclaim. No-op builds must preserve source compatibility for call sites that expect hook APIs to exist.

## Test Signals
Build coverage should include both config paths. Runtime checks should verify static-branch state tracks hook registration, hook callbacks receive action and private data, and no-op builds return `NOTIFY_DONE` without needing notifier storage.
