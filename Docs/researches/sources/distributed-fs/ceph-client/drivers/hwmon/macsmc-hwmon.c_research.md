# sources/distributed-fs/ceph-client/drivers/hwmon/macsmc-hwmon.c

Purpose: Apple Silicon SMC hwmon platform driver that dynamically exposes temperature, voltage, current, power, and fan sensors described by device tree child nodes.

Important APIs/types/functions: `struct macsmc_hwmon` owns dynamic channel info arrays and sensor/fan collections. `macsmc_hwmon_read_key()` decodes SMC key data types including IEEE-754 float, 48.16 fixed point, and integer formats. `macsmc_hwmon_create_sensor()` and `macsmc_hwmon_create_fan()` parse DT keys. Hwmon callbacks handle read, write, visibility, and labels.

Control flow: probe requires an OF hwmon node from the parent Apple SMC MFD, allocates state, walks child nodes by prefixes `current-`, `fan-`, `power-`, `temperature-`, and `voltage-`, validates SMC keys, builds dynamic hwmon config arrays, then registers `macsmc_hwmon`. Reads fetch SMC keys live and scale to hwmon units; fan target writes optionally switch fans to manual mode.

State and persistence behavior: sensor metadata and labels are devm-managed. Values are not cached. Fan manual state is tracked per fan and writes to SMC mode/target keys persist in controller state until reset or a write of zero returns to automatic mode.

Dependencies and integration points: integrates with the Apple SMC MFD API, OF child-node schemas, hwmon core, platform bus, and the unsafe module parameter `fan_control`.

Risks: fan control is intentionally gated because the SMC does not sanity-check target speeds. Float conversion clamps overflow/underflow and must remain careful. Bad or missing DT key definitions silently reduce sensor count, and probe fails if no valid sensors remain.

Test signals: DT parsing tests for each sensor prefix, SMC key type conversion fixtures, label visibility checks, fan min/max/target/mode behavior with `fan_control` off and on, and probe failure when all keys are invalid.
