# sources/distributed-fs/ceph-client/samples/coresight/coresight-cfg-sample.c

Purpose: module that registers an alternate CoreSight `autofdo2` system configuration with preset strobing parameters.

Important APIs/functions: defines `struct cscfg_config_desc`, `struct cscfg_load_owner_info`, feature reference names, preset parameter table, `cscfg_load_config_sets`, and `cscfg_unload_config_sets`.

Control flow: init passes the config and empty feature list to the CoreSight syscfg loader. Exit unloads all sets owned by the module owner handle.

State and persistence: static preset tables and descriptors exist while the module is loaded; registered CoreSight syscfg state is removed on module unload.

Dependencies and integration: integrates with CoreSight ETM syscfg infrastructure and references the built-in `strobing` feature by name.

Risks: feature name and parameter count must match CoreSight expectations. Incorrect preset dimensions would misconfigure tracing. This is a registration example and does not validate hardware availability itself.

Test signals: build/load with CoreSight syscfg support, inspect registered configurations, select `autofdo2` presets, and unload to confirm owner cleanup.
