# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 21529-22532

## Scope And Purpose

This chunk is the closing 1,004-line section of AMD's generated Vega10 enum header. It starts in the tail of `RMIPerfSel`, then defines the complete `IH_PERF_SEL`, `SEM_PERF_SEL`, and `SDMA_PERF_SEL` performance selector enums, a fixed `ROM_SIGNATURE` constant, small XDMA swizzle/alpha/pipe-selection enums, and the final `_vega10_ENUM_HEADER` include guard close.

The path sits under a `ceph-client` source mirror, but this file is AMDGPU/DRM hardware metadata rather than Ceph filesystem logic. The values are compile-time names for Vega10 hardware encodings used by register programming, performance counter setup, interrupt diagnostics, SDMA diagnostics, ROM validation paths, and XDMA display/cross-display fields. This chunk defines no functions, global storage, locks, allocation paths, IO helpers, or runtime algorithms.

## Important APIs, Types, And Constants

The exported API is the generated C enum/define namespace. Consumers include this header and pass the numeric constants to register fields or descriptor fields defined by companion AMDGPU register headers.

- `RMIPerfSel` tail: the range continues the RMI performance-selector enum from earlier lines and ends it at `RMI_PERF_SEL_RMI_RB_EARLY_WRACK_NACK3 = 0x000000e7`. The covered tail includes RMI/RB 32-byte read returns by CID and NACK lane, RMI-to-TC write/read request selectors by CID, UTC/UTCL1 request and fault selectors, XNACK/latency/PRT/skid FIFO occupancy and busy selectors, TCIW request/busy/residency selectors, multiple ready-to-send/ready-to-receive handshake selectors across xbar/probegenerator/demux/formatter/consumer/pop/xnack paths, reorder FIFO selectors, and early write-ack selectors.
- `IH_PERF_SEL`: a 512-value interrupt-handler performance selector enum from `IH_PERF_SEL_CYCLE = 0x00000000` through `Reserved511 = 0x000001ff`. It covers IH cycle/idle/input/buffer state, RB0/RB1/RB2 full and overflow events, write-pointer writeback and pointer-wrap events, memory-controller write events, BIF line 0 rising/falling events, 16-VF selector ranges for RB0/RB1/RB2 full/overflow/wptr/rptr/BIF events, interrupt client selectors `CLIENT0_INT` through `CLIENT31_INT`, and large reserved ranges preserving hardware selector positions.
- `SEM_PERF_SEL`: a semaphore/performance-monitor selector enum ending at `SEM_PERF_SEL_ATC_INVALIDATION = 0x000000ad`. It covers cycle/idle, request-signal and request-wait events for SDMA0/SDMA1/UVD/VCE0/ACP/ISP/VCE1/VP8/CPG/CPC immediate engines, CPC1/CPC2 offline engine wait selectors for engines 0-31, CPC1/CPC2 offline poll-wait selectors for engines 0-31, memory-controller read/write request and return selectors, and ATC request/return/XNACK/invalidation selectors.
- `SDMA_PERF_SEL`: an SDMA performance selector enum ending at `SDMA_PERF_SEL_MMHUB_TAG_DELAY_COUNTER = 0x000000ff`. It covers SDMA cycle/idle/register idle, ring-buffer empty/full/pointer-wrap/poll/writeback state, RB/IB command FIFO idle/full state, execution idle and poll-timer expiry, MC read/write idle/count/stall selectors, SEM and interrupt request/response selectors, packet count, copy-engine idle/FIFO/stall selectors, queue source selectors for GFX/RLC0/RLC1/page, context-change and doorbell selectors, bus-arbitration read/write selectors, L1/ATCL2 invalidation and XNACK/ACK selectors, DMA L1/MC send selectors, L1 FIFO and L1-to-L2/MC idle selectors, invalidation wait/enable state, and tag-delay counters at `0xfe` and `0xff`.
- `ROM_SIGNATURE`: fixed SMUIO ROM signature constant `0x0000aa55`, matching the common PCI/option-ROM signature value used to identify a valid GPU ROM image header.
- `ENUM_XDMA_LOCAL_SW_MODE`: three XDMA common local swizzle-mode values: `SW_256B_D = 0x2`, `SW_64KB_D = 0xa`, and `SW_64KB_D_X = 0x1a`.
- `ENUM_XDMA_SLV_ALPHA_POSITION` and `ENUM_XDMA_MSTR_ALPHA_POSITION`: four alpha-byte lane selections each, mapping alpha to bits `7:0`, `15:8`, `23:16`, or `31:24`.
- `ENUM_XDMA_MSTR_VSYNC_GSL_CHECK_SEL`: six XDMA master pipe selectors, `PIPE0` through `PIPE5`, used to select which display pipe participates in the VSYNC/GSL check.

## Control Flow And Runtime Behavior

There is no local control flow in this chunk. It is declarative hardware metadata:

1. AMDGPU code includes `vega10_enum.h` along with Vega10 register offset and bitfield headers.
2. Driver logic chooses a selector or field value based on the block being programmed: RMI/IH/SEM/SDMA performance counter programming, interrupt diagnostics, SDMA queue diagnostics, ROM signature checks, or XDMA display setup.
3. The chosen enum value is written into a hardware register field, command/register packet field, or firmware-facing structure by code outside this header.
4. The GPU hardware interprets the numeric value. The C enum name is only a source-level alias.

The file itself performs no validation, range checking, fallback selection, or reserved-value filtering. Any such policy must be implemented by the consumer that picks these values.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. Its constants describe values that can select or affect stateful hardware behavior once written elsewhere.

The state represented by the selectors can persist in GPU register fields, performance counter mux configuration, interrupt-handler diagnostic configuration, SDMA performance monitor state, ROM parsing decisions, and XDMA display-control fields until overwritten, reset, or lost during a GPU reset or power-management transition. Reserved enum slots are also part of the persistent hardware contract because they preserve selector numbering even though they should not be selected as usable events.

## Dependencies And Integration Points

This range depends on the earlier parts of `vega10_enum.h` for the include guard, license block, GL aliases, and the beginning of `RMIPerfSel`. It integrates with companion generated Vega10 headers that define register addresses, register field masks, and shifts. The enum values are meaningful only when paired with the correct Vega10 hardware block and register field width.

Likely integration points include:

- AMDGPU performance counter setup for RMI, IH, SEM, and SDMA blocks.
- IH setup and diagnostics around ring-buffer fullness, overflow, write-pointer writeback, pointer wrapping, BIF line events, client interrupt lines, and SR-IOV/VF-specific event attribution.
- SEM diagnostics for synchronization request/wait behavior from SDMA, media engines, command processor paths, memory controller, and ATC.
- SDMA queue/ring/copy-engine diagnostics, context-change tracking, doorbell activity, MC/L1/ATCL2 traffic, and XNACK/invalidation behavior.
- ROM handling code that checks the `0xaa55` option-ROM signature before consuming ROM contents.
- XDMA master/slave display paths that need stable numeric values for swizzle mode, alpha lane position, and VSYNC/GSL pipe selection.

Nearby generated headers for other ASIC generations, such as `navi10_enum.h`, `soc21_enum.h`, `soc24_enum.h`, and `include/asic_reg/oss/*_enum.h`, provide useful parity references for naming and selector families. They are not drop-in substitutes because selector availability, reserved holes, and numeric assignments differ across GPU generations.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A single numeric change can compile cleanly while selecting the wrong hardware event or field value at runtime.
- The work item begins in the middle of `RMIPerfSel`; the merge lane must combine this with prior chunks before making complete claims about the full RMI selector enum.
- `IH_PERF_SEL` contains many `Reserved*` entries up to `0x1ff`. These reserve selector numbers and should not be treated as valid events unless hardware documentation explicitly says otherwise.
- `SDMA_PERF_SEL` has intentional gaps, including missing values around `0x16`, `0x17`, `0x24`, `0x2c`, `0x2d`, and `0x2f`/`0x30`, plus a jump from `0x5e` to `0xfe`. Code that assumes dense iteration over all values can select undefined hardware events.
- Repetitive VF-indexed IH values are easy to misread or generate incorrectly. RB0/RB1/RB2 groups have similar names but different selector ranges, and an off-by-one index can misattribute interrupt or virtualization behavior.
- SEM CPC offline engine selectors repeat across CPC1/CPC2, wait versus poll-wait, and engine indices 0-31. A wrong family still produces a legal integer but records the wrong diagnostic signal.
- SDMA selector names overlap conceptually with SEM and IH selectors. The enum type does not protect consumers that pass values as raw integers to register helpers.
- XDMA alpha-position enums use the same member suffixes for slave and master blocks but are distinct typedefs. Mixing them may compile in raw integer code while programming the wrong block's field.
- `ROM_SIGNATURE` only identifies the leading ROM signature value; it is not a complete ROM validation policy. Consumers still need bounds checks, table validation, checksum handling where applicable, and device-specific parsing.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU/Vega10 code that includes `vega10_enum.h` to catch duplicate enum names, malformed typedefs, missing include-guard closure, or syntax regressions.
- Mechanically compare lines 21529-22532 against the authoritative Vega10 register database or generated header source, especially `RMIPerfSel` ending at `0xe7`, `IH_PERF_SEL` ending at `0x1ff`, `SEM_PERF_SEL` ending at `0xad`, and `SDMA_PERF_SEL` tag-delay counters at `0xfe` and `0xff`.
- Exercise performance counter selection for RMI, IH, SEM, and SDMA blocks and confirm counters increment under matching workloads: SDMA copies, command processor semaphore waits, memory-controller traffic, ATC invalidation/XNACK behavior, interrupt storms, ring-buffer full/overflow conditions, and VF/PF interrupt activity.
- Validate SR-IOV/VF scenarios where IH per-VF selector ranges are expected to attribute events to the correct virtual function and ring buffer.
- Test SDMA ring-buffer and copy-engine stress paths that trigger RB empty/full, pointer wrap, doorbell, context-change, MC/L1 traffic, invalidation, XNACK, and tag-delay observations.
- Validate ROM parsing with known-good and malformed ROM images to ensure `ROM_SIGNATURE` is only the first acceptance gate.
- Exercise XDMA display paths that use alpha-position, local swizzle mode, and VSYNC/GSL pipe-selection fields, watching for swapped alpha channels, wrong tiling/swizzle behavior, or pipe-selection mismatches.
- Watch for silent failures: bogus performance counter readings, counters stuck at zero, misattributed VF events, missed or overflowing interrupts, SDMA queue stalls, XNACK/invalidation anomalies, ROM parse errors, and display corruption in XDMA paths.

## Cross-Chunk Notes

This chunk closes `vega10_enum.h` with `#endif /*_vega10_ENUM_HEADER*/`. There is no following enum content in this source file after line 22532. The merge/reconciliation lane should join this with earlier `vega10_enum.h` chunks before producing the final per-file research document.
