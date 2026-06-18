<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.c

Purpose: utility for packing raw HDMI infoframe bytes into the register layout used by Nouveau SOR HDMI callbacks.

Important APIs and functions: `pack_hdmi_infoframe()` fills `struct packed_hdmi_infoframe` fields: `header`, `subpack0_low`, `subpack0_high`, `subpack1_low`, and `subpack1_high`. It accepts a raw byte buffer and a length.

Control flow: a fallthrough switch copies bytes 0 through up to 16 into little-endian-style 32-bit register words. Inputs longer than 17 bytes are intentionally truncated to 17 bytes; length 0 leaves all packed fields zero. The fallthrough implementation lets one switch handle every short length without loops.

State and persistence: no persistent state. The packed result is consumed immediately by generation HDMI callbacks in G84, GT215, GF119, GK104, GV100, and descendants.

Dependencies and integration points: includes `hdmi.h`; callers write packed fields to hardware infoframe registers and handle enable/disable bits.

Risks: assumes no valid frame needed by these hardware paths exceeds 17 octets including header. The function does not validate `raw_frame` for nonzero length; callers must pass a valid buffer. Byte ordering must match hardware register expectations.

Test signals: compare packed output for known AVI/VSI infoframes, check len 0 through 17, check truncation for longer frames, and verify HDMI infoframes on a sink analyzer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.c -->
