## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_cfg_regs.h

### Purpose
`tpc7_cfg_regs.h` is an auto-generated Gaudi register-address header for the configuration block of TPC engine 7. It gives the driver symbolic `mmTPC7_CFG_*` constants for tensor descriptors, TPC control/status, cache and debug controls, work queues, MMU AXUSER programming, lookup tables, and per-QM special register file windows in the TPC7 CFG aperture.

### Important APIs, Types, And Functions
The file exports only preprocessor constants. It defines 602 `mmTPC7_CFG_*` register addresses from `mmTPC7_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xFC6400` through `mmTPC7_CFG_QM_SRF_31` at `0xFC6E3C`. The largest groups are 272 `KERNEL_TENSOR_*` registers and 272 `QM_SRF_*` registers. Other important groups include `TPC_STALL`, `STATUS`, `TPC_INTR_CAUSE`, `TPC_INTR_MASK`, `ARUSER_*`, `AWUSER_*`, `PROT`, `VFLAGS`, `SFLAGS`, `ROUND_CSR`, `TSB_*`, `WQ_*`, `DBGMEM_*`, `FUNC_MBIST_*`, and `LUT_FUNC*`/`LUT_UPDATE_*`.

### Control Flow
There is no executable control flow in this header. The runtime flow is in users such as `gaudi.c` and `gaudi_security.c`: initialization and teardown code writes selected TPC7 CFG registers, MMU preparation code programs `ARUSER`/`AWUSER`, idle and reset paths read status fields through masks from `gaudi_masks.h`, and security code derives protection-bit masks by grouping addresses around `PROT_BITS_OFFS`.

### State, Persistence, And Dependencies
The state represented here lives in device MMIO registers, not in host memory. Values persist in hardware until reset, power gating, or explicit driver/firmware writes. This header depends on inclusion by aggregate ASIC register headers such as `asic_reg/gaudi_regs.h`, and field interpretation depends on corresponding mask headers and helper macros such as `FIELD_PREP`, `BIT_MASK`, and `GENMASK` used by higher-level headers.

### Integration Points
`gaudi_regs.h` includes this file; `gaudi.c` references TPC7 registers for stop/stall, queue doorbells, MMU ASID setup, and event handling; `gaudi_security.c` uses the register addresses to build protection-bit allow/deny tables. The constants mirror the register layout of other TPC instances, so loops and per-engine code often derive TPC-specific behavior by substituting base addresses or using engine-specific constants.

### Risks
The main risk is hardware ABI drift. A wrong address silently targets the wrong TPC register, which can break dispatch, MMU protection, debug capture, or reset sequencing. Because the file is generated, hand edits are especially risky. Security code that computes masks from address low bits also depends on alignment and address ordering remaining compatible with the protection register layout.

### Test Signals
Useful signals are successful Gaudi probe, TPC7 queue creation and command submission, TPC7 MMU access under multiple ASIDs, idle detection, TPC stall/unstall during reset, interrupt cause/mask handling, and security/protection-table validation that covers the TPC7 CFG register ranges. Register-address regressions usually surface as failed boot, stuck queues, MMU faults, or TPC7-specific event storms.
