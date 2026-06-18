# sources/distributed-fs/ceph-client/include/sound/q6usboffload.h

Source read summary: 20 lines, Qualcomm QDSP6 USB offload parameters.

Purpose: defines the data passed for Qualcomm USB backend DAI link offload through QDSP6 audio paths.

Important APIs, types, and functions: `struct q6usb_offload` stores the USB backend device, allocated IOMMU domain, USB interrupter number, and stream ID (`sid`) for IOMMU transactions.

Control flow: Qualcomm audio machine/backend code fills this structure when configuring USB audio offload so DSP/audio code can address the USB device, interrupt, and IOMMU context.

State and persistence behavior: the structure is runtime configuration for an offload path; IOMMU domain lifetime is managed elsewhere and no state is persisted here.

Dependencies and integration points: integrates USB audio, Qualcomm QDSP6 ASoC backend, and IOMMU mapping.

Risks and edge cases: stale device/domain pointers, wrong interrupter number, or SID mismatch can break DMA isolation or offload interrupts.

Test signals: USB offload setup/teardown, IOMMU domain mapping, interrupter routing, multiple USB stream IDs, and disconnect during offload.
