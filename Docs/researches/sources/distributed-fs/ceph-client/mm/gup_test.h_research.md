# sources/distributed-fs/ceph-client/mm/gup_test.h

## Purpose

`gup_test.h` defines the user/kernel ABI for the debugfs GUP test driver in `gup_test.c`. It is shared with in-tree user-space selftests, so its ioctl numbers, structure layouts, and flag meanings must remain stable for compatible test binaries.

## Important APIs, Types, and Functions

The header defines ioctl commands with the `'g'` type: `GUP_FAST_BENCHMARK`, `PIN_FAST_BENCHMARK`, `PIN_LONGTERM_BENCHMARK`, `GUP_BASIC_TEST`, `PIN_BASIC_TEST`, `DUMP_USER_PAGES_TEST`, `PIN_LONGTERM_TEST_START`, `PIN_LONGTERM_TEST_STOP`, and `PIN_LONGTERM_TEST_READ`. The benchmark and dump commands use `struct gup_test`; long-term start uses `struct pin_longterm_test`; long-term read accepts a `__u64` user destination address.

`struct gup_test` contains timing outputs (`get_delta_usec`, `put_delta_usec`), input range (`addr`, `size`), batching (`nr_pages_per_call`), raw GUP flags (`gup_flags`), test-specific flags (`test_flags`), and up to `GUP_TEST_MAX_PAGES_TO_DUMP` one-based page indices in `which_pages`. `GUP_TEST_FLAG_DUMP_PAGES_USE_PIN` selects pin vs get behavior for dump mode.

`struct pin_longterm_test` contains an address, size, and flags. `PIN_LONGTERM_TEST_FLAG_USE_WRITE` adds `FOLL_WRITE`; `PIN_LONGTERM_TEST_FLAG_USE_FAST` selects `pin_user_pages_fast()` instead of slow `pin_user_pages()`.

## Control Flow

The header has no runtime control flow, but it shapes ioctl dispatch in `gup_test.c`. `_IOWR` commands copy a structure in and back out, allowing the kernel to return timing and adjusted-size fields. `_IOW` commands copy input only. `PIN_LONGTERM_TEST_STOP` carries no payload and triggers cleanup of the persistent fixture.

## State and Persistence Behavior

The structures are ABI state exchanged with user space. `struct gup_test` is both input and output; the kernel overwrites timing fields and adjusts `size` to the processed range. The header itself stores no state, but changes to field order, type width, command numbers, or flag values would break compiled selftests and external diagnostic tools.

## Dependencies and Integration Points

The only include is `linux/types.h` for fixed-width kernel ABI types. The header is included by `mm/gup_test.c` and by selftests under `tools/testing/selftests/mm`, including COW and GUP benchmark tests. It also appears in documentation for pin-user-pages testing.

## Risks and Edge Cases

The ABI uses `__u64` for user addresses so 32-bit compatibility depends on `compat_ptr_ioctl` and explicit casting in `gup_test.c`. `which_pages` uses one-based indexing where zero means "do nothing"; tests must not treat entries as zero-based. `gup_flags` passes raw kernel `FOLL_*` values from user test code to the debugfs helper, so test binaries must be built against matching kernel headers.

## Test Signals

The primary signal is that in-tree selftests compile against this header and can drive `/sys/kernel/debug/gup_test`. ABI regressions usually show up as ioctl failures, incorrect timing/size copyback, wrong page dump selection, or long-term fixture commands being rejected unexpectedly.
