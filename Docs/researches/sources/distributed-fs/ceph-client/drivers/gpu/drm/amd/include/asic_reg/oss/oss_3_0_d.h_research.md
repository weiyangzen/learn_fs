# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_d.h

## Purpose

`oss_3_0_d.h` is a generated AMDGPU register-address header for the OSS 3.0 hardware block family. It exports symbolic MMIO and indexed-register offsets for interrupt handling, semaphore/virtualization, SRBM, security/key or client registers, SDMA engines and contexts, and HDP/XDP host-data-path registers. It contains no executable code; it gives driver code stable names for hardware addresses.

The include guard is `OSS_3_0_D_H`. Macro prefixes distinguish address spaces:

- `mm*` names are memory-mapped register offsets used by normal MMIO register access helpers.
- `ix*` names are indexed-register offsets, notably for a client/key/session/security-style register block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or mutable variables. The API is a flat set of `#define`s mapping symbolic register names to numeric offsets.

Major address groups include:

- `mmIH_*`: IH VMID LUTs, ring buffer control/base/read/write pointers, writeback pointer address registers, interrupt control/status, perf counters, debug, DSM matching, doorbell read pointer, VF/virtual reset status, and level/incomplete-interrupt controls.
- `mmSEM_*`, `mmSDMA_CONFIG`, `mmSDMA1_CONFIG`, `mmUVD_CONFIG`, `mmVCE_CONFIG`, and `mmCP_CONFIG`: semaphore and client-configuration registers around the `0xf90` range.
- `mmSRBM_*`, `mmSYS_GRBM_*`, and `mmCC_*`: SRBM control/status/reset/debug/read-error/firewall/interrupt/perf/CAM/domain/virtualization and backend-disable/redundancy registers.
- `ixDH_TEST`, `ixKHFS*`, `ixKSESSION*`, `ixKSIG*`, `ixEXP*`, `ixLX*`, `ixCLIENT0` through `ixCLIENT4`, `ixKEFUSE*`, `ixHFS_SEED*`, `ixRINGOSC_MASK`, and `ixSPU_PORT_STATUS`: indexed-register space entries for key/session/client-related hardware state.
- `mmSDMA0_*` and `mmSDMA1_*`: public SDMA engine registers, perf counters, debug/freeze/phase/power/VM/atomic registers, and repeated GFX/RLC0/RLC1 ring-buffer, IB, doorbell, watermark, context, and mid-command address ranges.
- `mmHDP_*` and `mmHDP_XDP_*`: host-data-path cache, nonsurface, tiling, memory IO, VF, direct-to-HDP, P2P mailbox/BAR, XDP configuration, busy/sticky/debug, and high BAR address registers.

Notable offset patterns:

- IH registers occupy `0xe00` through `0xe4b`.
- SEM/client configuration appears around `0xf90` through `0xf9f`.
- Core SRBM registers appear around `0x390` through `0x3b9`, with perf registers at `0x7c00` and domain/virtualization windows at `0xfa00` and above.
- SDMA0 public/context ranges begin around `0x3400`; SDMA1 begins around `0x3600`. RLC0/RLC1 context ranges are offset blocks for each engine.
- HDP appears around `0xb00`/`0xbc9` and XDP-related HDP registers around `0xc00` through `0xc44`.

## Control Flow And Data Flow

This header has no direct control flow. It participates in driver control flow as address data:

1. Driver code selects a symbolic register offset, for example `mmIH_RB_CNTL`, `mmSRBM_STATUS`, `mmSDMA0_GFX_RB_WPTR`, or `mmHDP_XDP_D2H_FLUSH`.
2. It combines the offset with an MMIO access helper and, when needed, field macros from a matching `*_sh_mask.h` header.
3. It reads or writes the GPU register.
4. Higher-level control flow waits on status bits, writes reset bits, posts doorbells, updates read/write pointers, configures VM context, or flushes host data paths.

The file's layout mirrors hardware initialization and service paths: IH addresses support interrupt-ring initialization and servicing; SRBM addresses support global block selection/status/reset; SDMA addresses support microcode, rings, IBs, doorbells, VM, and context switching; HDP/XDP addresses support CPU/host-visible memory coherency and P2P/BAR operations.

## State And Persistence Behavior

The header stores no software state. Each constant identifies a hardware register whose value persists in the device across ordinary driver reads/writes until changed by driver code, firmware, reset, power transitions, or hardware activity.

Stateful hardware represented by these addresses includes:

- Interrupt state: IH ring pointers, overflow/status, interrupt masks and incomplete-interrupt counters.
- Global routing and reset state: SRBM graphics selection, busy status, soft reset, read/firewall error latches, and domain address mappings.
- Security/client indexed state: key/session/client/fuse/seed-like indexed registers exposed through `ix*` constants.
- DMA state: SDMA engine control, queue rings, IB pointers, doorbells, VM context, atomics, context status, preemption, and perf counters.
- Host data path state: HDP cache/nonsurface metadata, memory IO transaction status, VF enablement, XDP flush/bar/P2P mappings, busy/sticky/debug flags, and high BAR address bits.

Because the constants are part of the driver-to-hardware ABI, the persistent behavior is in the hardware side effects of reads and writes performed by consumers.

## Dependencies And Integration Points

This header has no include dependencies beyond the C preprocessor. It is designed to be included by AMDGPU ASIC code together with compatible field-layout headers, such as `oss_3_0_sh_mask.h` or related OSS 3.0.x mask headers.

Integration points include:

- Register access helpers that expect `mm*` offsets.
- Indexed-register access helpers for `ix*` offsets.
- AMDGPU interrupt handler code for IH register setup and servicing.
- SRBM helpers for block idleness, read-error/firewall reporting, domain address setup, graphics selection, virtualization, and reset.
- SDMA initialization and ring-management code for SDMA0/SDMA1 public and context registers.
- HDP/XDP cache flush, memory IO, P2P, BAR, and VF handling paths.
- Generated-register build or sync processes that keep `*_d.h` address headers aligned with `*_sh_mask.h` field headers.

## Risks And Edge Cases

- Address constants must match the exact ASIC generation. A wrong address can corrupt unrelated device state even when the field masks are correct.
- SDMA0/SDMA1 and GFX/RLC0/RLC1 address blocks are highly repetitive but offset differently. Incorrectly substituting one block for another can route commands to the wrong engine or queue.
- The `ix*` indexed-register macros are in a different access space than `mm*` macros. Using the wrong accessor class can fail silently or access unintended hardware.
- Register offsets alone do not encode access semantics. Some registers are read-only, write-only, write-one-to-clear, latch-on-read, or require ordering/delay rules defined outside this file.
- The header is OSS 3.0 while the paired work item also includes an OSS 3.0.1 mask file. Consumers must verify that the address generation and mask generation are compatible for the target ASIC.
- HDP/XDP and SRBM virtualization registers affect host-visible memory routing and VF state. Mistakes can create coherency, isolation, or reset issues.

## Test Signals

Useful validation signals are mostly compile-time and hardware-integration tests:

- AMDGPU builds for ASICs using OSS 3.0 address headers, catching missing or renamed macros.
- Register-database diffing against the canonical AMD-generated source for OSS 3.0.
- Probe and boot on matching hardware with successful IH setup, no spurious interrupts, and correct SRBM status polling.
- SDMA0 and SDMA1 ring tests that exercise GFX, RLC0, and RLC1 contexts, doorbells, IB submission, VM context setup, and preemption.
- GPU reset, suspend/resume, and power-management tests that touch SRBM, SDMA, and HDP state.
- HDP cache flush/memory coherency tests, especially around CPU-visible buffers and P2P/BAR paths.
- SR-IOV/VF tests that validate VF enable/reset/status and memory IO routing when virtualization is enabled.
