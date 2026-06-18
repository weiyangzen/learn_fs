# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-common.c

Purpose: implements bus-independent V4L2 behavior for Silicon Labs Si470x FM radio receivers. USB and I2C frontends provide register read/write and open/release/querycap callbacks; this file handles tuning, seek, RDS read/poll, volume/mute controls, and common ioctl tables.

Important APIs and functions: exported symbols are `si470x_ctrl_ops`, `si470x_viddev_template`, `si470x_set_freq`, `si470x_start`, and `si470x_stop`. Internal helpers include `si470x_set_band`, `si470x_set_chan`, `si470x_get_step`, `si470x_get_freq`, `si470x_set_seek`, and `si470x_rds_on`. File ops implement RDS `read`, `poll`, delegated `open`, and delegated `release`. V4L2 handlers cover tuner/frequency/seek/band enumeration and controls.

Control flow: bus drivers initialize `struct si470x_device` callbacks and copy `si470x_viddev_template`. Starting the radio programs `POWERCFG`, enables RDS/STC interrupts and de-emphasis, programs band/spacing/volume in `SYSCONFIG2`, then restores the channel. Frequency setting clamps within current band and converts to channel number based on spacing. If a requested frequency is outside the current band, the common ioctl switches to the 76-108 MHz band before tuning. Hardware seek optionally switches to an exact requested band, starts seek bits, waits for completion, clears seek, and reports timeout as `-ENODATA`. RDS read/poll lazily enables RDS and drains 3-byte V4L2 RDS blocks from the circular buffer filled by bus interrupt handlers.

State and persistence: common state lives in `struct si470x_device`: register cache, current band, circular RDS buffer indices, waitqueue, completion, and bus callbacks. It is volatile and owned by the USB/I2C device.

Dependencies and integration points: depends on `radio-si470x.h`, V4L2 core/control/event APIs, completion/waitqueue primitives, and bus-specific register operations. It integrates with USB/I2C files through exported symbols and function pointers.

Risks: RDS buffer read/copy is not explicitly locked despite comments/history about avoiding sleeping under locks; concurrent producer/consumer races rely on simple indices. `copy_to_user` failure breaks without returning `-EFAULT` if some paths are hit. Seek band selection requires exact low/high matches when bounds are supplied. `FREQ_MUL` is defined using a floating literal in the header snapshot, which is unusual.

Test signals: common V4L2 compliance through both USB and I2C drivers, frequency step/band conversion tests for 50/100/200 kHz, tune and seek completion timeouts, RDS read/poll blocking and wraparound, volume/mute controls updating cached registers, and module symbol dependency checks.
