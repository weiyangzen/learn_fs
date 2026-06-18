# sources/distributed-fs/ceph-client/include/linux/rcuwait_api.h

## Purpose

This one-line compatibility header includes `linux/rcuwait.h`. It exists so users that include the `_api` name receive the same `rcuwait` declarations without duplicating definitions.

## Important APIs, Types, and Functions

It defines no symbols directly. All APIs, including `struct rcuwait`, `rcuwait_init()`, `rcuwait_wake_up()`, `rcuwait_wait_event()`, and timeout helpers, come from `rcuwait.h`.

## Control Flow

There is no control flow in this file beyond preprocessing include resolution.

## State and Persistence Behavior

The file has no state. Runtime behavior is entirely inherited from `rcuwait.h`.

## Dependencies and Integration Points

Its only dependency and integration point is `#include <linux/rcuwait.h>`. It is useful for source compatibility where include naming changed or generated imports target the API wrapper.

## Risks

The only practical risk is assuming this header is an independent API surface. Any semantic change comes from `rcuwait.h`.

## Test Signals

Build coverage that includes `rcuwait_api.h` instead of `rcuwait.h` is sufficient; runtime testing belongs to `rcuwait.h`.
