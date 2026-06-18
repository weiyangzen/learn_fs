# subset-b-006432

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l35.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l35.c

Purpose: implements the Linux ASoC component/platform driver for the Cirrus Logic CS47L35 Madera-family codec. It exposes mixer controls, DAPM widgets/routes, DAIs, FLL programming, ADSP compressed streams, IRQ handling, and probe/remove lifecycle glue for the codec child of the Madera MFD.

Important APIs, types, and data:
- `struct cs47l35` owns the shared `struct madera_priv core` plus one `struct madera_fll`.
- `CS47L35_NUM_ADSP` is 3 and `CS47L35_MONO_OUTPUTS` is 1. DSP memory maps are declared as three `cs_dsp_region` arrays, each with PM/ZM/XM/YM windows, and indexed through `cs47l35_dsp_regions`.
- `wm_adsp2_control_bases` maps DSP1-DSP3 to `MADERA_DSP*_CONFIG_1`.
- `cs47l35_snd_controls` publishes ALSA controls for two input pairs, EQ/DRC/LHPF/ISRC blocks, three DSP preload/FW controls, output mixers, noise generator/gate controls, AIF/Slimbus/SPDIF TX mixers, digital mute/volume controls, short-circuit protection, and SPKDAT high-performance mode.
- `cs47l35_dapm_widgets` and `cs47l35_dapm_routes` define the power graph: supplies/regulators, MICBIAS, input muxes, generators, AEC loopback muxes, AIF/Slimbus endpoints, DSP widgets, EQ/DRC/LHPF/ISRC paths, headphone/speaker/SPKDAT/SPDIF outputs, and DRC activity outputs.
- `cs47l35_dai` registers AIF1-3, Slimbus1-2, CPU/DSP voice-control capture, and CPU/DSP trace capture DAIs. Normal AIFs use `madera_dai_ops`; Slimbus DAIs use `madera_simple_dai_ops`; compressed CPU endpoints use `snd_soc_new_compress`.

Control flow:
- Platform probe defers until `madera->irq_dev` exists, allocates `struct cs47l35`, initializes `madera_priv`, overheat handling, DSP compressed IRQ wake, all three ADSP2 cores, the single FLL, all DAI instances, and digital volume update latch bits before registering the ASoC component.
- Component probe binds the component regmap, publishes the DAPM pointer under `dapm_ptr_lock`, calls `madera_init_inputs()`, calls `madera_init_outputs()` with the one mono route for `HPOUT1 Mono Mux`, disables `HAPTICS`, adds per-DSP rate controls, and runs `wm_adsp2_component_probe()` for each DSP.
- DAPM events drive clock and output sequencing. `cs47l35_adsp_power_ev()` reads `MADERA_DSP_CLOCK_1`, extracts the legacy DSP frequency field, sets the selected ADSP clock on `SND_SOC_DAPM_PRE_PMU`, then delegates to `wm_adsp_early_event()`. `cs47l35_hp_ev()` wraps `madera_hp_ev()` and additionally enables EDRE stereo control only after both HPOUT1 channels are on; on power-down it resets DCS controls and clears the EDRE bit.
- `cs47l35_set_fll()` dispatches `MADERA_FLL1_REFCLK` and `MADERA_FLL1_SYNCCLK` to the one local FLL, returning `-EINVAL` for unsupported IDs.
- `cs47l35_open()` maps compressed streams by codec DAI name: `cs47l35-dsp-voicectrl` uses ADSP index 2 (DSP3) and `cs47l35-dsp-trace` uses ADSP index 0 (DSP1). Other DAI names fail with `-EINVAL`.
- `cs47l35_adsp2_irq()` iterates all DSPs, gives each `wm_adsp_compr_handle_irq()`, counts any non-`-ENODEV` service, and sends `MADERA_NOTIFY_VOICE_TRIGGER` through the Madera blocking notifier when firmware reports `WM_ADSP_COMPR_VOICE_TRIGGER`.

State and persistence: persistent driver state is device-managed allocation plus Madera-owned register state. ALSA controls write codec registers through regmap/component helpers. DAPM keeps power-routing state and stores `madera->dapm` while the component is bound. DSP firmware/control state is held in `core.adsp[]` and initialized/removed by WM_ADSP helpers. Runtime PM is enabled after hardware setup and disabled during remove/error unwind. No file-backed persistence is used.

Dependencies and integration points: depends on the Madera MFD core, Madera IRQ chip, Madera register definitions, shared Madera codec helpers in `madera.h`, WM_ADSP/CS DSP support, Linux regmap, runtime PM, and ASoC component/DAI/DAPM/compress APIs. It integrates with machine drivers through named DAIs, with firmware through WM_ADSP controls and compressed streams, with system wake through `MADERA_IRQ_DSP_IRQ1`, and with external listeners through the Madera notifier chain for voice triggers.

Risks:
- DSP clock setup relies on the legacy field in `MADERA_DSP_CLOCK_1`; mismatched register programming can prevent DSP boot or produce invalid audio rates.
- Compressed stream routing depends on exact DAI names. Renaming DAIs without updating `cs47l35_open()` breaks voice-control or trace capture.
- The headphone event wrapper performs variant-specific EDRE/DCS writes after common Madera sequencing; ordering changes could affect pop suppression or output calibration.
- DAPM route/control names are ABI-like for userspace mixer state and machine-driver routing. Renames or missing routes can silently strand paths.
- Error unwind must stay paired for DSP init, IRQ wake, overheat, and core setup to avoid stale IRQ handlers or leaked DSP instances.

Test signals:
- Build coverage should compile this file with the Madera/WM_ADSP headers and catch array/register symbol mismatches.
- Probe smoke tests on CS47L35 hardware or emulation should verify `cs47l35-codec` registration, all expected DAIs, runtime PM enablement, and no deferred-probe loop once the IRQ chip is ready.
- ALSA route tests should exercise AIF/Slimbus playback/capture, HPOUT/EPOUT demux, SPKOUT, SPKDAT1, SPDIF1, AEC loopback, and DRC activity paths.
- DSP tests should load firmware on all three DSPs, open voice-control and trace compressed streams, trigger the ADSP IRQ, and observe notifier delivery for voice trigger events.
- Power tests should watch DAPM transitions for SYSCLK/DSPCLK/domain clocks, regulator supplies, HPOUT EDRE toggling, and clean remove/error-unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l85.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l85.c

Purpose: implements the ASoC codec driver for the CS47L85 Madera-family codec. It is the high-I/O variant in this group, exposing six input pairs, seven ADSP2 cores, four AIFs, three Slimbus DAIs, three headphone outputs, stereo analog speakers, two SPKDAT ports, RXANC, ASRC/ISRC processing, and compressed DSP voice/trace capture.

Important APIs, types, and data:
- `struct cs47l85` embeds `struct madera_priv core` and three `struct madera_fll` instances.
- `CS47L85_NUM_ADSP` is 7 and `CS47L85_MONO_OUTPUTS` is 4. Seven DSP memory-region arrays map PM/ZM/XM/YM spaces at increasing base addresses, and `wm_adsp2_control_bases` maps the seven DSPs to their config registers.
- `cs47l85_snd_controls` defines a large ALSA control surface: IN1-IN6 OSR/HPF/digital-volume controls, analog PGA volumes for IN1-IN3, RXANC coefficient/config byte controls, EQ/DRC/LHPF coefficients, ISRC and ASRC rate controls, seven DSP preload/FW controls, output mixer/mute/volume controls for HPOUT1-3, stereo speaker, SPKDAT1-2, noise gate source controls, and AIF/Slimbus/SPDIF TX mixers.
- RXANC support is built from `CS47L85_RXANC_INPUT_ROUTES`, `CS47L85_RXANC_OUTPUT_ROUTES`, ANC input muxes, an ANC noise-generator mux, and per-output ANC source muxes.
- `cs47l85_dapm_widgets` and `cs47l85_dapm_routes` describe clock domains, regulators, MICBIAS1-4, analog/digital input muxes, DMIC inputs 4-6, RXANC graph, all AIF/Slimbus endpoints, output PGAs, ASRC/ISRC blocks, seven DSPs, AEC loopbacks, SPDIF, and output pins.
- `cs47l85_dai` registers AIF1/AIF2 as 8-channel DAIs, AIF3/AIF4 as 2-channel DAIs, Slimbus1-3, and compressed CPU/DSP voice-control and trace endpoints.

Control flow:
- Platform probe defers until the Madera IRQ chip is ready, allocates the codec state, sets `core.num_inputs = 12`, initializes the Madera codec core and overheat support, requests/wakes `MADERA_IRQ_DSP_IRQ1`, initializes all seven ADSP2 cores, initializes FLL1-FLL3, initializes all DAIs, latches all output digital-volume update bits, enables runtime PM, and registers the component.
- Component probe initializes the component regmap and shared DAPM pointer, calls Madera input/output initialization with four mono-capable outputs, disables `HAPTICS`, adds seven ADSP rate controls, and binds all seven DSPs to the component.
- `cs47l85_adsp_power_ev()` reads `MADERA_DSP_CLOCK_1`, extracts the legacy DSP clock frequency field, programs the per-DSP ADSP clock before power-up, and then runs the WM_ADSP early event handler.
- `cs47l85_hp_ev()` applies common headphone event sequencing and adds the same HPOUT1 EDRE/DCS handling used by the smaller variant. Other outputs use common `madera_out_ev` or `madera_spk_ev`.
- `cs47l85_set_fll()` dispatches REFCLK and SYNCCLK programming for FLL1, FLL2, and FLL3; unknown IDs return `-EINVAL`.
- `cs47l85_open()` maps compressed DAI names to firmware cores: DSP voice control opens ADSP index 5 (DSP6), trace opens ADSP index 0 (DSP1), and unsupported compressed DAIs are rejected.
- The ADSP IRQ handler loops over all seven DSPs, delegates compressed IRQ work to WM_ADSP, reports spurious interrupts when no DSP handles the IRQ, and sends `MADERA_NOTIFY_VOICE_TRIGGER` with the 1-based core number on voice trigger events.

State and persistence: state is held in the platform driver's `struct cs47l85`, the shared `madera_priv`, register-map values, DAPM graph state, and WM_ADSP firmware/control state. Mixer byte controls persist only as hardware register contents and normal ALSA control state while the device is active. `madera->dapm` is set only while the component is present. Runtime PM state is process/kernel state, not file-backed persistence.

Dependencies and integration points: integrates with the Madera MFD/regmap/IRQ core, the shared Madera ASoC helper layer, WM_ADSP/CS DSP firmware loading and compressed capture, ASoC component/DAI/DAPM/compress infrastructure, regulator-backed DAPM supplies, runtime PM, and the Madera notifier chain. Machine drivers consume the named DAIs and DAPM pins/routes; user space consumes the named ALSA controls and compressed capture endpoints.

Risks:
- The route table is very large and variant-specific; omissions in clock-domain, supply, RXANC, ASRC/ISRC, or output routes can leave paths unpowered even when controls appear valid.
- `cs47l85_open()` relies on string comparison against codec DAI names and hard-coded DSP indices; DAI renames or firmware placement changes can break compressed capture.
- L85 has three FLLs and many clock domains. Incorrect FLL ID dispatch or clock-source programming can affect all DAIs and asynchronous sample-rate conversion.
- RXANC coefficient byte controls expose register ranges directly; size or address mistakes would corrupt filter state or adjacent registers.
- The ADSP init unwind path must remove only initialized DSPs and release IRQ wake/overheat/core resources in order.
- Control names and DAPM widget names are part of the userspace/machine-driver contract; changing them can regress saved mixer profiles and board routing.

Test signals:
- Compile tests should catch Madera register/control macro mismatches and `MADERA_MAX_DAI` overflow via `BUILD_BUG_ON`.
- Probe tests should verify `cs47l85-codec` registers with all eleven DAIs, seven DSP controls, and expected input/output counts.
- Audio path tests should cover AIF1/AIF2 8-channel operation, AIF3/AIF4, Slimbus1-3, HPOUT1-3, speaker L/R, SPKDAT1-2, SPDIF1, PWM, EQ/DRC/LHPF/ISRC/ASRC, and AEC loopback.
- RXANC tests should program coefficients/config, switch internal/external noise-generator paths, select left/right/combine channels, and route ANC output to each supported analog/digital output.
- Firmware tests should initialize all seven DSPs, open DSP6 voice-control and DSP1 trace streams, exercise compressed IRQ handling, and confirm voice-trigger notifier events.
- Power-management tests should confirm runtime PM enable/idle, DAPM regulator and clock sequencing, HPOUT1 EDRE behavior, and clean remove/error unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l85.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l90.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l90.c

Purpose: implements the ASoC codec driver for the CS47L90 Madera-family codec. It resembles CS47L85 in DSP and digital-interface scale but has a different analog I/O mix: five input pairs, no analog speaker outputs, one SPKDAT port, DFC processing blocks, ADSP2 revision 2 setup with locked regions, bus-error IRQ integration, and an always-on FLL path.

Important APIs, types, and data:
- `struct cs47l90` contains `struct madera_priv core` and three FLL slots used for FLL1, FLL2, and FLLAO.
- `CS47L90_NUM_ADSP` is 7 and `CS47L90_MONO_OUTPUTS` is 3. Seven DSP memory-region arrays map PM/ZM/XM/YM windows; `cs47l90_dsp_control_bases` maps DSP control bases.
- `cs47l90_snd_controls` exposes IN1-IN5 controls, low-power mode switches for IN1/IN2, RXANC byte controls, EQ/DRC/LHPF, ISRC/ASRC rates, seven DSP preload/FW controls, HPOUT1-3 and SPKDAT1 controls, noise gate controls, DFC width/type controls for RX/TX of DFC1-DFC8, AIF/Slimbus/SPDIF TX mixers, and processing block controls.
- RXANC graph support mirrors L85 but only routes outputs to HPOUT1-3 and SPKDAT1. `CS47L90_RXANC_INPUT_ROUTES` covers IN1-IN5 rather than IN1-IN6.
- `cs47l90_dapm_widgets` includes SYSCLK/ASYNCCLK/DSPCLK, many domain clocks including `DFCCLK`, regulators, MICBIAS split supplies, analog/DMIC input widgets, RXANC widgets, AIF/Slimbus endpoints, HPOUT/SPKDAT outputs, ASRC/ISRC, DFC1-DFC8 PGAs and mux widgets, seven DSP widgets, and SPDIF.
- `cs47l90_dai` registers the same broad DAI shape as L85: AIF1/AIF2 8-channel, AIF3/AIF4 2-channel, Slimbus1-3, CPU/DSP voice-control, and CPU/DSP trace.

Control flow:
- Platform probe defers until `madera->irq_dev` is present, allocates state, sets `core.num_inputs = 10`, initializes the Madera core, requests/wakes `MADERA_IRQ_DSP_IRQ1`, initializes all seven ADSP2 cores as revision 2, enables `CS_ADSP2_REGION_1_9` locking, registers a per-DSP bus-error IRQ after each successful DSP init, initializes FLL1, FLL2, and FLLAO, initializes DAIs, latches output digital-volume update bits, enables runtime PM, and registers the component.
- Component probe binds the regmap/DAPM pointer, initializes inputs/outputs with three mono-capable outputs, disables `HAPTICS`, adds seven DSP rate controls, and runs WM_ADSP component probe for each DSP.
- `cs47l90_adsp_power_ev()` reads `MADERA_DSP_CLOCK_2` and passes its value directly to `madera_set_adsp_clk()` during DSP pre-power-up, then calls `wm_adsp_early_event()`. Unlike L35/L85, it does not mask/shift the legacy field from `MADERA_DSP_CLOCK_1`.
- `cs47l90_set_fll()` dispatches FLL1/FLL2 REFCLK and SYNCCLK plus FLLAO REFCLK. There is no FLLAO SYNCCLK case.
- `cs47l90_open()` maps `cs47l90-dsp-voicectrl` to ADSP index 5 (DSP6) and `cs47l90-dsp-trace` to ADSP index 0 (DSP1), rejecting all other compressed DAIs.
- `cs47l90_adsp2_irq()` matches the L85 interrupt pattern: loop all seven DSPs, count serviced compressed IRQs, notify voice-trigger listeners with the 1-based DSP number, and report spurious interrupts if none handled the IRQ.
- Remove and error paths free per-DSP bus-error IRQs, remove DSPs, disable runtime PM, clear DSP IRQ wake, free the DSP IRQ, and release the Madera core.

State and persistence: runtime state is in `struct cs47l90`, `madera_priv`, DAPM state, regmap registers, FLL configuration, WM_ADSP instances, and bus-error IRQ registrations. ALSA controls and DAPM routes affect hardware registers and kernel state only. `madera->dapm` is installed while bound and cleared on component removal. There is no durable storage outside the device/register/firmware state managed by the kernel.

Dependencies and integration points: depends on Madera MFD/regmap/IRQ/register definitions, shared Madera ASoC helper functions, WM_ADSP/CS DSP code, ASoC component/DAI/DAPM/compress APIs, runtime PM, and the Madera notifier chain. It uniquely integrates with Madera DSP bus-error IRQ helpers and with DFC helper controls/routes. Machine drivers and user space integrate through the exported DAI names, DAPM widget names, ALSA controls, compressed capture endpoints, and voice-trigger notifier events.

Risks:
- The CS47L90 DSP setup differs from L35/L85: DSP rev 2, locked regions, `MADERA_DSP_CLOCK_2`, and bus-error IRQs. Copying assumptions from older variants can break DSP boot, memory access, or fault reporting.
- Bus-error IRQ allocation is interleaved with DSP init; unwind loops must free bus-error IRQs only for initialized cores and continue to remove DSPs.
- FLLAO uses a distinct helper and ID. Treating it like FLL3 would program the wrong clock path.
- DFC controls expose width/type selections for many channels. Invalid route/control pairing can produce format conversion faults or silent channels.
- The route graph intentionally omits L85 speaker and SPKDAT2 paths. Adding generic L85 routes would advertise nonexistent hardware paths.
- Compressed stream mapping is hard-coded by DAI name and DSP index, so firmware/DAI naming changes require coordinated code updates.

Test signals:
- Build tests should catch register/helper mismatches for DFC, FLLAO, DSP bus-error, and ADSP region-lock support.
- Probe tests should verify all seven DSPs initialize as rev 2, bus-error IRQs are allocated, FLL1/FLL2/FLLAO are initialized, runtime PM is enabled, and the component exposes the expected DAIs and controls.
- Audio route tests should cover AIF1/AIF2 8-channel, AIF3/AIF4, Slimbus1-3, HPOUT1-3, SPKDAT1, SPDIF1, EQ/DRC/LHPF/ISRC/ASRC, DFC1-DFC8, AEC, and RXANC paths.
- Firmware tests should load all seven DSPs, exercise bus-error IRQ reporting, open DSP6 voice-control and DSP1 trace compressed streams, and validate voice-trigger notifier delivery.
- Power tests should verify DAPM sequencing for ASYNCCLK, DFCCLK, DSP clocks, split MICBIAS supplies, HPOUT/SPKDAT output paths, and clean remove/error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l90.c -->
