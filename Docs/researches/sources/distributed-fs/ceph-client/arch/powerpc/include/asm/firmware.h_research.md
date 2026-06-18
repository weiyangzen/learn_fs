## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/firmware.h

Purpose: defines firmware capability bits, possible/always masks for supported platforms, and firmware feature test/fixup interfaces.

Important APIs/types/functions: `FW_FEATURE_*` bits cover pseries RTAS/PAPR services, LPAR/SPLPAR, OPAL, PS3 LV1, dynamic memory, ultravisor, TCE features, watchdog, PLPKS, and more. It exports `powerpc_firmware_features`, `firmware_has_feature()`, FWNMI entry points, `fwnmi_active`, `ibm_nmi_interlock_token`, firmware fixup section boundaries, and `pseries_probe_fw_features()`.

Control flow: platform probe code populates `powerpc_firmware_features`; `firmware_has_feature()` returns true for always-present features or runtime-detected possible features. Feature-fixup code can patch firmware-dependent sections.

State and persistence: global firmware feature masks and FWNMI state persist after platform initialization. Firmware capabilities drive hypervisor calls, memory hotplug, dump, IOMMU, and interrupt behavior.

Dependencies and integration: depends on asm constants and platform config selections for pseries, PowerNV, PS3, and native hash MMU. Used throughout platform, memory, interrupt, dump, and virtualization code.

Risks and test signals: incorrect possible/always masks can call unavailable firmware services or skip required ones. Test signals include pseries/PowerNV/PS3 boot, RTAS/OPAL feature probing, firmware fixup patching, FWNMI handling, SPLPAR behavior, and dynamic memory features.
