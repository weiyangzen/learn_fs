# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_pm.h

## Purpose

`cc_pm.h` declares the ccree runtime PM interface and provides no-op fallbacks when `CONFIG_PM` is disabled. It lets request submission code use a uniform API independent of kernel PM configuration.

## Important APIs, Types, And Functions

The header defines `CC_SUSPEND_TIMEOUT`, declares `extern const struct dev_pm_ops ccree_pm`, `cc_pm_get()`, and `cc_pm_put_suspend()` under `CONFIG_PM`, and provides inline stubs that return success/do nothing otherwise.

## Control Flow

There is no runtime control flow except the compile-time branch. With PM enabled, callers enter `cc_pm.c`. Without PM, request submission proceeds without runtime PM references.

## State And Persistence Behavior

The header owns no state. Its stubs imply the hardware remains available by other means when runtime PM support is absent.

## Dependencies And Integration Points

It includes `cc_driver.h` and is consumed by `cc_request_mgr.c` and the platform driver PM registration path. The PM ops are attached to the device driver outside this header.

## Risks And Edge Cases

The no-op fallback means PM-only bugs may be hidden on kernels built without `CONFIG_PM`. Callers must pair `cc_pm_get()` and `cc_pm_put_suspend()` even though that balance is compile-time invisible when PM is disabled.

## Test Signals

Build both with and without `CONFIG_PM`. With PM enabled, runtime suspend/resume crypto stress should pass. Without PM, request manager code should compile and run with the inline stubs.
