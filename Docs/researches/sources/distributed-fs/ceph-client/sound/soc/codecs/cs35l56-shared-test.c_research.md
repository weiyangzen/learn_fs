# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-shared-test.c

Purpose: KUnit coverage for CS35L56 shared speaker-ID and GPIO/pad helper logic across CS35L56 and CS35L63 variants and regmap transports.

Important APIs and data: test-private structures model a faux amplifier device, faux GPIO provider, mock register cache, shared `cs35l56_base`, and applied pad pull latch state. A mock GPIO chip implements input direction and `get()` from a bitmask. Custom regmap buses intercept reads/writes for GPIO/pad/update registers, synthesize `GPIO_STATUS1`, and fail unexpected register accesses. Tests exercise `cs35l56_configure_onchip_spkid_pads()`, `cs35l56_read_onchip_spkid()`, `cs35l56_check_and_save_onchip_spkid_gpios()`, and `cs35l56_get_speaker_id()`.

Control flow: suite init creates faux devices and regmaps for a specific part/revision/transport config. The mock `UPDATE_REGS` write simulates applying pad pull states into always-on latches. Parametrized cases verify GPIO status self-test behavior, speaker-ID bit assembly from on-chip GPIOs, pad input/pull configuration, property validation/rejection, absence behavior, vendor speaker ID stub override, direct `cirrus,speaker-id` property, and host GPIO `spk-id-gpios` software-node lookup. Seven KUnit suites reuse the same cases for L56 B0/B2 over SDW/SPI/I2C and L63 A1 over SDW.

State and persistence: all state is per-test and cleaned by KUnit actions: faux devices are destroyed, regmaps exited, and software nodes removed. Static stubbing hooks `cs_amp_get_vendor_spkid()` for the vendor-ID path.

Dependencies and integration: depends on KUnit, KUnit static stubs, faux devices, gpiolib, regmap, software nodes, seq_buf parameter descriptions, and public/shared CS35L56 and CS amp-library APIs. It imports `SND_SOC_CS35L56_SHARED` and `SND_SOC_CS_AMP_LIB`.

Risks: mock behavior intentionally allows only a narrow register set; new shared-helper register accesses will fail tests until the mock is updated. Host GPIO tests are skipped without reachable `CONFIG_GPIOLIB`. The suites validate logic but not real bus timing, IRQ, or PM behavior.

Test signals: this file is itself the test signal. Passing suites demonstrate stable speaker-ID handling across transport regmap configs, part variants, GPIO bit ordering, pull programming, invalid property rejection, vendor override precedence, software-node property path, and direct `cirrus,speaker-id` property path.
