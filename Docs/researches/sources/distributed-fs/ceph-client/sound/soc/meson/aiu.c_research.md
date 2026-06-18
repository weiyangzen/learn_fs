# sources/distributed-fs/ceph-client/sound/soc/meson/aiu.c

Purpose: Implements the AIU platform driver and CPU component for Meson8/GX audio output. It registers AIU FIFO and encoder DAIs, exposes the SPDIF source DAPM mux, initializes regmap/clock/IRQ resources, and registers HDMI/internal-codec control components.

Important APIs and functions: `aiu_probe()` is the platform probe. `aiu_of_xlate_dai_name()` converts two-cell DAI phandles into DAI names. `aiu_cpu_component_probe()` and remove keep the I2S pclk enabled for SPDIF source control. `aiu_clk_get()` and `aiu_clk_bulk_get()` fetch global, I2S, and SPDIF clocks. Static `aiu_cpu_dai_drv[]` defines I2S FIFO, SPDIF FIFO, I2S Encoder, and SPDIF Encoder DAIs.

Control flow: Probe allocates `struct aiu`, reads SoC match data, resets the device, maps registers, creates a 32-bit regmap, obtains I2S/SPDIF IRQs, fetches clocks, registers the CPU component/DAIs, registers HDMI control, and conditionally registers internal DAC control when the platform has an acodec. Error paths unregister already-registered components. Remove unregisters all components attached to the device.

State and persistence: `struct aiu` stores the SPDIF master clock, per-interface clock arrays, IRQs, and platform flags. Regmap-backed AIU register state persists in hardware. Component registration creates ASoC DAI and DAPM graph state.

Dependencies and integration points: Depends on dt-bindings `meson-aiu.h`, regmap MMIO, reset, clock, platform IRQ resources named `i2s` and `spdif`, FIFO/encoder ops from sibling files, and codec-control registrations. Compatible strings distinguish GXBB, GXL, Meson8, and Meson8b platform quirks.

Risks: All AIU subcomponents share one physical regmap, so component order and clock availability matter. HDMI control registration is mandatory after CPU registration; internal DAC registration is conditional. DAI phandle translation requires exactly two args and matching component id. Component probe keeps I2S pclk enabled for a control that touches I2S misc registers, which affects power behavior.

Test signals: Device probe on all compatible strings, reset and regmap initialization, DAI phandle parsing from DT, DAPM route visibility for FIFO-to-encoder paths, HDMI and acodec component registration, and playback through I2S/SPDIF on GXBB/GXL/Meson8 variants.
