# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-mxs.h

## Purpose
Defines the shared data model and encoding helpers for the MXS pinctrl backend and its SoC-specific frontends. It documents how MXS device-tree mux IDs and packed config values are decoded and supplies the structures consumed by `pinctrl-mxs.c`.

## Important APIs, Types, and Functions
Important macros are register aliases `SET`, `CLR`, `TOG`; `MXS_PINCTRL_PIN()`; `PINID(bank, pin)`; mux decoders `MUXID_TO_PINID()` and `MUXID_TO_MUXSEL()`; pin decoders `PINID_TO_BANK()` and `PINID_TO_PIN()`; config presence bits `PULL_PRESENT`, `VOL_PRESENT`, `MA_PRESENT`; and config extractors `PIN_CONFIG_TO_PULL()`, `PIN_CONFIG_TO_VOL()`, and `PIN_CONFIG_TO_MA()`. Types include `struct mxs_function`, `struct mxs_group`, `struct mxs_regs`, and `struct mxs_pinctrl_soc_data`. The public probe hook is `mxs_pinctrl_probe()`.

## Control Flow
This header has no execution. SoC drivers provide `mxs_pinctrl_soc_data` with pin descriptors and register offsets, then call `mxs_pinctrl_probe()`. The common driver uses the macros to convert DT `fsl,pinmux-ids` into pin numbers and mux selections and to convert compact config words into hardware writes.

## State and Persistence Behavior
The structures describe persistent per-SoC tables and mutable per-group runtime fields. `mxs_group.config` caches the last group configuration; `pins` and `muxsel` arrays are populated during DT parsing. The header’s bitfield definitions are part of the binding contract and must remain stable.

## Dependencies and Integration Points
Includes platform-device and pinctrl descriptor types. It is shared between common MXS code and SoC-specific MXS pinctrl drivers. The bitfield layout integrates directly with device-tree properties and the MXS hardware register layout.

## Risks
Changing bit positions, presence-bit semantics, or bank/pin conversion macros breaks all MXS DT pinmux IDs. `u8 config` and `u8 *muxsel` assume small hardware fields; widening or adding features needs care. `struct mxs_pinctrl_soc_data` is passed by pointer and modified by probe, so callers should not treat all fields as immutable.

## Test Signals
Build coverage of MXS SoC drivers, DT pinmux IDs decoding to expected bank/pin/mux values, config presence bits applying only requested fields, and pinctrl debug output showing cached config are the main signals.
