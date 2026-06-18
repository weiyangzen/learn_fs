# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_i2c.h

## Purpose
`xe_i2c.h` defines the Xe I2C endpoint data, runtime state, capability bits, public I2C lifecycle APIs, and no-op stubs when `CONFIG_I2C` is disabled.

## Important APIs, Types, And Functions
- `XE_I2C_MAX_CLIENTS` is 3, matching the endpoint address array.
- `XE_I2C_EP_COOKIE_DEVICE` validates firmware-provided endpoint data.
- `XE_I2C_EP_CAP_IRQ` indicates adapter IRQ support.
- `struct xe_i2c_endpoint` stores cookie, capabilities, and client addresses.
- `struct xe_i2c` stores platform/fwnode, adapter/client objects, notifier/work, IRQ domain, endpoint, parent device, and MMIO pointer.
- Public functions cover probe, presence checks, IRQ handling/reset/postinstall, and PM suspend/resume.

## Control Flow
Callers include this header to interact with optional I2C support. When I2C is disabled, every exported operation compiles to a no-op or `false`/0 result, allowing the main driver and IRQ paths to remain unconditional.

## State And Persistence
The header defines, but does not allocate, `struct xe_i2c` state. The implementation stores the state in `xe->i2c` after endpoint validation.

## Dependencies And Integration Points
The header depends on Linux notifier, workqueue, bits, and type definitions. It bridges Xe device code, IRQ code, PM code, and the I2C implementation.

## Risks
Because the stubs silently succeed, callers must use `xe_i2c_present()` rather than assuming `xe_i2c_probe()` created hardware state. The endpoint layout is ABI-like with firmware/MMIO producer expectations, so packing or field changes would be high risk.

## Test Signals
Build with and without `CONFIG_I2C`; check that global IRQ and PM paths still compile and that runtime behavior cleanly skips I2C when `xe->i2c` is unset.
