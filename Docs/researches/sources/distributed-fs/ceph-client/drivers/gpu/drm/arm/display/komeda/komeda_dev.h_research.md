# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.h

Purpose: defines the generic Komeda hardware-device contract, event model, chip callbacks, display modes, and `struct komeda_dev`.

Important APIs/types/functions: event and error bit definitions classify VSYNC/FLIP/URUN/IBSY/OVR/EOW and hardware errors. `struct komeda_dev_funcs` is the chip backend vtable for format init, resource enumeration, cleanup, IOMMU, IRQ, vblank, register dump, opmode, and flush. `struct komeda_dev` stores device resources, chip info, format table, clocks, pipelines, IOMMU, debugfs, and error verbosity. Display modes describe inactive, display0, display1, and dual display.

Control flow: core code calls chip funcs during probe, PM, IRQ, vblank, atomic flush, and opmode transitions. Events flow from chip IRQ handler into KMS CRTC handling and event printing.

State and persistence: `komeda_dev` persists for platform-device lifetime. `dpmode` is mutable runtime state protected by `lock`. `err_verbosity` persists via debugfs until driver removal.

Dependencies/integration: includes Linux device/clock, `komeda_pipeline.h`, product IDs, and format caps. Used by nearly every Komeda source file.

Risks: callback contract is broad; missing chip funcs cause null dereferences if core assumes presence. Event bit allocation must match printer and CRTC handling. Test signals: callback coverage in chip backends, IRQ event classification, debugfs `err_verbosity`, dual-display opmode transitions, and static analysis for NULL func usage.
