<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_hps_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_hps_i2c.c

## Purpose

This I2C driver exposes a ChromeOS Human Presence Sensor as `/dev/cros-hps` and controls sensor power with an enable GPIO. It intentionally does not implement data read/write; opening the misc device powers the sensor through runtime PM, and closing it releases power.

## Important APIs, Types, And Functions

`struct hps_drvdata` holds the I2C client, miscdevice, and enable GPIO. `hps_open()` calls `pm_runtime_resume_and_get()`, and `hps_release()` calls `pm_runtime_put()`. `hps_suspend()` and `hps_resume()` drive the GPIO low/high. Probe obtains the `enable` GPIO, registers a misc device, powers the sensor off, and enables runtime PM.

## Control Flow

Firmware leaves HPS powered before Linux probe, so the driver requests the GPIO as output-high to preserve state while binding. After misc registration it powers HPS down and enables runtime PM. An open file descriptor resumes the device and sets the GPIO high; release drops the runtime PM reference. Driver removal disables PM, deregisters the misc device, and restores the default powered-on state.

## State And Persistence

State is volatile and consists of the GPIO output and runtime PM usage count. No sensor configuration or user data is persisted. Removal deliberately powers HPS on to return control to firmware/default behavior.

## Dependencies And Integration Points

The driver depends on I2C enumeration, ACPI ID `GOOG0020`, gpiolib consumer API, miscdevice registration, and runtime PM. It also has an I2C modalias `cros-hps`.

## Risks

There is no per-open serialization beyond runtime PM counting, so multiple opens keep the device powered until the last close. `hps_resume()` always powers on, including system resume paths, so platform expectations must match. Missing or misdescribed `enable` GPIO fails probe.

## Test Signals

Check ACPI/I2C probe, `/dev/cros-hps` creation, GPIO transitions on open/close, runtime PM reference balancing with multiple opens, suspend/resume GPIO behavior, and removal restoring the enable line high.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_hps_i2c.c -->
