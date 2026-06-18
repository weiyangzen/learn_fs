# sources/distributed-fs/ceph-client/drivers/virt/Kconfig

Purpose: top-level Kconfig menu for virtualization support drivers. It groups VM-oriented device drivers and sources submenus for vboxguest, Nitro Enclaves, ACRN, and confidential-computing support.

Important APIs, types, and functions: config symbols include `VIRT_DRIVERS`, `VMGENID`, and `FSL_HV_MANAGER`; it sources `drivers/virt/vboxguest/Kconfig`, `drivers/virt/nitro_enclaves/Kconfig`, `drivers/virt/acrn/Kconfig`, and `drivers/virt/coco/Kconfig`.

Control flow: `VIRT_DRIVERS` gates most nested virtualization drivers. `VMGENID` defaults to yes and supports RNG reseeding after VM cloning. `FSL_HV_MANAGER` depends on `FSL_SOC` and selects `EPAPR_PARAVIRT`.

State and persistence: build configuration state only.

Dependencies and integration points: consumed by `drivers/virt/Makefile` and architecture/platform virtualization driver builds. `coco` is sourced outside the `VIRT_DRIVERS` conditional.

Risks: disabling `VIRT_DRIVERS` skips most virtual environment drivers but not the `coco` submenu. Defaults such as `VMGENID=y` affect built-in footprint.

Test signals: menuconfig visibility, dependency resolution, and object inclusion for VMGENID, Freescale HV, Nitro, ACRN, vboxguest, and coco configurations.
