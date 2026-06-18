# sources/distributed-fs/ceph-client/include/media/drv-intf/s3c_camif.h

Purpose: Platform data for Samsung S3C24xx/S3C64xx CAMIF sensor wiring.

Important APIs/types/functions: `s3c_camif_sensor_info` embeds I2C board info, sensor clock frequency, media bus type, I2C bus number, bus polarity flags, and optional FIELD-signal usage. `s3c_camif_plat_data` adds sensor info plus `gpio_get`/`gpio_put` callbacks.

Control flow: Platform code provides sensor description and GPIO reservation callbacks. CAMIF probe/configuration uses this to register the sensor subdevice, program sensor clocking, and configure bus flags.

State and persistence: Configuration is static platform data; GPIO ownership and runtime capture state live in the CAMIF driver.

Dependencies and integration: Depends on I2C and V4L2 media-bus enums. Integrates old Samsung camera hosts with board-file sensor data.

Risks and test signals: Risks include invalid sensor clock, bus polarity mismatch, missing GPIO release, and wrong FIELD usage. Test probe/remove GPIO pairing, sensor I2C creation, clock rate, and frame capture with each bus flag combination.
