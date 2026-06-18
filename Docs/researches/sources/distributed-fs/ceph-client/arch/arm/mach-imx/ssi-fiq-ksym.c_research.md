# sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq-ksym.c

Purpose: Exports assembly SSI FIQ handler symbols for modular i.MX ASoC SSI support.

Important APIs/types/functions: Exports `imx_ssi_fiq_tx_buffer`, `imx_ssi_fiq_rx_buffer`, `imx_ssi_fiq_start`, `imx_ssi_fiq_end`, and `imx_ssi_fiq_base`.

Control flow: No runtime control flow beyond module symbol export table generation.

State and persistence: No owned state; the exported symbols refer to variables/labels in `ssi-fiq.S` patched or copied by SSI audio code.

Dependencies and integration points: Depends on `linux/platform_data/asoc-imx-ssi.h`, module symbol infrastructure, and the assembly FIQ handler.

Risks: The exported data symbols expose writable handler configuration ABI. Mismatches with the assembly labels or module users break FIQ audio transfer.

Test signals: Build modular SSI audio and confirm symbols resolve with `CONFIG_FIQ`/ASoC SSI configurations.
