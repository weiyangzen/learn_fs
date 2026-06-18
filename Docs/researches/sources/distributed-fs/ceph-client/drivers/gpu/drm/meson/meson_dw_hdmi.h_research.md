# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.h

Purpose: Defines HDMI TOP block register offsets and interrupt/status bit masks used by the Meson DW-HDMI glue driver.

Important APIs, types, and functions: This header exports no functions or structs. Its public surface is a compact set of `#define`s for `HDMITX_TOP_SW_RESET`, `HDMITX_TOP_CLK_CNTL`, HPD filter and interrupt registers, BIST/shift-pattern controls, TMDS clock pattern registers, revocation memory status, and `HDMITX_TOP_STAT0`. Named interrupt masks include `HDMITX_TOP_INTR_CORE`, `HDMITX_TOP_INTR_HPD_RISE`, `HDMITX_TOP_INTR_HPD_FALL`, and G12A RxSense bits.

Control flow: The header has no execution path. It drives control flow in `meson_dw_hdmi.c` by naming registers touched during initialization, PHY TMDS pattern setup, HPD setup, interrupt clearing/masking, HPD polling, and TOP reset.

State and persistence: Register constants describe persistent HDMI TOP hardware state. `HDMITX_TOP_INTR_STAT_CLR` is write-one-to-clear, while `HDMITX_TOP_INTR_MASKN` is active-high unmask. `HDMITX_TOP_STAT0` reports filtered HPD/RxSense. `HDMITX_TOP_SW_RESET` bit comments document which sub-block resets persist until cleared.

Dependencies and integration points: Requires bit macros from normal Linux kernel headers included by consumers. Used directly by `meson_dw_hdmi.c`; the values are passed through either indirect TOP register access or direct G12A TOP MMIO offseting.

Risks: The header encodes hardware semantics in comments and constants; wrong bit polarity causes hard-to-debug HPD or reset failures. Some fields are G12A-specific while sharing the same register names, so consumers must keep compatible-specific behavior outside the header.

Test signals: HDMI initialization should clear `HDMITX_TOP_SW_RESET`, enable TOP clocks, install HPD filters, and observe HPD changes via `HDMITX_TOP_STAT0`. Interrupt tests should verify rise/fall bits are cleared and unmasked correctly.
