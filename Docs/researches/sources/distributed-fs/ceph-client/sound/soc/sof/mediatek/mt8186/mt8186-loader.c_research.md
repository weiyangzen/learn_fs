# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-loader.c

Purpose: Implements MT8186/MT8188 HIFIxDSP boot and shutdown register sequencing.

Important APIs: `mt8186_sof_hifixdsp_boot_sequence()` stalls the core, enables mailbox 0/1 IRQs, writes alternate vector address/select bits, asserts reset, delays, releases reset, and clears RUNSTALL. `mt8186_sof_hifixdsp_shutdown()` stalls the core and asserts reset.

Control flow and integration: `mt8186_run()` in `mt8186.c` calls boot with `SRAM_PHYS_BASE_FROM_DSP_VIEW` after firmware has been loaded to SRAM. Suspend/remove paths call shutdown before SRAM/clock power down.

State and persistence: Hardware reset, RUNSTALL, mailbox IRQ enable, and boot vector registers persist until changed or power-gated.

Risks: Sequencing is timing-sensitive; changing reset polarity or delay can prevent FW_READY. Mailbox IRQ enable is limited to channels 0 and 1. The header deliberately sets both MT8186 and MT8188 ALTVECSEL bits to simplify shared support, which depends on documented ignored bits.

Test signals: Boot-to-FW_READY, shutdown during suspend/remove, mailbox interrupt delivery after boot, and MT8186/MT8188 coverage for alternate vector selection.
