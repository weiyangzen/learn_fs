<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.c

### Purpose
`quartet.c` implements Infrasonic Quartet support. It controls AK4620 ADC/DAC codecs over GPIO SPI, AK4113 S/PDIF receiver over I2C, external CPLD/system/monitor registers through GPIO latch sequences, custom clocking with S/PDIF and word-clock options, monitor/input/mute/phantom controls, virtual master volume, proc diagnostics, and synthetic EEPROM.

### Important APIs, Types, And Functions
`struct qtet_spec` stores AK4113 and cached SCR/MCR/CPLD register images. `struct qtet_kcontrol_private` describes reusable controls. Key functions are `qtet_ak4113_read/write`, `qtet_akm_write`, `qtet_akm_set_regs`, `qtet_akm_set_rate_val`, `reg_write`, `set_scr/set_mcr/set_cpld`, `proc_regs_read`, `qtet_mute_get/put`, `qtet_ain12_sw_get/put`, `qtet_php_get/put`, generic `qtet_sw_get/put`, `qtet_add_controls`, clock callbacks `qtet_is_spdif_master/get_rate/set_rate/set_mclk/set_spdif_clock/get_spdif_master_type`, `qtet_ak4113_change`, `qtet_spdif_in_open`, and `qtet_init`.

### Control Flow
Initialization forces ICE1724 into external-clock mode supplied by Quartet circuitry, allocates spec, overrides all clock/rate callbacks, advertises three external clock names, and assigns `qtet_spdif_in_open` to both S/PDIF and pro-open hooks. It initializes SCR with phantom off then codec power-up, clears MCR and CPLD, sets two stereo DAC/two stereo ADC topology, initializes AK4620 through AKM helpers, creates AK4113, sets AK4113 change callback, creates proc diagnostics, and sets initial rate to 44.1 kHz. Control building creates AKM controls, custom SCR/MCR/CPLD controls, virtual master volume, and AK4113 capture controls.

### State And Persistence
SCR, MCR, and CPLD are write-only external registers, so the driver caches their values in `qtet_spec`. Clock source/rate, input selection, monitor routing, mute, phantom power, and coax source all live in these cached register images plus hardware latches. AK4620 rate mode is updated on internal rate changes and when AK4113 reports an external S/PDIF rate change. No persistent EEPROM writes occur.

### Dependencies And Integration Points
The file uses core I2C/GPIO helpers, ALSA AK4113 and AKM helpers, ALSA controls/TLV/proc, and core clock callback surfaces. It integrates via `snd_vt1724_qtet_cards[]`, overrides `ice->hw_rates`, `ice->ext_clock_names/count`, `ice->spdif.ops.open`, and `ice->pro_open`.

### Risks
The GPIO latch protocol changes direction/mask broadly and must restore outputs correctly. Cached write-only register images can diverge from hardware after reset unless init/resume paths replay them; no explicit PM callbacks are present. `qtet_get_spdif_master_type` returns `-1` for internal mode even though core callers expect external indices only when external is active. Phantom power sequencing deliberately toggles voltage and enable in order; regressions could affect hardware safety. AKM allocation uses space for two descriptors but configures one codec with two chips, so assumptions must remain consistent.

### Test Signals
Test all internal rates, S/PDIF and both word-clock external clock selections, S/PDIF capture rate constraint, AK4113 external rate callback, mute and AK4620 soft mute, phantom power sequencing, analog input selectors, monitor routing switches, virtual master followers, proc `quartet` SCR/MCR/CPLD output, and recovery after card reset or suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.c -->
