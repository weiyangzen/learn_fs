# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.c

Purpose: implements the Freescale MXS SAIF CPU DAI driver, including SAIF master/slave clocking, MCLK export, DAI format setup, DMA-triggered playback/capture, IRQ error accounting, and PCM registration.

Important APIs/types/functions: global `mxs_saif[2]` indexes the two SAIF instances. Exported helpers `mxs_saif_get_mclk` and `mxs_saif_put_mclk` allow codecs/machine drivers to use SAIF MCLK. DAI ops include `mxs_saif_set_dai_sysclk`, `mxs_saif_set_dai_fmt`, `mxs_saif_startup`, `mxs_saif_hw_params`, `mxs_saif_prepare`, and `mxs_saif_trigger`.

Control flow: probe resolves the SAIF alias ID, optional `fsl,saif-master` phandle, clock, MMIO, IRQ, and registers the DAI plus DMAEngine PCM. Startup clears reset/clock-gate and prepares the clock. `hw_params` programs master clock rate, word length, 48xfs mode, and TX/RX direction. Trigger enables master and possibly local clocks, starts RUN, primes or drains `SAIF_DATA`, and tracks running state; stop waits one sample period before disabling.

State and persistence: `struct mxs_saif` tracks clock, base, id/master id, current rate, MCLK use, ongoing flag, underrun/overrun counters, and running/stopped state. Hardware control/status registers hold format and run state.

Dependencies and integration: depends on DT aliases, optional master phandle, common clock framework, raw MMIO set/clear registers, IRQ handling, `mxs-pcm`, and ASoC DAI registration. SAIF0 can register an exported `mxs_saif_mclk` clock provider.

Risks: global two-entry state assumes only two SAIFs and correct probe ordering for master references. Clock-rate changes are rejected while the master is ongoing; simultaneous streams must share rate. Raw MMIO and busy polling make ordering important. Error counters are debug-only and do not stop streams.

Test signals: probe of both SAIF instances with correct aliases, MCLK get/put from SGTL5000 path, I2S and left-justified playback/capture, shared-rate enforcement, IRQ handling for FIFO underflow/overflow, and suspend/resume clock balance.
