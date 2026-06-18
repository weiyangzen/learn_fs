<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-reg.h

Purpose: constants for SAA7164 firmware result codes, command IDs, MMIO registers, bootloader flags, descriptor subtypes, format IDs, firmware controls, state transitions, tuner/video/audio controls, and encoder controls.

Important APIs, types, and functions: this header defines no functions. Key groups are `SAA_OK`/`SAA_ERR_*`, `PVC_*` command/response flags, `SAA_DEVICE_*` firmware registers and boot flags, descriptor subtype constants such as `PVC_HARDWARE_DESCRIPTOR`, format constants such as `VS_FORMAT_MPEG2TS` and `VS_FORMAT_VBI`, DMA states `SAA_DMASTATE_*`, and control selectors such as `PU_BRIGHTNESS_CONTROL` and `EU_VIDEO_BIT_RATE_CONTROL`.

Control flow: included by `saa7164.h` and consumed by firmware, API, command, core, encoder, DVB, and VBI code to encode firmware messages and interpret MMIO status.

State and persistence: no state. The values define the ABI between driver and firmware and therefore must remain stable for supported firmware images.

Dependencies and integration points: firmware command bus, descriptor parsing, encoder/VBI/DVB port transitions, firmware loader, and user-control mapping.

Risks: values are magic ABI constants with little type safety. Duplicate `SET_DEBUG_LEVEL_CONTROL` and `GET_DEBUG_DATA_CONTROL` definitions appear in the file. Any value drift breaks hardware communication in ways that may only appear at runtime.

Test signals: successful firmware download, descriptor parsing, port state transitions, control changes, VBI format negotiation, and command responses without PVC error flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-reg.h -->
