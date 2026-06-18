# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.h

Purpose: declares the UIF entity structure and public functions.

Important APIs/types: defines `UIF_PAD_SINK`, `UIF_PAD_SOURCE`, `struct vsp1_uif` with embedded `vsp1_entity` and `m3w_quirk`, `to_uif()`, `vsp1_uif_create()`, and `vsp1_uif_get_crc()`.

Control flow/state: `m3w_quirk` is set at creation based on SoC matching and affects stream configuration. CRC access is direct register read.

Dependencies/integration: included by UIF implementation and device setup code; depends on `vsp1_entity.h`.

Risks and test signals: callers need a valid subdevice and powered hardware for CRC reads. Compile and runtime-test with UIF-enabled SoCs and verify crop/CRC behavior.
