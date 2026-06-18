# sources/distributed-fs/ceph-client/drivers/usb/storage/debug.h

## Purpose

`debug.h` declares and gates USB Mass Storage debug helpers so call sites compile both with and without verbose debugging enabled.

## Important APIs, Types, and Functions

When `CONFIG_USB_STORAGE_DEBUG` is set, the header declares `usb_stor_show_command()`, `usb_stor_show_sense()`, and `usb_stor_dbg()`, and expands `US_DEBUG(x)` to execute `x`. Otherwise it provides a typed no-op `_usb_stor_dbg()` and defines `usb_stor_dbg()` and `US_DEBUG(x)` so debug call sites compile away while preserving format checking.

## Control Flow

There is no runtime flow in the debug-enabled case beyond function declarations. In the disabled case, debug calls are wrapped in `do { if (0) ... } while (0)`, keeping expressions unreachable and optimized out.

## State and Persistence Behavior

The header has no state or persistence. It only controls conditional compilation and logging call visibility.

## Dependencies and Integration Points

It depends on kernel printf annotations and forward visibility of `struct us_data` from including translation units. It is included by usb-storage core and vendor transports to share a consistent debug interface.

## Risks and Test Signals

Risks include format-signature drift between declaration and implementation, debug-only expressions hiding side effects when disabled, and missing declarations for modules that call exported debug helpers. Test signals include builds with debug on/off, compiler format warnings on bad debug calls, and no generated code for disabled debug paths.
