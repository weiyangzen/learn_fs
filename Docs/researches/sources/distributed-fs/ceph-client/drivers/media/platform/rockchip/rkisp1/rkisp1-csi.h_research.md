# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.h

Purpose: internal header for the RKISP1 CSI-2 receiver module.

Important APIs/types/functions: forward-declares CSI/device/sensor async structs and declares `rkisp1_csi_init()`, `rkisp1_csi_cleanup()`, `rkisp1_csi_register()`, `rkisp1_csi_unregister()`, and `rkisp1_csi_link_sensor()`.

Control flow: `rkisp1-dev.c` calls init/cleanup around PHY lifetime, register/unregister around media entity lifetime, and `rkisp1_csi_link_sensor()` from async notifier binding for port 0 sensors.

State and persistence: no state in the header; state is in `struct rkisp1_csi`.

Dependencies/integration: connects platform glue to `rkisp1-csi.c`.

Risks: CSI functionality is compiled into the module but should only be initialized/registered when match-data feature flags advertise MIPI CSI2.

Test signals: compile/link for MIPI-capable and non-MIPI variants, probe cleanup after CSI init failures, and sensor binding through port 0.
