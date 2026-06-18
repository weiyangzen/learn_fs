# sources/distributed-fs/ceph-client/net/core/skb_fault_injection.c

## Purpose

`skb_fault_injection.c` adds a fault-injection hook for skb head reallocation. It allows tests to force `pskb_expand_head()` from `skb_might_realloc()` according to standard Linux fault-injection attributes, optionally filtered by network device name. This helps exercise paths that must tolerate skb data/head pointer changes.

## Important APIs, Types, And Functions

The file-level `skb_realloc` object stores `struct fault_attr attr`, a device-name buffer, and a `filtered` boolean. `should_fail_net_realloc_skb()` checks the optional device-name filter and then calls `should_fail()` on the configured fault attributes. It is marked with `ALLOW_ERROR_INJECTION()`.

`skb_might_realloc()` is the exported hook. If `should_fail_net_realloc_skb()` returns true, it calls `pskb_expand_head(skb, 0, 0, GFP_ATOMIC)`, forcing skb head reallocation without requesting additional headroom or tailroom.

`fail_skb_realloc_setup()` wires the boot parameter `fail_skb_realloc=` into `setup_fault_attr()`. `fail_skb_realloc_debugfs()` creates a debugfs fault-injection directory named `fail_skb_realloc` and adds a `devname` file. `devname_write()` resets settings, copies a user-provided name, trims a trailing newline or whitespace, and enables filtering when non-empty. `devname_read()` returns the active filter name or EOF when unfiltered.

## Control Flow

At boot, the `__setup()` handler can initialize fault attributes from the kernel command line. During late init, debugfs controls are created through `fault_create_debugfs_attr()` and `debugfs_create_file()`.

Runtime callers invoke `skb_might_realloc(skb)` at points where tests want to simulate possible skb reallocation. The function checks the device filter first; when filtering is enabled, only matching `skb->dev->name` can trigger. It then checks the fault-injection policy. On a selected hit, it calls `pskb_expand_head()` in atomic allocation context.

Users can update the device filter by writing to debugfs. Each write clears the previous filter, copies up to `IFNAMSIZ`, null-terminates, trims, and sets `filtered` according to whether the resulting string is non-empty.

## State And Persistence Behavior

Fault policy, filter name, and filter enablement are static kernel-memory state. They can be initialized from the boot command line and adjusted at runtime through debugfs. They do not persist across reboot. The exported hook mutates the passed skb by potentially reallocating its head; callers must assume skb data pointers may be invalidated after the call.

## Dependencies And Integration Points

This file depends on `CONFIG_FAULT_INJECTION` style helpers, debugfs, skb memory helpers, and netdevice naming. It exports `skb_might_realloc()` for other networking code to place reallocation fault points. Test automation can control frequency/probability through the standard fault-injection debugfs attributes plus the custom `devname` filter.

## Risks And Edge Cases

`should_fail_net_realloc_skb()` assumes `skb->dev` is valid because it immediately reads `skb->dev->name`. Callers must not use this hook on skbs without a device unless they first guard that condition.

`skb_might_realloc()` ignores the return value of `pskb_expand_head()`. This is acceptable for a fault-injection perturbation hook whose purpose is to trigger reallocation when possible, but tests should not interpret it as guaranteed reallocation.

The debugfs filter is global and unsynchronized beyond simple writes/reads to static storage. Concurrent filter updates and hook calls can race at string-comparison granularity, which is typical for debug/test controls but unsuitable as a production policy mechanism.

## Test Signals

Tests should verify boot-parameter parsing, debugfs creation, unfiltered and filtered triggering, newline trimming in `devname`, EOF reads when unfiltered, and that callers tolerate skb head/data pointer changes after `skb_might_realloc()`. Negative tests should include nonmatching device filters and disabled fault attributes.
