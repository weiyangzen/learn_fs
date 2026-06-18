# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Makefile

Purpose: Lists ath6kl object composition for the core module and SDIO/USB transport modules.

Important build targets: `obj-$(CONFIG_ATH6KL) += ath6kl_core.o` builds the core from debug, HIF, HTC mailbox/pipe, BMI, cfg80211, init, main, txrx, WMI, core, and recovery objects. `ath6kl_core-$(CONFIG_NL80211_TESTMODE) += testmode.o` and `ath6kl_core-$(CONFIG_ATH6KL_TRACING) += trace.o` add optional objects. `obj-$(CONFIG_ATH6KL_SDIO) += ath6kl_sdio.o` builds `sdio.o`; `obj-$(CONFIG_ATH6KL_USB) += ath6kl_usb.o` builds `usb.o`. `CFLAGS_trace.o := -I$(src)` supports trace header discovery.

Control flow: Kernel kbuild expands objects according to Kconfig selections and links per-module object lists. Transport modules depend on the core module APIs but are built separately.

State and persistence: No runtime state. It defines build-time module composition and object ordering.

Dependencies and integration points: Integrates with Kbuild, Kconfig symbols, trace generation, nl80211 testmode, SDIO/USB transport implementations, and the shared ath6kl core exported symbols.

Risks: Omitting an object breaks link-time symbol resolution; changing optional object gates can accidentally expose testmode/tracing code in production builds. Trace include flags must stay aligned with `trace.h` include path assumptions.

Test signals: Build every Kconfig combination, verify module symbol linkage between core and transports, ensure testmode and trace objects appear only under their configs, and run modpost without unresolved exports.
