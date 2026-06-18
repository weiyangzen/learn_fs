<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv18xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv18xx.h

## Purpose

`pinctrl-cv18xx.h` defines the shared Sophgo CV18xx-family pinmux packing macros used by CV1800B, CV1812H, SG2000, and SG2002 package pin headers.

## Important APIs, Types, and Functions

The key constants are `PIN_MUX_INVALD` with value `0xff`, `PINMUX2(pin, mux, mux2)`, and `PINMUX(pin, mux)`. `PINMUX2()` packs a 16-bit pin ID, an 8-bit primary mux in bits 16-23, and an 8-bit secondary mux in bits 24-31. `PINMUX()` sets the secondary mux byte to `PIN_MUX_INVALD`.

## Control Flow

There is no runtime control flow. Device-tree preprocessing expands these macros into a single 32-bit integer cell. The Sophgo pinctrl driver later unpacks the pin, primary mux, and optional secondary mux fields.

## State and Persistence Behavior

The header is stateless. The packed values persist only as device-tree cells. Runtime state is the hardware mux configuration applied by the pinctrl driver.

## Dependencies and Integration Points

The file is standalone and is included by SoC/package-specific Sophgo pin headers. It must agree with the binding schema and the driver's bit-field decoder. The misspelled exported name `PIN_MUX_INVALD` is part of the binding ABI and should not be silently renamed without compatibility handling.

## Risks and Edge Cases

Arguments are masked, so oversized pin or mux values are truncated rather than rejected by the macro. That can hide DTS mistakes until runtime. The invalid secondary mux sentinel is `0xff`; if hardware ever has a valid secondary mux value of 255, the encoding cannot distinguish it. Consumers must treat the misspelled macro as intentional ABI.

## Test Signals

Static tests should evaluate representative `PINMUX()` and `PINMUX2()` values and verify driver unpacking. DTS compilation should cover each package header using these macros, and `dtbs_check` should catch invalid property shapes even though value-range mistakes may require driver-side validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv18xx.h -->
