# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.c

Purpose: implements the QAT data-compression service handler. It registers a `service_hndl` named `qat_compression`, creates per-device compression instances from ADF config, exposes NUMA-aware instance selection, and allocates shared compression overflow/skid DMA storage.

Important APIs and functions: `qat_compression_register()` and `qat_compression_unregister()` bind the service into the ADF service bus. `qat_compression_event_handler()` reacts to `ADF_EVENT_INIT` and `ADF_EVENT_SHUTDOWN`. `qat_compression_create_instances()` reads `ADF_NUM_DC` and per-instance `ADF_DC%d...` keys, creates DC TX/RX transport rings, initializes `qat_instance_backlog`, and attaches `accel_dev->dc_data`. `qat_compression_get_instance_node(node, alg)` chooses a started accelerator and least-used `qat_compression_instance`, filtering ZSTD/LZ4S requests through `accel_capabilities_ext_mask`. `qat_compression_put_instance()` releases both instance and device references.

Control flow: service init allocates `adf_dc_data` first, mapping a `QAT_COMP_MAX_SKID` overflow buffer with `dma_map_single()`, then creates rings. Runtime clients call `qat_compression_get_instance_node()`, submit through `dc_tx`, and receive completions through the RX ring callback `qat_comp_alg_callback`. Shutdown frees DMA data and removes all rings/instances.

State and persistence: state is in `accel_dev->compression_list`, per-instance atomic `refctr`, backlog list/lock, and `accel_dev->dc_data`. The overflow buffer persists for the accelerator service lifetime only. Device references are mirrored with instance references via `adf_dev_get()`/`adf_dev_put()`.

Dependencies and integration points: depends on ADF config, device manager, transport rings, QAT firmware request/response sizes, and compression algorithm callbacks declared outside this file. Integrates with capability masks and NUMA placement.

Risks: several error returns inside `qat_compression_create_instances()` occur after an instance has been linked; unlike the initial allocation failure path, not all of them jump to common cleanup. This can leave partially created rings/list entries for the caller to handle poorly. The ZSTD/LZ4S filter accepts either extended capability bit in a combined mask rather than requiring an algorithm-specific bit. Test focus should cover config parse failures after partial ring creation, DMA mapping failure cleanup, reference balancing, NUMA fallback, and unsupported extended-compression algorithms.
