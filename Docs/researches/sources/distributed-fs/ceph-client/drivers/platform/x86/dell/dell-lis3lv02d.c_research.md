# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-lis3lv02d.c

Purpose: Instantiates an I2C `lis3lv02d` accelerometer client for Dell SMO88xx ACPI devices that lack usable I2C resources.

Important APIs/types/functions: DMI product-to-address table, `probe_i2c_addr` parameter, `detect_lis3lv02d()` WHO_AM_I probe, main I801 adapter discovery, `instantiate_i2c_client()` work item, and I2C bus notifier.

Control flow/state/persistence: Init first requires an SMO88xx platform device. It then uses DMI or opt-in SMBus probing, registers an I2C notifier, and queues work to create the I2C client. Exit unregisters notifier, cancels work, and unregisters the client. Global state tracks the chosen address and client.

Dependencies/integration: ACPI SMO IDs, DMI, I2C core, I801 adapter naming, workqueues, and generic `lis3lv02d`.

Risks/test signals: SMBus probing can be dangerous and is opt-in. Test known DMI systems, unknown systems without probing, opt-in scan, late adapter registration, and cleanup after client removal.
