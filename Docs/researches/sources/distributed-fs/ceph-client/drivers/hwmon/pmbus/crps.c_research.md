# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/crps.c

Purpose: PMBus driver for Intel Common Redundant Power Supply model `03NK260` / `intel_crps185`.

Important APIs/types/functions: `crps_info` declares one default-linear PMBus page with input/output voltage, current, power, temperature, fan, and status capabilities. `crps_probe()` reads `PMBUS_MFR_MODEL`, validates exact length and string, runs `pmbus_do_probe()`, and reports failures through `dev_err_probe()`.

Control flow: OF/I2C matching binds the driver, probe validates model identity, PMBus core creates hwmon attributes from the descriptor, and all subsequent sensor reads use standard PMBus core behavior.

State and persistence: no private state. The only stateful action is PMBus core registration.

Dependencies and integration: depends on I2C, OF matching, PMBus core, and standard PMBus linear formats.

Risks: exact model length/string matching rejects compatible units with alternate manufacturer strings. No explicit adapter functionality check is performed before block read. The descriptor assumes default linear formats for all sensors.

Test signals: successful probe with model `03NK260`, rejection of other models, hwmon attributes for all declared sensors, and error paths for failed model read and failed PMBus probe.
