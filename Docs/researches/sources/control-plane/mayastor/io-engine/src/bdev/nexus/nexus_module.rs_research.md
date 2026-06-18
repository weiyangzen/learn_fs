<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_module.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_module.rs

Purpose: registers the SPDK bdev module that owns nexus bdev instances, provides module lifecycle callbacks, declares per-I/O context size, and emits JSON configuration for existing nexus devices.

Important APIs/types/functions: `NEXUS_MODULE_NAME`, `NexusModule`, `NexusModule::current`, `current_opt`, `WithModuleInit::module_init`, `WithModuleFini::module_fini`, `WithModuleGetCtxSize::ctx_size`, `WithModuleConfigJson::config_json`, `BdevModuleBuild`, and `register_module`.

Control flow: `register_module` builds and registers a module named `NEXUS_CAS_MODULE` with init/fini/context-size/config-json callbacks. `ctx_size` returns `size_of::<NioCtx>()` so SPDK allocates enough driver context for every nexus bdev I/O. `config_json` iterates current nexus bdevs and writes `create_nexus` JSON RPC entries with name, bdev UUID, child URIs, and requested size.

State and persistence: no runtime state is stored in this type. The generated config JSON can be used as external configuration persistence, but persistent nexus info is handled elsewhere.

Dependencies/integration: depends on `spdk_rs` bdev module traits, `NioCtx` from the I/O module, `nexus_iter`, and `serde_json`. `Nexus::new` uses `NexusModule::current().bdev_builder()`.

Risks: `current` panics when called before registration. Config JSON uses the bdev UUID, not necessarily the separate nexus UUID used by v2 creation. The config only includes basic create parameters and omits NVMe reservation parameters and persistence keys, so it may not fully reconstruct advanced nexus state.

Test signals: module registration before nexus creation, context size matching `NioCtx`, config JSON for zero and multiple nexuses, UUID field expectations for v1/v2 nexus names, and `current_opt` before/after registration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_module.rs -->
