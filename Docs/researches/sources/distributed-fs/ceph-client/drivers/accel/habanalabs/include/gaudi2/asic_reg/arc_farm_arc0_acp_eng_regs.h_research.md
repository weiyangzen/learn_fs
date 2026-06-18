## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_acp_eng_regs.h

### Purpose
`arc_farm_arc0_acp_eng_regs.h` is the generated Gaudi2 register-address map for ARC farm ARC0's ACP engine. It exposes ACP producer/consumer, queue, memory, stream, debug, and event register addresses in the ARC0 ACP engine aperture.

### Important APIs, Types, And Functions
The file defines 272 `mmARC_FARM_ARC0_ACP_ENG_*` constants from `mmARC_FARM_ARC0_ACP_ENG_ACP_PI_REG_0` at `0x4E8F000` through `mmARC_FARM_ARC0_ACP_ENG_ACP_DBG_REG` at `0x4E8F43C`. The families include `ACP_PI_REG_*`, `ACP_CI_REG_*`, queue base/size/control/status registers, DCCM-related queueing, stream/message registers, event and interrupt controls, and debug/status registers.

### Control Flow
There is no executable code. Gaudi2 initialization and security code use the map to identify allowed or protected ACP engine register ranges. Runtime firmware/ARC flows use these registers indirectly for queue handoff and ACP engine control, while the host may access selected registers during setup, diagnostics, or security validation.

### State, Persistence, And Dependencies
The state is ARC0 ACP engine hardware state: queue indices, queue configuration, event latches, and debug/status values. The register map is included via `gaudi2_regs.h`; field-level interpretation depends on matching mask headers and on Gaudi2 security code that clones ARC0 ranges to other ARC instances by instance offsets.

### Integration Points
`gaudi2_regs.h` includes this file, and `gaudi2_security.c` references `mmARC_FARM_ARC0_ACP_ENG_BASE`, the first/last ACP engine registers, and the ACP range when constructing protection rules. ARC CPU IDs from `gaudi2_arc_common_packets.h` identify which ARC instance these registers belong to at the firmware-command level.

### Risks
Address drift can expose or block the wrong ACP engine registers. Security code uses ARC0 as the template for instance-offset calculations, so errors in ARC0 constants can propagate to every ARC farm instance. Queue index/control register mistakes can deadlock ARC-host communication.

### Test Signals
Validate Gaudi2 register-range protection for ACP engine apertures, ARC0 ACP queue setup, producer/consumer index movement, event interrupt delivery, debug/status reads, and instance-offset replication to other ARC farm engines. Firmware boot and scheduler tests should include ACP communication on ARC0.
