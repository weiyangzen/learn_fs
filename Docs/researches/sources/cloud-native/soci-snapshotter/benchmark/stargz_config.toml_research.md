## sources/cloud-native/soci-snapshotter/benchmark/stargz_config.toml

Purpose: placeholder stargz benchmark configuration file.

Important APIs/types/functions: none; the file is empty.

Control flow: not executable. If passed to a stargz process, behavior depends entirely on the external stargz snapshotter's defaults for an empty config.

State and persistence: no state and no persisted settings.

Dependencies and integration: benchmark launch helpers pass a config path to the stargz binary; this file can satisfy that argument while leaving defaults active.

Risks and test signals: empty config may be accepted or rejected depending on the external stargz snapshotter version. No tests cover the file.
