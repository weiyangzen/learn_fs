# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.c

Purpose: Common Qualcomm CAMSS CSID core: owns format tables, V4L2 subdevice operations, power/clock/reset sequencing, media-link setup, test-pattern control, resource initialization, and entity registration. Generation-specific files plug in through `struct csid_hw_ops`.

Important APIs/types/functions: Exports `csid_formats_4_1`, `csid_formats_4_7`, `csid_formats_gen2`, `csid_find_code()`, `csid_get_fmt_entry()`, `csid_hw_version()`, `csid_src_pad_code()`, `msm_csid_subdev_init()`, `msm_csid_register_entity()`, `msm_csid_unregister_entity()`, `msm_csid_get_csid_id()`, and `csid_is_lite()`. Internal key functions include `csid_set_clock_rates()`, `csid_set_power()`, `csid_set_stream()`, pad format ops, `csid_set_test_pattern()`, and `csid_link_setup()`.

Control flow/state: Init binds resources, maps MMIO or VFE-embedded CSID offsets, requests IRQ with `IRQF_NO_AUTOEN`, builds clock/regulator arrays, initializes completion, and calls hardware `subdev_init()`. Registration creates the CSID subdev with one sink and four source pads, optional test-pattern menu, default UYVY 1920x1080 formats, and media ops. Link setup captures CSIPHY id/lane count/lane assignment on sink links, prevents conflicting testgen/sensor use, tracks enabled source pads as `phy.en_vc`, and marks VC update needed. Power-on gets the parent VFE/IFE, runtime-resumes, enables regulators/clocks, enables IRQ, resets hardware, and reads version. Stream-on syncs controls, requires a sink link unless using testgen, and calls hardware `configure_stream()` only when VC state changed.

Dependencies/integration: Integrates V4L2 subdev, media controller, PM runtime, regulators, clocks, CAMSS parent device ops, CSIPHY lane config, VFE buffer/update callbacks, MIPI CSI-2 data types, and all generation-specific ops.

Risks/test signals: `csid_set_power()` has multiple error exits where parent-device reference unwinding is sensitive. `csid_set_stream()` configures only when `need_vc_update` is true, so format/control changes must correctly set that state elsewhere. Format defaults and packed RAW10 source-code selection affect downstream VFE. Test link setup conflicts, multi-source-pad VC masks, testgen exclusive mode, power failure unwind, clock-rate selection from link frequency, VFE-embedded CSID mapping on CAMSS_8250, and subdev format propagation.
