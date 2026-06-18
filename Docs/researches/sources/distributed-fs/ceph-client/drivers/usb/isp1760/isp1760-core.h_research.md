# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.h

## Purpose
`isp1760-core.h` declares the common ISP1760 device container, board/chip flags, public registration API, pullup API, and small regmap helper wrappers used by both HCD and UDC code.

## Important APIs, Types, And Functions
`struct isp1760_device` owns `dev`, `devflags`, optional `rst_gpio`, embedded `struct isp1760_hcd`, and embedded `struct isp1760_udc`. Flags describe bus width, peripheral enablement, analog overcurrent, DACK/DREQ polarity, chip variant, interrupt polarity/triggering, and 8-bit mode. Public functions are `isp1760_register()`, `isp1760_unregister()`, and `isp1760_set_pullup()`. Inline helpers wrap `regmap_field_read/write`, set/clear full fields, and raw `regmap_read/write`.

## Control Flow
The header has no standalone runtime flow. Its helpers are called throughout core, HCD, and UDC paths to abstract field operations. The device flags are produced by bus glue and consumed by core initialization.

## State And Persistence
The state shape declared here persists for the lifetime of the bound device. It embeds both role states regardless of whether both roles are active; disabled role functions become stubs through their own headers.

## Dependencies And Integration Points
The header depends on Linux ioport and regmap plus the local HCD and UDC headers. It is the shared contract between bus glue, common core, host controller, and gadget controller.

## Risks
`isp1760_field_read()` and register helpers ignore regmap return values, so bus faults are not propagated. `isp1760_field_set()` writes `0xFFFFFFFF`, relying on regmap-field masking to constrain writes. Adding flags requires updates in platform/PCI parsing, core setup, and documentation/bindings.

## Test Signals
Compile coverage catches enum/type mismatches. Runtime signals come from probe and role operation across all chip variants, especially field writes for bus width, interrupts, pullup, and reset. Fault-injection of regmap operations would expose the current lack of error propagation.
