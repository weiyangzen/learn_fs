# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h lines 21031-22477

## Scope And Purpose

This chunk is the closing 1,447-line segment of AMD's generated `soc21_enum.h` hardware enum header. It exports numeric selector values for SOC21 GPU blocks: the tail of `PH_PERFCNT_SEL`, complete `PhSPIstatusMode`, `RMIPerfSel`, `GCRPerfSel`, `UTCL1PerfSel`, interrupt-handler enums, `SEM_PERF_SEL`, `LSDMA_PERF_SEL`, the ROM signature constant, and `EFC_SURFACE_PIXEL_FORMAT`. The path sits below the mirrored `ceph-client` tree, but the content is AMDGPU hardware metadata, not Ceph filesystem code.

The definitions are compile-time ABI between AMDGPU/KFD code and SOC21 hardware register fields. They identify perf-counter mux inputs, interrupt-ring/interface encoding, semaphore and LSDMA monitor events, ROM image signature value, and video/compositor surface pixel formats. This chunk defines no functions, structs, variables, locks, allocations, sysfs nodes, or direct MMIO accesses.

The chunk starts mid-enum at `PH_PERF_SEL_SC5_PA3_DATA_FIFO_WE`, so the beginning of `PH_PERFCNT_SEL` is in the previous chunk. It ends at the `#endif /*_soc21_ENUM_HEADER*/` guard close.

## Important APIs, Types, And Constants

The exported API is the set of enum type names and enumerators consumed by SOC21 AMDGPU code or by shared generated register-programming paths:

- `PH_PERFCNT_SEL`: performance-counter selector values for the primitive/parameter handling path. This chunk covers SC5 PA3-PA7 FIFO events, full SC6 and SC7 selector groups, aggregate SC arbiter starvation/stall selectors, and per-SC FIFO status selectors through `PH_PERF_SC7_FIFO_STATUS_3 = 0x3ff`. The visible events cover data FIFO reads/writes, empty/full flags, null/event/FPOV/LPOV/EOP/EOPG writes, dealloc reads, screen/arbiter busy states, credit states, graphics pipe transitions, and FIFO status lanes.
- `PhSPIstatusMode`: selects PH/SPI status reporting mode: largest PA/PH FIFO count, arbiter-selected PA/PH FIFO count, or disabled.
- `RMIPerfSel`: two RMI performance events for RB-to-RMI write requests and read requests across all client IDs.
- `GCRPerfSel`: graphics cache request performance selectors. It enumerates request classes for SDMA0, SDMA1, CPC, CPG, CPF, RLC, PM, and PIO; each group separates GL2/GL1 range requests, less-than-16K, 16K, greater-than-16K, all-request, metadata, SQC data, SQC instruction, TCP, and TCP TLB-shootdown traffic. It also includes virtual/physical request selectors, heavy/light TLB shootdown, all requests, outstanding request clocks, UTCL2 request/return/inflight/credit/filter signals.
- `UTCL1PerfSel`: UTCL1 TLB/cache performance selectors for request, hit, miss, miss-handler behavior, UTCL2 requests/returns, XNACK retry, fault and permanent/PRT fault returns, credit or miss-handler stalls, outstanding request accumulation, bypass requests, invalidation filter hits, CP invalidation requests, UTCL2-to-UTCL1 invalidations, range invalidations, and all-VMID invalidations.
- `IH_CLIENT_TYPE`, `IH_INTERFACE_TYPE`, `IH_RING_ID`, and `IH_VF_RB_SELECT`: compact interrupt-handler encoding enums. They distinguish GFX/MM/multi-VMID clients, legacy versus register-write interfaces, interrupt/request/translation rings, and VF ring-buffer selection by client function ID, IH function ID, or PF.
- `IH_PERF_SEL`: large interrupt-handler performance selector enum. It covers cycle/idle/input/buffer-idle state, RB0/RB1/RB2 full/overflow/writeback/wrap/load-RPTR events, MC write activity and stalls, BIF line edge events, client credit/cookie/storm/drop/self-IV/buffer FIFO signals, 32 client interrupt inputs, and virtualization-specific per-VF variants for VF0-VF15 on ring-buffer fullness, overflow, write-pointer writeback/wrap, read-pointer wrap, BIF line edges, full-drain drops, and load-RPTR operations.
- `SEM_PERF_SEL`: semaphore performance selectors for cycle/idle, request-signal and request-wait events from SDMA0-3, UVD/UVD1, VCE0/VCE1, ACP, ISP, VP8, CPG engines, CPC immediate engines, CPC offline engines 0-31 for CPC1/CPC2, poll waits for those offline engines, MC read/write request/return events, and ATC request/return/XNACK/invalidation/VM-invalidation events.
- `LSDMA_PERF_SEL`: local SDMA performance selectors for ring-buffer state, command queue state, indirect-buffer queue state, execution idleness, SRBM register sends, memory-controller request/return activity, semaphore and interrupt request/response states, packet count, copy-engine idleness/stalls/FIFO fullness, GFX/RLC/page selection, context changes, doorbell, bus-address routing, L1/ATCL2 invalidation/XNACK paths, MMHUB requests/returns for CE/F32/atomic/RB/IB/WPTR, UTCL1/UTCL2 traffic, command operation match/start/end, CE busy transitions, perf-counter trigger transitions, DRAM ECC, and NACK generation errors.
- `ROM_SIGNATURE`: `0x0000aa55`, the standard BIOS/option-ROM signature value expected in ROM image headers.
- `EFC_SURFACE_PIXEL_FORMAT`: UVD EFC surface-format IDs for RGB/BGR/ARGB/RGBA formats, YCrCb/YCbCr ordering variants, 10-bit and 12-bit MSB/LSB packed or planar formats, 16:16:16:16 float/unorm/snorm variants, 4:2:0 planar and 4:2:2 packed YUV formats, RGB111110/BGR101111 fixed and float formats, and mono 8/10/12/16-bit formats.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime behavior appears only when other driver code writes these numeric values into SOC21 register fields or compares hardware-provided values against them.

The typical flow is:

1. A SOC21-specific driver path includes `soc21_enum.h` directly or indirectly alongside generated register address and bitfield headers.
2. A perf-counter, interrupt, semaphore, DMA, ROM, or media setup path chooses one of these enum constants.
3. The value is packed into the appropriate selector or control field using generated register masks/shifts and written with AMDGPU register access helpers.
4. Hardware interprets the selector and routes the matching internal event, ring selection, status mode, signature comparison, or pixel-format behavior.

Concrete local integration is visible through direct include/use patterns around SOC21 KFD interrupt and queue code. `amdkfd/kfd_device_queue_manager_v11.c` includes `soc21_enum.h`, and SOC21 interrupt processing uses related SOC21 client/source IDs in `amdkfd/kfd_int_process_v11.c`, `amdkfd/kfd_int_process_v12_1.c`, `amdkfd/soc15_int.h`, and `include/soc15_ih_clientid.h`. The exact enum names in this chunk are mostly hardware selector vocabulary and appear heavily in adjacent generated headers such as `navi10_enum.h` and `soc24_enum.h`, which makes cross-ASIC generated consistency an important integration signal even when direct C references are sparse.

## State And Persistence Behavior

The enum definitions hold no mutable software state and persist nothing. They describe values for stateful hardware blocks:

- Perf-counter mux configuration persists in hardware registers until reprogrammed, reset, power-gated, or restored after suspend/resume.
- IH ring/interface/VF selection values affect interrupt routing and virtualization ring-buffer attribution when placed into IH configuration registers.
- Semaphore, GCR, UTCL1, PH, RMI, and LSDMA selectors control which internal event a counter observes; the counters and hardware FIFOs they observe are mutable hardware state outside this header.
- `ROM_SIGNATURE` is a fixed expected value used to identify ROM image contents, not a stored driver state variable.
- `EFC_SURFACE_PIXEL_FORMAT` values describe command/register programming for video or EFC surface interpretation; actual surfaces, tiling, memory, and format conversion state live elsewhere.

The file does not encode access permissions. Some selected events are counter inputs, some are status signals, some are virtualization-specific state, and some are programming values that may be meaningful only for particular SOC21 SKUs or enabled IP blocks.

## Dependencies And Integration Points

This header depends on the generated SOC21 hardware contract. Its numeric values must stay synchronized with companion SOC21 register headers under `drivers/gpu/drm/amd/include/asic_reg/` and with the hardware register database used to generate `soc21_enum.h`.

Important integration domains:

- AMDGPU perf-counter programming: `PH_PERFCNT_SEL`, `GCRPerfSel`, `UTCL1PerfSel`, `IH_PERF_SEL`, `SEM_PERF_SEL`, `LSDMA_PERF_SEL`, and `RMIPerfSel` are selector namespaces for internal block counters. Consumers need matching selector-field widths and the correct perfmon block/register for each enum family.
- Interrupt handling and virtualization: `IH_CLIENT_TYPE`, `IH_INTERFACE_TYPE`, `IH_RING_ID`, `IH_VF_RB_SELECT`, and the per-VF `IH_PERF_SEL_*_VF*` values tie into IH ring-buffer routing, SR-IOV virtual-function accounting, and KFD/amdgpu interrupt processing.
- DMA/cache/TLB monitoring: `GCRPerfSel`, `UTCL1PerfSel`, `SEM_PERF_SEL`, and `LSDMA_PERF_SEL` connect cache request paths, TLB invalidation/fault behavior, semaphore waits, local SDMA rings, MMHUB, ATCL2, and memory-controller traffic.
- ROM and media paths: `ROM_SIGNATURE` aligns with option-ROM parsing expectations, while `EFC_SURFACE_PIXEL_FORMAT` is an input vocabulary for UVD/EFC surface programming and format negotiation.
- Cross-generation generated headers: similar enum names appear in `navi10_enum.h` and `soc24_enum.h`. Some values intentionally match across generations, while others differ or have added dummy/reserved entries; consumers must include the ASIC-specific header rather than assuming a universal numeric table.

## Risks And Edge Cases

- The chunk begins in the middle of `PH_PERFCNT_SEL`. A final per-file report must merge with the previous chunk before making complete claims about the PH selector range.
- Generated enum drift can compile cleanly while breaking runtime behavior. A wrong selector value can route a perf counter to the wrong event, making diagnostics and power/performance tuning misleading rather than obviously failing.
- Repetitive per-instance patterns are off-by-one sensitive. `PH_PERF_SEL_SC6/SC7_PA0-PA7`, per-SC FIFO status selectors, `IH_PERF_SEL_*_VF0-VF15`, `SEM_PERF_SEL_CPC*_OFFL_E0-E31`, and `LSDMA_PERF_SEL_*_REQ/RET` ranges can be damaged by inserting or deleting one value.
- Sparse values are intentional. `LSDMA_PERF_SEL` skips several IDs, and `EFC_SURFACE_PIXEL_FORMAT` leaves gaps between format families. Code must not assume that every value in the numeric range is valid.
- Virtualization-specific IH selectors are high risk in SR-IOV environments. Misnumbered VF fullness, overflow, wrap, or full-drain-drop events can obscure noisy or wedged virtual functions.
- Pixel-format IDs are hardware ABI, not DRM fourcc values. Treating `EFC_SURFACE_PIXEL_FORMAT` as directly interchangeable with userspace DRM format constants would be unsafe without explicit translation.
- `ROM_SIGNATURE` is endian-sensitive in practice. The constant is `0xaa55` as a numeric value, while byte order in memory or MMIO reads depends on the ROM access path.
- Access type is not represented. Some selected signals may be debug-only, unsupported on specific IP revisions, or require clocks/power domains to be active before reads are meaningful.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU and KFD with SOC21 support to catch missing enum names, duplicate definitions, or include-order issues.
- Mechanically compare `soc21_enum.h` against the authoritative generated hardware database and against the matching SOC21 register field headers for selector width compatibility.
- Diff enum families against nearby generated headers (`navi10_enum.h`, `soc24_enum.h`) while accounting for deliberate ASIC differences, especially `GCRPerfSel`, `UTCL1PerfSel`, `IH_PERF_SEL`, `LSDMA_PERF_SEL`, and `EFC_SURFACE_PIXEL_FORMAT`.
- Runtime perf-counter smoke tests should program representative selectors from PH, GCR, UTCL1, IH, SEM, and LSDMA blocks and confirm counters change under targeted workloads: graphics/primitive traffic, SDMA copies, TLB invalidations or faults, semaphore waits, interrupt storms, and MMHUB memory traffic.
- KFD/SR-IOV testing should exercise interrupt rings and VF ring-buffer pressure so RB full/overflow/wrap/load-RPTR and full-drain-drop signals can be correlated with expected VF behavior.
- Media validation should program representative EFC formats, including RGB, YUV 4:2:0 planar, YUV 4:2:2 packed, high-bit-depth, float, and mono formats, then verify surface interpretation and rejection of unsupported values.
- ROM validation should verify that option-ROM reads identify the `0xaa55` signature through the actual ROM access path used by SOC21 devices.

## Cross-Chunk Notes

The previous chunk contains the start of `PH_PERFCNT_SEL`, including earlier SC and PA selector values. This chunk closes `PH_PERFCNT_SEL`, adds the remaining enum groups through UVD EFC formats, and closes the header guard. The merge lane should combine all chunks for `soc21_enum.h` before summarizing the file-level generated enum namespace.
