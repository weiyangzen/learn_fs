<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/omap.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/omap.h

## Purpose

`omap.h` defines common OMAP pinctrl binding constants and address helper macros. It gives DTS files symbolic mux modes, active/off-state pin configuration bits, SoC-specific padconf offset helpers, and a few common UART RX pad offsets.

## Important APIs, Types, and Functions

The API surface includes `MUX_MODE0` through `MUX_MODE7`, active bit flags such as `PULL_ENA`, `PULL_UP`, `ALTELECTRICALSEL`, and `INPUT_EN`, and off-mode/wakeup flags such as `OFF_EN`, `OFFOUT_EN`, `OFFOUT_VAL`, `OFF_PULL_EN`, `OFF_PULL_UP`, `WAKEUP_EN`, and `WAKEUP_EVENT`. Convenience composites include `PIN_OUTPUT`, `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`, `PIN_INPUT_PULLUP`, `PIN_INPUT_PULLDOWN`, and `PIN_OFF_*`.

Address helpers include `OMAP_IOPAD_OFFSET(pa, offset)`, SoC wrappers such as `OMAP2420_CORE_IOPAD`, `OMAP3_CORE1_IOPAD`, `OMAP3_WKUP_IOPAD`, `DM814X_IOPAD`, `AM33XX_IOPAD`, and `AM33XX_PADCONF`, plus `OMAP_PADCONF_OFFSET()`, `OMAP4_IOPAD()`, and `OMAP5_IOPAD()`. `OMAP3_UART*_RX` and `OMAP4_UART*_RX` define commonly used pad offsets.

## Control Flow

No runtime control flow is present. The unusual helper form intentionally expands to multiple device-tree cells, for example an offset expression followed by one or more value cells. DTS compilation resolves the arithmetic before the OMAP pinctrl driver receives the cells.

## State and Persistence Behavior

State exists only in compiled DTS pinctrl states and in hardware padconf registers after the kernel applies them. Off-mode bits influence low-power behavior, but this header does not itself store or restore state.

## Dependencies and Integration Points

The file is standalone. It integrates with OMAP, AM33xx, DM814x/DM816x, OMAP4, and OMAP5 pinctrl bindings whose `pinctrl-single,pins` or related properties accept offset/config pairs. Board DTS files rely on the helper base offsets matching each SoC's padconf register layout.

## Risks and Edge Cases

The address helpers mask physical addresses with `0xffff` and subtract SoC-specific base offsets; using the wrong helper can produce a plausible but incorrect offset. `AM33XX_IOPAD()` expands an extra `(0)` cell while `AM33XX_PADCONF()` expands separate config and mux cells, so property formats must match the binding. Wakeup and off-mode bits can change suspend behavior; wrong use can cause excessive power draw, broken wake sources, or pins driving against external circuitry.

## Test Signals

Validation should include DTS compilation across representative OMAP generations, `dtbs_check` for cell counts, boot-time pinctrl debugfs state, padconf register inspection when available, UART RX smoke tests for the common offsets, and suspend/resume tests for off-mode and wakeup definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/omap.h -->
