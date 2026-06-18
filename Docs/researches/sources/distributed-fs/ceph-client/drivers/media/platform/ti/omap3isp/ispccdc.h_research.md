# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccdc.h


Purpose: Declares the CCDC submodule interface and state structures for the OMAP3 ISP driver.

Important APIs/types: `enum ccdc_input_entity` identifies none, parallel, CSI2A, CCP2B, and CSI2C inputs. Output bitmasks select memory, preview, or resizer. LSC structs model state (`STOPPED`, `STOPPING`, `RUNNING`, `RECONFIG`), requested configs, coherent table storage, active/request/free queues, and deferred freeing work. Stop/event macros encode the CCDC/LSC stopping state machine. Pad constants define sink, output formatter source, and video-port source pads. `struct isp_ccdc_device` contains the V4L2 subdev, pads, formats, crop, input/output routing, video node, image controls, LSC/FPC resources, update flags, BT.656/field/underrun/streaming state, locks, wait queue, and ioctl mutex. Prototypes expose init/cleanup, entity registration, busy/ISR, context restore, and max-rate calculation.

Control flow: `isp.c` includes this header to embed `struct isp_ccdc_device`, initialize/register the module, dispatch interrupts, restore context, and ask rate limits. Other modules use pad/output constants when creating media links.

State and persistence: Declares in-memory state only. Coherent DMA table lifetime is managed by `ispccdc.c`.

Dependencies/integration: Includes public OMAP3 ISP ABI (`linux/omap3isp.h`), workqueues, and `ispvideo.h`. It forward-declares `struct isp_device` to avoid a full core dependency for function prototypes.

Risks and test signals: Stop/event bit encodings are consumed by interrupt code and wait conditions; changes require careful state-machine tests. The struct is central to both IRQ and userspace ioctl paths, so field ordering is internal but semantic grouping matters. Build and stream tests should cover all declared inputs/outputs and cleanup paths.
