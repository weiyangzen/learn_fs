# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.c

Purpose: provides common media-entity helpers for DCMIPP subdevices. It centralizes pad allocation, standard subdevice initialization/registration, link validation wiring, and subdevice cleanup.

Important APIs: `dcmipp_pads_init` allocates and initializes an array of `media_pad` entries from caller-supplied flags. `dcmipp_ent_sd_register` initializes a `dcmipp_ent_device` plus `v4l2_subdev`, assigns entity function/ops/name/owner/internal ops/subdev ops, exposes a devnode, initializes media pads, finalizes subdev state, registers the subdev, and stores optional IRQ callbacks. `dcmipp_ent_sd_unregister` cleans the entity and unregisters the subdevice. `dcmipp_entity_ops` uses `v4l2_subdev_link_validate`.

Control flow: DCMIPP input and byteproc entities call `dcmipp_ent_sd_register` during core topology creation. On failures, pads and media entity state are unwound. Release paths call `dcmipp_ent_sd_unregister` and rely on subdev internal release callbacks for private allocation cleanup.

State and persistence: state is allocated kernel memory for pads and subdevice/media entity registrations. No disk persistence exists. The helper stores IRQ handler pointers in the shared `dcmipp_ent_device`, later consumed by `dcmipp-core.c` IRQ fan-out.

Dependencies and risks: depends on media controller, V4L2 subdev registration, and the shared `dcmipp_ent_device` contract in `dcmipp-common.h`. Risks include cleanup ordering (`media_entity_cleanup` before/after subdev unregister), pad leaks if caller release paths miss `dcmipp_pads_cleanup`, and all subdevices using the same generic link validator even when entity-specific validation might be needed. Test signals are probe failure injection at pad init/entity init/finalize/register, remove/unbind leak checks, media graph validation, and IRQ callback registration visibility in core.
