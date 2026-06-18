# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debug.h

## Purpose

`i40e_debug.h` defines debug mask bits and lightweight logging macros for i40e hardware-level diagnostics. It centralizes category bits used by `hw->debug_mask` and maps hardware debug output to Linux device logging.

## Important APIs, Types, And Functions

- `enum i40e_debug_mask` defines categories such as init, release, link, PHY, HMC, NVM, LAN, flow, DCB, diagnostics, Flow Director, package, iWARP, AdminQ message/descriptor/buffer/command, user bits, and all bits.
- `i40e_hw_to_dev()` is declared as the bridge from `struct i40e_hw` to `struct device`.
- `hw_dbg()` and `hw_warn()` wrap `dev_dbg()` and `dev_warn()`.
- `i40e_debug()` conditionally emits `dev_info()` when the requested mask intersects `h->debug_mask`.

## Control Flow

There is no standalone control flow. Runtime gating occurs in the `i40e_debug()` macro: it tests the mask against a hardware structure’s `debug_mask` and emits only when enabled.

## State And Persistence

Debug state is the `debug_mask` field in `struct i40e_hw`; this header does not persist it. Messages are emitted to the kernel logging infrastructure.

## Dependencies And Integration Points

The header depends on `<linux/dev_printk.h>` and a driver-provided `i40e_hw_to_dev()`. It is used by diagnostics and DCB code for category-specific logging.

## Risks

- The `i40e_debug()` macro references `hw` inside `i40e_hw_to_dev(hw)` while its formal hardware argument is named `h`; this relies on call-site scope containing a `hw` variable and is fragile.
- Debug masks are broad bitfields, so accidental use of overlapping values would alter logging categories.
- `dev_info()` can be noisy for high-frequency paths if masks are enabled.

## Test Signals

Build coverage should catch macro call sites lacking a `hw` variable. Runtime smoke tests can toggle `debug_mask` and confirm category-gated output for DCB and diagnostic failures.
