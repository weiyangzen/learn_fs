# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.c

Purpose: owns MDP4 KMS platform setup, hardware initialization, modeset object construction, power/clock control, VM setup, and platform driver registration.

Important APIs and functions: `mdp4_probe()` maps registers, gets IRQ/regulator/clocks, and invokes `msm_drv_probe()`. `mdp4_kms_init()` initializes `mdp_kms`, validates hardware revision, enables runtime PM, disables bootloader-left outputs, initializes VM and modeset objects, and allocates/pins a blank cursor BO. `modeset_init()` creates planes, CRTCs, and LVDS/DSI/TMDS interfaces. `mdp4_hw_init()` programs fetch, portmap, layer mixer, and default CSC/operation registers. `mdp4_enable()` and `mdp4_disable()` gate core/interface/LUT/AXI clocks.

Control flow: probe collects platform resources, then DRM component init calls KMS init. KMS init programs clocks and revision checks before object creation. Commit hooks enable/disable clocks and wait for per-CRTC flush completion.

State and persistence: `struct mdp4_kms` stores device, revision, mmio, clocks, regulator, IRQ handler, runtime PM flag, and blank cursor BO/iova. No disk persistence.

Dependencies and integration: integrates DRM bridges/connectors for LVDS, HDMI, and DSI; MSM GEM/VM; runtime PM; clock/regulator frameworks; and MDP shared KMS ops.

Risks: limited fixed topology: two CRTCs and fixed RGB/VG plane assumptions. Some optional clock/regulator handling relies on bootloader/platform behavior. Failure paths call `mdp4_destroy()` if `kms` exists, so partially initialized resources must tolerate cleanup.

Test signals: probe/remove, revision mismatch, modeset init per interface, blank cursor allocation, suspend/resume, and bootloader-enabled-output cleanup.
