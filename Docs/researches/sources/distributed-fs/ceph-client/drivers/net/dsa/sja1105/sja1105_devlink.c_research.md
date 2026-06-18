## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_devlink.c

Purpose: this file adds devlink integration for SJA1105 by exposing the switch static configuration as a devlink region snapshot and reporting the ASIC identity through devlink info.

Important APIs, types, and functions: `sja1105_static_config_get_max_size()` constructs a dummy static config with every table set to maximum entry count and computes its packed length. `sja1105_region_static_config_snapshot()` allocates a buffer and serializes the current static config with `static_config_buf_prepare_for_upload()`. `sja1105_setup_devlink_regions()` creates devlink regions, `sja1105_teardown_devlink_regions()` destroys them, `sja1105_devlink_info_get()` reports `DEVLINK_INFO_VERSION_GENERIC_ASIC_ID`, and public setup/teardown wrappers are `sja1105_devlink_setup()` and `sja1105_devlink_teardown()`.

Control flow: setup allocates `priv->regions`, calculates each region size dynamically, and calls `dsa_devlink_region_create()` with one snapshot slot. The static-config snapshot path retrieves `priv` from the DSA devlink handle, computes the current packed length and maximum region length, allocates a maximum-sized zeroed buffer, and packs the current config into it. Teardown iterates registered regions and frees the region pointer array. Info-get simply writes the selected chip info name as the fixed ASIC ID.

State and persistence: persistent software state is `priv->regions`, an array of devlink region pointers. The exposed snapshot data is not live state; it is an allocated copy of `priv->static_config` serialized in hardware-upload format and freed by the region destructor. Region sizing is derived from table ops at setup/snapshot time to avoid hard-coded limits.

Dependencies and integration points: this file depends on DSA devlink helpers, SJA1105 static config table ops, static config serialization, and `priv->info->static_ops`/`device_id`. It is called by the main SJA1105 setup/teardown path and by devlink info callbacks in DSA.

Risks: if dummy static-config initialization fails, max size becomes zero and region creation or snapshot allocation may fail. The snapshot allocates `max_len` but packs only the current `len`, so consumers must interpret trailing zeroes based on serialized config format. Setup cleanup destroys already created regions but relies on `priv->regions` entries being initialized. Static config table max-entry metadata must stay in sync with serializer support.

Test signals: `devlink region show` should list `static-config`, snapshots should succeed and contain a parseable static-config image after setup and after config reloads, failed allocation paths should unwind created regions, and `devlink dev info` should report the selected SJA1105/SJA1110 chip name as the generic ASIC ID.
