# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_common.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_common.h

### Purpose
`otx2_cpt_common.h` centralizes OcteonTX2/CN10K CPT shared constants, AF/RVU addressing helpers, capability flags, PF/VF mailbox message structures, engine capability formats, device-generation predicates, feature gates, and common mailbox function declarations.

### Important APIs, Types, And Functions
Important constants include max VF count, RVU function address macro, invalid group, DMA alignment, CN10K capability bit indices, engine types, and private mailbox message IDs. It defines inline `otx2_cpt_write64()` / `otx2_cpt_read64()`, generation predicates (`is_dev_otx2()`, `is_dev_cn10ka()`, `is_dev_cn10ka_ax()`, `is_dev_cn10kb()`, `is_dev_cn10ka_b0()`), `otx2_cpt_set_hw_caps()`, errata and SGV2 feature gates, mailbox request/response structs for inline IPsec LF config, engine group lookup, kernel VF limits, and capabilities, plus declarations for AF register and LF resource mailbox helpers.

### Control Flow, State, And Persistence
The header has mostly inline logic. Runtime code uses the device predicates at probe to set capability bits and choose CN10K mailbox/LMTST behavior, errata workarounds, and SG format. Read/write helpers compute RVU block/slot offsets over a mapped register base. Mailbox structs persist request payload layouts exchanged between PF, VF, and AF.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on PCI, crypto, devlink, OcteonTX2 hardware types, `rvu.h`, and `mbox.h` from the AF networking driver. Risks include subsystem/revision checks going stale, capability bits being inverted for non-OTX2 devices, private mailbox IDs colliding with AF range assumptions, and register offset macro misuse. Test signals include PF/VF probes across OTX2/CN10KA/CN10KB, capability replies, kernel VF limit mailbox, SGV2 feature selection, errata 38550 path, AF register read/write helpers, and include-path build coverage.
