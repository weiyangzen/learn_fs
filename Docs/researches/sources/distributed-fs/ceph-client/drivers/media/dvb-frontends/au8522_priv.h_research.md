# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_priv.h

Purpose: Defines the private AU8522 hybrid-device contract shared by the digital demodulator and analog decoder files. It centralizes `struct au8522_state`, mode constants, pad indexes, shared helper prototypes, and the AU8522 register map/bit-value definitions used by both analog and digital programming sequences.

Important APIs/types/functions: `AU8522_ANALOG_MODE`, `AU8522_DIGITAL_MODE`, and `AU8522_SUSPEND_MODE` describe the active hardware function. `enum au8522_pads` describes media-controller pads when enabled. `struct au8522_state` owns the I2C client/adapter, shared tuner-I2C properties and hybrid instance list, board `struct au8522_config`, DVB frontend, cached digital tune state, LED state, V4L2 subdev/control state, analog input/std fields, and optional media pads. Shared routines include `au8522_writereg()`, `au8522_readreg()`, `au8522_init()`, `au8522_sleep()`, `au8522_get_state()`, `au8522_release_state()`, digital/analog I2C-gate control, and `au8522_led_ctrl()`.

Control flow: This header has no executable logic, but it defines the cross-file lifecycle. Attach paths call `au8522_get_state()` so analog and digital frontends can share one physical AU8522 instance, set `operational_mode`, then call common init/sleep and register helpers. Mode-specific code writes the register constants declared here to switch between ATSC/J83B, analog CVBS/S-video/RF, audio, GPIO, VBI, and transport-stream behavior.

State and persistence: State is entirely runtime kernel memory plus volatile AU8522 registers. The hybrid tuner instance list and `tuner_i2c_props` are the persistence-like mechanism within a boot session for sharing one I2C-addressed chip among multiple frontend/subdevice users.

Dependencies/integration: Includes Linux I2C, DVB frontend, V4L2 subdev/control/media-controller headers, `au8522.h` for public config, and `tuner-i2c.h` for hybrid sharing. Consumers include `au8522_dig.c` and the analog decoder implementation.

Risks and test signals: Validate analog/digital attach/release reference behavior, mode transitions, suspend/resume paths, I2C gate state across tuner calls, LED control availability, and media-controller pad setup. Because this header exposes a large raw register map, regressions are likely when symbolic values drift from data-sheet meanings or when a digital sequence accidentally reuses analog-only constants.
