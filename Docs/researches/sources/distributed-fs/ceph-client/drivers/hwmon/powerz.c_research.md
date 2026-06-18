# sources/distributed-fs/ceph-client/drivers/hwmon/powerz.c

Purpose: USB hwmon driver for ChargerLAB POWER-Z KM002C/KM003C USB-C testers. It sends a vendor command over bulk OUT, reads a packed sensor frame over bulk IN, and exposes voltage/current/temperature channels.

Important APIs/types/functions: `struct powerz_sensor_data` describes the 64-byte response layout. `struct powerz_priv` owns a DMA-safe transfer buffer, mutex, completion, URB, and status. `powerz_read_data()` orchestrates command and data URB phases; `powerz_read()` converts fields to hwmon units.

Control flow: probe allocates state and one URB, registers hwmon. On each read, the mutex serializes access, command bytes are written to endpoint 0x01, the command completion resubmits the same URB for endpoint 0x81, and the reader waits up to 5 ms for completion.

State and persistence: no cached measurements; every sysfs read triggers USB I/O. Disconnect kills and frees the URB under the mutex and sets it NULL.

Dependencies/integration: USB core, hwmon, completions, DMA annotations, little-endian conversion helpers.

Risks: the response structure contains unknown fields and relies on exact firmware layout. A single URB is reused for both phases, so locking and disconnect ordering are critical. Timeout is short and returns `-EIO`.

Test signals: USB ID matching, bulk endpoint transfers, disconnect during read, short frame handling, labels for VBUS/VCC/DP/DM/VDD, and unit sanity for averages and temperature.
