# Research: sources/distributed-fs/ceph-client/include/linux/mfd/madera/core.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/core.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/madera/core.h

**Purpose:** Defines internal shared state and constants for Cirrus Logic Madera codec MFD devices such as CS47L35, CS47L85, CS47L90/91/92/93, WM1840, CS47L15, and CS42L92.

**Important APIs and types:** `enum madera_type`, MCLK indexes, GPIO and MICBIAS limits, notifier event bits, extensive GPIO-function constants, and `struct madera`. The structure contains 16-bit and 32-bit regmaps, device identity, core regulators, DCVDD/internal-LDO state, platform data, IRQ child state, clock bulk data, MICBIAS child counts, DAPM pointer/lock, headphone/output fault state, and notifier chain.

**Control flow:** The transport-specific parent probes the codec, identifies type/revision, creates regmaps, powers supplies/clocks, configures IRQ support, and exposes `struct madera` to child drivers. ASoC, GPIO, regulator, pinctrl, extcon, and IRQ children coordinate through shared regmap and notifier state.

**State and persistence:** Runtime state includes power rails, clock handles, IRQ mappings, DAPM association, output clamp/short flags, headphone enable bitmap, and notifiers. Persistent effects are hardware register changes and platform/firmware configuration.

**Dependencies and integration:** Depends on clk, GPIO descriptors, interrupts, Madera pdata, mutex, notifier, regmap, and regulator consumers; integrates heavily with ASoC DAPM through a forward-declared context.

**Risks:** This is an internal MFD contract; external use can couple to unstable details. GPIO-function constants are device-specific and must match the actual codec. Shared DAPM pointer access requires the provided lock discipline.

**Test signals:** Probe matrix across supported `madera_type` values, regulator/clock failure unwinds, IRQ child registration tests, GPIO function validation, and notifier tests for voice trigger, HPDET, and MICDET events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/core.h -->
