## sources/distributed-fs/ceph/src/rgw/rgw_object_expirer.cc

Purpose: standalone daemon entry point for RGW object expiration processing.

Important APIs/functions: `StoreDestructor` closes the SAL driver on exit. `usage()` delegates generic server usage. `main()` initializes Ceph, config store, site config, storage driver, constructs `RGWObjectExpirer`, starts its processor, and sleeps forever on `rgw_objexp_gc_interval`.

Control flow: parses args/usage, calls `global_init()`, daemonizes if configured, initializes an `io_context_pool`, creates a config store using `rgw_config_store`, loads `SiteConfig`, opens storage with most optional services disabled and object expiration enabled, then runs the expirer background processor.

State and persistence: expiration state and object deletions are handled by `RGWObjectExpirer` and the SAL driver. This file owns process-lifetime driver and context pool.

Dependencies/integration: depends on Ceph global init/config, SAL DriverManager/config store, site config, RGW object expirer core, and RGW object/log/usage support.

Risks and test signals: the infinite sleep loop means shutdown relies on process signals outside this file. Startup has several `exit(1)` paths. Tests should cover missing config store, site load failure, storage init failure, daemonized startup, and that driver close happens through `StoreDestructor` on early returns after storage creation.
