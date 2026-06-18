# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_tee.c

Purpose: Implements the legacy MEI PXP TEE component backend and streaming command path used for PXP firmware commands and HuC load/auth flows.

Important APIs/functions: `intel_pxp_tee_component_init()`, `intel_pxp_tee_component_fini()`, `intel_pxp_tee_cmd_create_arb_session()`, `intel_pxp_tee_end_arb_fw_session()`, and `intel_pxp_tee_stream_message()`. Component callbacks bind/unbind the MEI device and may trigger HuC loading.

Control flow: Component init optionally allocates a one-page LMEM streaming command object on dgfx, then registers a typed component. Bind stores `pxp_component`, sets `tee_dev`, optionally adds a device link, loads HuC via GSC if required, and initializes PXP hardware if runtime active. Normal message I/O serializes under `tee_mutex`, sends then receives via component ops with 5s timeout. Streaming message copies input to the pinned command object and calls component `gsc_command`. Session create and stream-key invalidation build API 4.2 packets; invalidation retries up to three times for coherency.

State/persistence: Maintains `pxp_component`, `dev_link`, `pxp_component_added`, and `stream_cmd` object/vaddr. Firmware platform config failures set `platform_cfg_is_bad`.

Dependencies/integration: Linux component framework, MEI PXP interface, i915 component IDs, GEM LMEM/internal mapping, HuC/GSC loading, runtime PM, and PXP command ABI 4.2/4.3.

Risks: Component binding is asynchronous relative to i915 probe and PM, so all message paths must handle `-ENODEV`. Stream command supports one page only. Device-link policy differs for HECI PXP platforms. Long TEE timeouts hold `tee_mutex`. Failed component unregister or missed hardware fini can leave interrupts/hardware enabled.

Test signals: Component bind/unbind logs, HuC load/auth result, PXP readiness status waiting for component bound, and TEE send/recv error logs.
