# sources/distributed-fs/ceph-client/drivers/soc/sophgo/sg2044-topsys.c

## Purpose

`sg2044-topsys.c` is an MFD parent for the Sophgo SG2044 TOP system controller. Its role is to instantiate the PLL clock child device.

## Important APIs, Types, and Functions

`sg2044_topsys_subdev[]` contains one MFD cell named `"sg2044-pll"`. `sg2044_topsys_probe()` calls `devm_mfd_add_devices()` with that cell. The OF match table binds `"sophgo,sg2044-top-syscon"`. `sg2044_topsys_driver` is registered with `module_platform_driver()`.

## Control Flow

On matching platform probe, the driver registers the child PLL platform device with no extra resources. Cleanup is device-managed.

## State and Persistence Behavior

The file has no mutable driver-private state and no persistence. Child state is owned by the PLL driver.

## Dependencies and Integration Points

It depends on the platform bus, OF matching, and MFD core. It integrates SG2044 top system-controller DT nodes with the clock/PLL implementation through the `"sg2044-pll"` child name.

## Risks and Edge Cases

The child receives no explicit MMIO resource here, so it must obtain registers from the parent device, syscon/regmap, or another binding mechanism. Probe has no validation beyond MFD registration. Any future children need careful resource partitioning.

## Test Signals

Boot with an SG2044 top-syscon DT node and verify `sg2044-pll` child creation and PLL driver probe. Test module unload/reload and missing child driver behavior.
