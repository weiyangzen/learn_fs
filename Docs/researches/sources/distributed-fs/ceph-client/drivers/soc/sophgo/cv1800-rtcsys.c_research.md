# sources/distributed-fs/ceph-client/drivers/soc/sophgo/cv1800-rtcsys.c

## Purpose

`cv1800-rtcsys.c` is an MFD parent for the Sophgo CV1800 RTC subsystem. It creates a child RTC device and forwards the named alarm interrupt resource.

## Important APIs, Types, and Functions

`cv1800_rtcsys_irq_resources[]` contains one named IRQ resource, `"alarm"`. `cv1800_rtcsys_subdev[]` defines one child cell named `"cv1800b-rtc"`. `cv1800_rtcsys_probe()` resolves the platform IRQ by name and calls `devm_mfd_add_devices()`. The OF match table binds `"sophgo,cv1800b-rtc"`. Module metadata names the driver and license.

## Control Flow

When a matching platform device probes, the driver obtains the `"alarm"` IRQ, writes the resolved IRQ number into the static resource, and registers the RTC child with `PLATFORM_DEVID_AUTO`. Device-managed MFD registration handles cleanup on detach.

## State and Persistence Behavior

The only mutable state is the static IRQ resource start/end values. There is no persistent storage. Runtime child-device state is owned by the child RTC driver.

## Dependencies and Integration Points

It depends on platform-device probing, OF matching, the MFD core, and a child driver matching `"cv1800b-rtc"`. It assumes the DT node provides an interrupt named `"alarm"`.

## Risks and Edge Cases

Because the resource array is static, multiple instances would share and overwrite the same resource values; this is probably acceptable only if the hardware is singleton. Probe fails hard if the named IRQ is absent. The parent compatible is the same string as the child name, so binding documentation must make the parent/child relationship clear.

## Test Signals

Probe with valid DT and confirm a child `cv1800b-rtc` platform device appears with the correct alarm IRQ. Test missing IRQ name, module unload/reload, and deferred child driver probing.
