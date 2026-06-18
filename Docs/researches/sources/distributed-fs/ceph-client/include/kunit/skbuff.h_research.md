<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/skbuff.h -->
# sources/distributed-fs/ceph-client/include/kunit/skbuff.h

## Purpose
`skbuff.h` adds KUnit-managed `struct sk_buff` allocation and release helpers for network tests.

## Important APIs, types, and functions
`kunit_action_kfree_skb()` is the cleanup adapter passed to KUnit deferred actions. `kunit_zalloc_skb()` allocates an skb with `alloc_skb()`, pads/zeroes the requested length with `skb_pad()`, and registers automatic cleanup with `kunit_add_action_or_reset()`. `kunit_kfree_skb()` releases an skb early by invoking `kunit_release_action()`.

## Control flow
Allocation returns `NULL` if `alloc_skb()` fails, if padding fails, or if action registration fails. When action registration fails, `kunit_add_action_or_reset()` runs the cleanup action immediately, preventing a leak. Early free calls are no-ops for `NULL` and otherwise execute and remove the matching deferred action.

## State and persistence behavior
The skb itself is normal network-stack state, but its lifetime is recorded in the test's KUnit resource/action list. No persistent state is stored in the header.

## Dependencies and integration points
This helper depends on `kunit/resource.h` and `<linux/skbuff.h>`. It integrates KUnit cleanup semantics with networking tests that allocate packets, avoiding manual teardown paths when assertions abort.

## Risks and test signals
Risks include assuming `kunit_zalloc_skb()` initializes more than the padded data area, using the skb after `kunit_kfree_skb()`, and registering the same skb through another cleanup path. Test signals are skb allocation tests that abort early and still free memory, explicit early free tests, and fault-injection tests for allocation/action registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/skbuff.h -->
