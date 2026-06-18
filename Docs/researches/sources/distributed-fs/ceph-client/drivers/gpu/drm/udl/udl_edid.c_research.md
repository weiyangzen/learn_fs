<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.c

Purpose: Reads monitor EDID over DisplayLink USB vendor control transfers and provides probe/read helpers for the DRM connector.

Important APIs/types/functions: `udl_read_edid_block()` reads each EDID byte by issuing a USB control message and storing `read_buff[1]`. `udl_probe_edid()` reads the EDID header and treats all-zero data as disconnected. `udl_edid_read()` delegates to `drm_edid_read_custom()`.

Control flow: Connector detect calls `udl_probe_edid()`. Mode enumeration calls `udl_edid_read()`, which repeatedly invokes the block reader. The block reader uses `drm_dev_enter()/exit()` to avoid USB access after unplug.

State and persistence: EDID is read on demand and not cached here.

Dependencies and integration points: Integrates Linux USB control transfers, DRM EDID helpers, and UDL USB-device resolution.

Risks and test signals: Byte-at-a-time control reads are slow and sensitive to disconnects. Risks include short reads, all-zero false disconnect, and USB error handling. Test hotplug, no-monitor, corrupt/short EDID, unplug during EDID read, and multi-block EDID modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_edid.c -->
