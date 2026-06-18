# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.h

Purpose: Public attach and configuration header for VES1893/VES1993 DVB-S demodulators.

Important APIs/types/functions: `struct ves1x93_config` supplies demodulator I2C address, crystal input frequency, and `invert_pwm`. `ves1x93_attach(config, i2c)` is declared under `CONFIG_DVB_VES1X93`; the disabled inline stub warns and returns `NULL`.

Control flow: Board drivers pass a static config and I2C adapter to attach. The implementation detects the exact VES chip and returns a frontend with DVB-S ops or `NULL` on probe failure.

State and persistence: The header has no state; config data must remain alive for the attached frontend because the implementation uses it during initialization and symbol-rate programming.

Dependencies/integration: Includes `<linux/dvb/frontend.h>` and follows the media DVB attach pattern.

Risks and test signals: Verify Kconfig-disabled builds, board handling of `NULL` attaches, and config correctness for I2C address, `xin`, and PWM polarity. Header signature changes affect all old DVB-S board files using VES1x93.
