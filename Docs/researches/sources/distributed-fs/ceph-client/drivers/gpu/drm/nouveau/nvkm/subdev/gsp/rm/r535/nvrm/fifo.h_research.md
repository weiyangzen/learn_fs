# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/fifo.h

Purpose: defines R535 FIFO, channel, engine-info, constructed-falcon, context-promotion, scheduling, and RC-event ABI structures.

Important APIs/types: `NV2080_CTRL_FIFO_GET_DEVICE_INFO_TABLE_PARAMS` returns engine table entries with engine data, PBDMA IDs, fault IDs, and names. `ENGINE_INFO_TYPE` defines indexes into the `engineData` array. `NV2080_CTRL_CE_GET_FAULT_METHOD_BUFFER_SIZE_PARAMS` and `NV2080_CTRL_INTERNAL_GET_CONSTRUCTED_FALCON_INFO_PARAMS` support context/falcon buffer sizing. `NV_CHANNELGPFIFO_ALLOCATION_PARAMETERS` is the large channel allocation payload, carrying GP FIFO location, flags, VAS handle, UserD memory, engine type, channel ID, subdevice mask, instance/UserD/RAMFC/method-buffer memory descriptors, error notifiers, and security fields. `NVA06F_CTRL_BIND_PARAMS`, `NVA06F_CTRL_GPFIFO_SCHEDULE_PARAMS`, and `NV2080_CTRL_GPU_PROMOTE_CTX_PARAMS` support channel binding, scheduling, and GPU context promotion. `rpc_rc_triggered_v17_02` reports recovery/RC events in R535 form.

Control flow and state: the header is declarative, but its payloads are central to FIFO initialization. Device info table results populate Nouveau runlist/engine metadata. Channel allocation creates persistent RM channel objects over Nouveau-allocated instance, UserD, RAMFC, and method-buffer memory. Promote context controls attach context buffers to a channel.

Dependencies and integration: used by R535/R570 FIFO and GR code, with R570 overriding several definitions in its own header. It depends on engine enumerations and RM memory descriptor types.

Risks: `ENGINE_INFO_TYPE` ordering is explicitly compatibility-sensitive. Channel flags are dense bitfields; incorrect USERD page/index, privilege, or skip-map settings can break submissions. Memory descriptor address-space/cache attributes must match actual backing memory. RC payload layout differs in R570, so versioned headers must be paired with matching callbacks.

Test signals: engine discovery should produce correct runlists and instance counts, channel allocation should submit GP FIFO work, context promotion should succeed for GR/CE/video engines, RC events should map CHIDs back to Nouveau channels, and fault method buffer sizing should match RM expectations.
