## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.h

Purpose: central encoder driver header defining SoC pdata, per-context state, per-device state, inline helpers, and logging macros.

Important APIs/types/functions: `struct mtk_vcodec_enc_pdata` carries SoC capabilities including extended firmware messaging and 34-bit IOVA. `enum mtk_encode_param` flags dynamic control changes. `struct mtk_enc_params` holds user-visible encoder settings. `struct mtk_vcodec_enc_ctx` represents one V4L2 file/m2m instance. `struct mtk_vcodec_enc_dev` represents the platform encoder device. Inline helpers map file/control objects to contexts and wake interrupt waitqueues.

Control flow: this header shapes how open creates a context, how queue code stores parameters, how codec backends find device registers/firmware, and how IRQ handlers wake backends waiting in `mtk_vcodec_wait_for_done_ctx`.

State and persistence behavior: context state persists for an open file and includes queue data, backend vtable/handle, interrupt condition arrays, controls, work item, flush state, colorspace metadata, queue mutex, and VPU instance pointer. Device state persists for the platform device and includes V4L2/m2m handles, resource mappings, context list, current context, locks, IRQ, PM, capabilities, and debugfs.

Dependencies and integration points: includes common MediaTek vcodec driver, debugfs, firmware, and utility headers. It is included by nearly every encoder source file and defines the internal state contract.

Risks: broad shared state increases coupling between frontend, platform driver, VPU transport, and codec backends. `curr_ctx` plus waitqueue arrays must be indexed consistently by hardware ID. Pdata macros hide SoC behavior in backend code, so adding new SoC quirks requires careful propagation.

Test signals: compile coverage across all encoder files after state layout changes; multi-instance open/close stress; IRQ wait/wake tests; dynamic parameter tests confirming `param_change` flags map to backend commands.
