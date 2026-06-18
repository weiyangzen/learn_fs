# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.h

Purpose: Declares the shared formatter driver contract for AXG TDM formatter blocks.

Important APIs and types: `struct axg_tdm_formatter_hw` carries hardware quirks such as skew offset. `struct axg_tdm_formatter_ops` lets a concrete formatter provide stream lookup, enable, disable, and prepare callbacks. `struct axg_tdm_formatter_driver` bundles component driver, regmap config, ops, and quirks for OF match data. Public prototypes expose channel-mask programming, DAPM event handling, and platform probe.

Control flow: No executable logic. Concrete formatter modules pass a `axg_tdm_formatter_driver` as match data to the common probe and use `axg_tdm_formatter_event()` in DAPM widgets.

State and persistence: Declares configuration structures that persist as static match data and drive runtime formatter state in `axg-tdm-formatter.c`.

Dependencies and integration points: Includes `axg-tdm.h` for stream/interface definitions and is included by TDM formatter implementations such as TDMIN/TDMOUT.

Risks: The ops contract assumes `get_stream()` can resolve a live `axg_tdm_stream` from DAPM graph topology. Incorrect quirks or regmap configs can break all formatter lifecycle code.

Test signals: Build/link coverage of formatter modules, OF match data validation, DAPM event invocation, and block-specific prepare callbacks receiving expected stream parameters.
