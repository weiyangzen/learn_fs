# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bios.h

Purpose: Declares the legacy VBIOS data model and public parser/script APIs consumed by Nouveau display, connector, and encoder code. It defines DCB capacity constants, ROM endian access helpers, BIT entry representation, the parsed `struct nvbios`, and old DCB table accessors.

Important APIs/types: `struct bit_entry`, `struct dcb_table`, `enum nouveau_or`, `enum LVDS_script`, and `struct nvbios`. Public functions include `bit_table()`, `olddcb_table()`, `olddcb_outp()`, `olddcb_outp_foreach()`, `olddcb_conntab()`, `olddcb_conn()`, `nouveau_bios_init()`, `nouveau_bios_takedown()`, `nouveau_run_vbios_init()`, `nouveau_bios_fp_mode()`, `nouveau_bios_embedded_edid()`, `nouveau_bios_parse_lvds_table()`, `run_tmds_table()`, and `call_lvds_script()`.

Control flow/state contract: The header makes `drm->vbios` the persistent carrier for parsed ROM state: ROM bytes, BIOS type/version, mobile flags, PLL defaults, init script pointers, RAM restrict tables, DCB outputs, LVDS/TMDS tables, panel mode pointers, cached EDID, and resume-sensitive LVDS script state. Callers initialize it through `nouveau_bios_init()` before using connector and encoder helpers.

Dependencies/integration: Includes nvkm BIOS and DCB/connector definitions plus DRM display mode declarations via users. `ROM16`, `ROM32`, and `ROMPTR` are central to all legacy ROM parsing. Connector code uses flat-panel/EDID helpers; encoder code uses script runners; debugfs exposes `data` and `length`; display code indirectly depends on DCB entries produced here.

Risks: The structure contains raw ROM offsets and cached pointers, so it assumes the underlying nvkm BIOS data remains stable for the DRM device lifetime. Capacity constants cap parsed DCB arrays at 16 outputs/connectors; unexpected ROMs beyond those limits require careful bounds handling in implementations. Test signals are build coverage, boot-time parser logs, connector enumeration, and suspend/resume script state reset behavior.
