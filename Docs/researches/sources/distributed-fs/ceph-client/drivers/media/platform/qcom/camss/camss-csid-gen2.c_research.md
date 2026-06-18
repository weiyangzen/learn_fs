# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.c

Purpose: Implements generic Gen2 CSID operations, including RX/RDI configuration, test pattern generation, IRQ handling, and reset for blocks with lite/full register-layout differences.

Important APIs/types/functions: Exports `csid_ops_gen2`. Helpers configure RX, RDI halt/resume, TPG registers, RDI stream registers, test pattern mode, ISR, and reset. It uses `csid_is_lite()` to choose register offsets.

Control flow/state: Streaming loops over `csid->phy.en_vc`. For each VC it optionally configures TPG, configures RDI payload-only decode with data type/VC/DT_ID, timestamp/measure/byte-counter flags, frame/IRQ/pixel/line drop periods, then configures RX and resumes or halts RDI. Reset clears/masks top reset IRQ, strobes reset while preserving registers, and waits for reset completion. ISR clears top, CSI2 RX, and enabled RDI statuses, then clears IRQ command and completes reset when seen.

Dependencies/integration: Common CSID core supplies format/control/link state and power sequencing; Gen2 constants come from `camss-csid-gen2.h`.

Risks/test signals: Risks are offset divergence for lite blocks, defaulting lane count to four when unset, and testgen configuration matching enabled virtual channels. Test lite/full SoCs, multi-VC masks, TPG modes, reset timeout, and CSI error IRQ clearing.
