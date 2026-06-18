# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.c

## Purpose
Implements the Matrox Maven/MGA-TVO external TV encoder driver as an I2C client. It attaches the encoder to the primary matroxfb head, exposes the secondary output through `struct matrox_altout`, computes monitor and TV timing register images, pushes long encoder register sequences over I2C/SMBus, and provides V4L2-style TV controls including brightness, contrast, saturation, hue, gamma, test output, and deflicker.

## Important APIs, Types, and Functions
- `struct maven_data` links an I2C client to the primary `matrox_fb_info` and stores detected MGA-TVO revision.
- `maven_controls[]` and `maven_gamma[]` define user-visible controls and hardware gamma presets.
- `maven_get_reg()`, `maven_set_reg()`, and `maven_set_reg_pair()` implement byte and word register I/O over the I2C adapter.
- `matroxfb_PLL_mavenclock()`, `matroxfb_mavenclock()`, and `DAC1064_calcclock()` compute encoder and monitor PLL parameters.
- `maven_init_TVdata()`, `maven_compute_timming()`, and `maven_program_timming()` prepare and program register images for PAL, NTSC, and monitor modes.
- `maven_set_control()` updates stored control state and writes corresponding live encoder registers.
- `maven_altout` is the alt-output operation table installed in `minfo->outputs[1]`.
- `maven_probe()` and `maven_remove()` are the I2C driver entry points registered by `module_i2c_driver()`.

## Control Flow
During probe, the driver checks adapter functionality for SMBus word/byte and protocol-mangling support, allocates `maven_data`, then calls `maven_init_client()`. Initialization derives the owning `matrox_fb_info` from the `i2c_bit_adapter`, installs the secondary output under `altout.lock`, reads register 0xB2 to classify the encoder as MGATVO_B or MGATVO_C, and fills TV control defaults. Mode setting enters through the alt-output compute callback: monitor modes get DAC1064-style clock and display timing registers; TV modes start from PAL/NTSC templates, find exact line clocks, compute horizontal/vertical resampling parameters, and set output mode to composite/S-Video. Programming either writes the monitor timing register list or calls `maven_init_TV()` for the full TV sequence. Start triggers a resync by writing register 0x95.

## State and Persistence
State is split between `maven_data`, `minfo->outputs[1]`, `minfo->altout.tvo_params`, and the shared `minfo->hw.maven` register image. The I2C client data owns the Maven attachment lifecycle. Control values persist only in memory and are reapplied during timing computation; live control changes also update hardware immediately.

## Dependencies and Integration Points
Depends on `matroxfb_maven.h`, shared PLL/VGA helpers from `matroxfb_misc.h`, DAC constants from `matroxfb_DAC1064.h`, Linux I2C APIs, and `<linux/matroxfb.h>` output/control definitions. It integrates with Matrox software I2C adapters via `struct i2c_bit_adapter` and with the fb output routing layer through `struct matrox_altout`.

## Risks
The register programming sequence is long, timing-sensitive, and largely hardware-magic. I2C read helpers log failures but still return the uninitialized local destination masked to 8 bits if `i2c_transfer()` fails, which can obscure hardware communication errors. Arithmetic in clock and resampling selection can reject modes or produce marginal values. Control offsets assume `struct matrox_fb_info` layout. Removal must clear `outputs[1]` under the lock to avoid stale output callbacks.

## Test Signals
Validation should include I2C probe on an adapter with required functionality, successful secondary output registration, correct MGATVO_B/C detection, mode verification for PAL/NTSC/monitor, visible monitor pass-through and TV output, and live control writes to brightness/contrast/gamma/deflicker registers. Negative signals include `-EINVAL` for unsupported modes, failed clock matching, and I2C write/read error logs.
