<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec_tpmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec_tpmi.c

Purpose: auxiliary driver bound to `intel_vsec.tpmi` that enumerates TPMI PM Feature Structure entries and creates one auxiliary device per supported TPMI feature, such as RAPL, PEM, uncore, SST, and PLR. It also exposes TPMI control/status helpers and gated debugfs dumps.

Important APIs/types/functions: `struct intel_tpmi_pfs_entry` models hardware PFS entries; `struct intel_tpmi_pm_feature` stores one feature header and MMIO offset; `struct intel_tpmi_info` stores feature array, OOBMSM platform info, control MMIO, and debugfs directory. Exported APIs include `tpmi_get_platform_data()`, `tpmi_get_resource_count()`, `tpmi_get_resource_at_index()`, `tpmi_get_feature_status()`, `tpmi_register_notifier()`, `tpmi_unregister_notifier()`, and `tpmi_get_debugfs_dir()`. `tpmi_create_device()` constructs feature resources and calls `intel_vsec_add_aux()`.

Control flow: probe allocates `intel_tpmi_info`, reads each PFS header from resources provided by `vsec.c`, derives feature offsets from the PFS start plus capability offset in 1 KiB units, processes `TPMI_INFO_ID` to populate package/bus/device/function/partition/cdie mapping, maps the control feature when present, optionally creates debugfs, and creates feature auxiliary devices for enabled, named TPMI IDs. Feature status commands serialize through `tpmi_dev_lock`, negotiate TPMI control ownership, issue GET_STATE, wait for run-busy clear, copy response, and signal completion.

State/persistence: mapping and feature metadata live in devm-managed probe state. Hardware feature state is queried on demand through the TPMI control interface. Debugfs `mem_write` can mutate TPMI MMIO state and is exposed only when lockdown allows devmem and caller has `CAP_SYS_RAWIO`.

Dependencies/integration: depends on Intel VSEC aux devices, PCI parent data, MMIO/ioremap, debugfs, Linux security lockdown, capabilities, notifier chains, and Intel TPMI public headers. Downstream feature drivers bind to names like `intel_vsec.tpmi-uncore`.

Risks: PFS data is trusted hardware input but entry size is capped to 1 KiB for debug paths. `tpmi_get_feature_status()` assumes parent/driver data topology created by this driver. Control ownership timeouts or missing control memory cause feature-status failures. Debugfs write access is intentionally powerful and must remain gated.

Test signals: a TPMI VSEC device should produce per-feature auxiliary devices only for enabled supported TPMI IDs; `tpmi_get_resource_count()` and resource lookup should match PFS `num_entries`; feature-status reads should reflect read/write blocked bits; debugfs should appear only with raw IO permission and no devmem lockdown; remove should call TPMI core exit notifier and remove debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec_tpmi.c -->
