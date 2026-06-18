# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Makefile

Purpose: kbuild rules for Samsung Sensor Platform sensorhub transport and IIO common module.

Important entries: `sensorhub-objs := ssp_dev.o ssp_spi.o` builds the sensorhub composite module. `obj-$(CONFIG_IIO_SSP_SENSORHUB) += sensorhub.o` gates transport support. `obj-$(CONFIG_IIO_SSP_SENSORS_COMMONS) += ssp_iio.o` gates IIO commons.

Control flow: selecting the sensorhub builds the SPI/device core pieces; selecting commons builds the IIO adapter object that depends on the sensorhub interfaces.

State and persistence: no runtime state in the Makefile.

Dependencies and integration: must remain synchronized with Kconfig and declarations in `ssp.h` plus other SSP source files not in this work item.

Risks and test signals: composite object membership determines module linkage; removing `ssp_spi.o` or `ssp_dev.o` would break sensorhub operation. Test signals are successful build for each symbol and modpost resolution between `ssp_iio` and `sensorhub` symbols.
