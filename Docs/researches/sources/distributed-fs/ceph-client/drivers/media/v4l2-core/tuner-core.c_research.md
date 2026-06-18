# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/tuner-core.c

## Purpose
`tuner-core.c` is the generic I2C analog TV/FM tuner subdevice driver. It presents a single V4L2 subdev driver named `tuner`, autodetects some tuner chips by address/probing, accepts bridge-provided tuner setup, attaches the chip-specific DVB tuner/analog demod implementation, tracks current tuner mode and frequency, and exposes V4L2 tuner operations to bridge drivers.

## Important APIs, types, and functions
The central runtime object is `struct tuner`, which embeds `struct dvb_frontend`, `struct i2c_client *`, `struct v4l2_subdev`, list linkage, current standard/frequencies/audmode/mode, mode mask, standby flag, type/config/name, and optional media pads. Important functions include `tuner_probe()`, `tuner_remove()`, `set_type()`, `tuner_s_type_addr()`, `tuner_s_config()`, `tuner_lookup()`, `set_mode()`, `set_freq()`, `set_tv_freq()`, `set_radio_freq()`, `tuner_fixup_std()`, `tuner_g_frequency()`, `tuner_s_frequency()`, `tuner_g_tuner()`, `tuner_s_tuner()`, `tuner_standby()`, `tuner_suspend()`, and `tuner_resume()`. Operation tables are `tuner_analog_ops`, `tuner_core_ops`, `tuner_tuner_ops`, `tuner_video_ops`, and `tuner_ops`.

## Control flow
Probe allocates `struct tuner`, initializes it as a V4L2 I2C subdev, seeds default radio and TV frequencies, optionally dumps I2C bytes, performs limited autodetection based on I2C address, determines radio/TV mode mask by scanning existing tuners on the same adapter, initializes media entity pads when enabled, selects a default mode, calls `set_type()`, and adds the object to the global `tuner_list`. `set_type()` detaches any previous tuner frontend, switches on the tuner type, attaches the chip-specific module, sets analog callbacks, updates media entity name, stores the mode mask, and often tunes immediately to the stored frequency. V4L2 tuner ops validate the requested mode, update mode/frequency/audmode/std state, and call analog frontend callbacks.

## State and persistence behavior
State is in memory per I2C client. `tv_freq`, `radio_freq`, `std`, `audmode`, `mode`, `mode_mask`, `standby`, `type`, and `config` are retained while the subdevice exists and restored or re-applied on resume. Module parameters (`debug`, `tv_range`, `radio_range`, `pal`, `secam`, `ntsc`, `addr`, `no_autodetect`, `show_i2c`) provide global configuration and compatibility behavior. There is no disk persistence.

## Dependencies and integration points
The file integrates V4L2 subdev APIs, I2C driver core, DVB frontend tuner ops, analog demod ops, media controller entities/pads, and many tuner-specific attach/probe functions (`tda829x`, `tea576x`, `xc2028`, `xc5000`, `tda18271`, `xc4000`, simple tuner, and others). With `CONFIG_MEDIA_ATTACH`, attach symbols are requested dynamically to avoid static links.

## Risks and edge cases
Autodetection is address-based and intentionally heuristic; wrong detection can bind the wrong chip or suppress a radio/TV peer. `set_type()` detaches prior ops before reattaching, so error paths must leave a safe absent state. Frequency units differ between TV and radio, making conversion bugs easy. Global `tuner_list` is not explicitly locked in this file and relies on I2C core serialization during probe plus normal driver call context. Module parameters can force nonstandard video standard variants and should be tested carefully.

## Test signals
Test probing with common tuner addresses, bridge-driven `s_type_addr`, separate radio and TV tuners on one adapter, TDA9887 IF demod special media entity setup, TV/radio frequency range clamping, PAL/SECAM/NTSC fixup parameters, suspend/resume with active and standby tuners, and remove after failed or repeated type setup. `VIDIOC_LOG_STATUS`, `g_frequency`, `s_frequency`, `g_tuner`, and `s_tuner` provide visible behavior.
