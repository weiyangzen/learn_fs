# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Kconfig

Purpose: Kconfig definition for the virtual DVB test driver.

Important APIs/types/functions: defines `CONFIG_DVB_VIDTV` as tristate "Virtual DVB Driver (vidtv)", depending on DVB core, media support, and I2C, and selecting CRC32.

Control flow: when enabled, Kbuild includes the virtual tuner, demodulator, and bridge/mux modules from the vidtv Makefile.

State and persistence: build-time only.

Dependencies and integration points: depends on DVB and I2C frameworks because vidtv models bridge-to-demod/tuner attachment via virtual I2C clients. CRC32 supports PSI table CRC generation in non-listed PSI code used by the listed channel/mux files.

Risks: missing CRC32 selection breaks PSI table generation; missing I2C prevents virtual module probing.

Test signals: Kconfig dependency tests and module build/load of `dvb_vidtv_*` components.
