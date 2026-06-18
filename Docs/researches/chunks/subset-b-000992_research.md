# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 27894-32825

## Scope

This chunk is a middle slice of the auto-generated Gaudi2 Linux-driver block map header. It is not Ceph filesystem logic despite the repository source path; it belongs to the HabanaLabs accelerator driver register-definition layer.

The covered range contains 4,932 preprocessor definitions: 1,644 block base macros, 1,644 maximum-offset macros, and 1,644 section-size macros. It starts inside the `NIC1_QPC0` definition group at `NIC1_QPC0_AXUSER_QPC_RESP_SECTION`, then covers the rest of NIC1's Linux-driver-visible NIC blocks, all NIC2/NIC3/NIC4 block-map entries, and the beginning of NIC5 through `NIC5_QPC0_DBFIFO6_CI_UPD_ADDR_MAX_OFFSET`. The matching `NIC5_QPC0_DBFIFO6_CI_UPD_ADDR_SECTION` is outside this chunk.

## Purpose

The header provides coarse MMIO aperture metadata for Gaudi2 hardware blocks. Each complete block normally appears as a generated macro triplet:

- `mm..._BASE`: 64-bit base address of a hardware block or sub-block.
- `..._MAX_OFFSET`: maximum generated register offset associated with that block.
- `..._SECTION`: generated section size or spacing used by the block map.

This chunk is focused on NIC register apertures. The address range runs from the tail of `NIC1_QPC0` at approximately `0x549f...` through early `NIC5_QPC0` at `0x569f...`. It names queue manager, queue-pair context, user memory region, receive/transmit datapath, master-interface, PHY/SERDES, port MAC, and MAC statistics sub-blocks for NIC1 through NIC5. Driver code uses these bases directly for queue-manager routing and security range programming, and indirectly through `gaudi2_regs.h`, which includes this generated block map before the per-register headers.

## Important APIs, Types, And Definitions

This chunk defines no C functions, structs, enums, or executable APIs. Its public surface is the generated macro namespace exported by `gaudi2_regs.h`.

Important macro families in the covered range include:

- `NIC1_QPC0` tail: the chunk begins with the final `AXUSER_QPC_RESP` section macro, followed by complete `AXUSER_QPC_REQ` and `SPECIAL` triplets.
- `NIC1_UMR1_*`: 15 user-memory-region windows, numbered `0` through `14`, each with `UNSECURE_DOORBELL0`, `UNSECURE_DOORBELL1`, `COMPLETION_QUEUE_CI_0`, `COMPLETION_QUEUE_CI_1`, and `SPECIAL` sub-blocks.
- `NIC1_QM1` and `NIC5_QM0`: queue-manager DCCM/ARC auxiliary windows, the queue-manager base, sixteen `QMAN_WR64_BASE_ADDR*` windows, secured/non-secured AXUSER windows, high/low bandwidth debug windows, CGM, and `SPECIAL` regions.
- `NIC1_QPC1`, `NIC2_QPC0`, `NIC2_QPC1`, `NIC3_QPC0`, `NIC3_QPC1`, `NIC4_QPC0`, `NIC4_QPC1`, and early `NIC5_QPC0`: queue-pair context windows with dense `DBFIFO0` through `DBFIFO29` CI update address triplets, secure and privileged DBFIFO entries, AXUSER windows for congestion queues, RX WQE, TX WQE/LBW QMAN backpressure, DB FIFO, event queue/LBW interrupt, error FIFO, QPC response, QPC request, and a `SPECIAL` region.
- `NIC2_UMR0/UMR1`, `NIC3_UMR0/UMR1`, `NIC4_UMR0/UMR1`, and `NIC5_UMR0`: each UMR instance follows the same 15-window pattern as `NIC1_UMR1`.
- `NIC1`, `NIC2`, `NIC3`, and `NIC4` datapath blocks: timer (`TMR`), receive buffer (`RXB_CORE`), receive engines (`RXE0`, `RXE1`), receive AXUSER completion-queue windows `CQ0` through `CQ31`, transmit scheduler/engine/buffer blocks (`TXS0`, `TXS1`, `TXE0`, `TXE1`, `TXB`), master-interface arbitration/debug/core windows, and `TX_AXUSER`.
- `NIC1` through `NIC4` physical/MAC-side blocks: `SERDES0`, `SERDES1`, `PHY`, `PHY_SPECIAL`, `PRT*_MAC_AUX`, `PRT*_MAC_CORE`, `NIC*_MAC_RS_FEC`, MAC global stat control, RX/TX statistic windows, RS-FEC stats, and four channel groups containing `MAC_PCS`, `MAC_128`, and `MAC_AN`.

Representative base macros from this chunk include `mmNIC2_QM0_BASE`, `mmNIC2_QM1_BASE`, `mmNIC3_QM0_BASE`, `mmNIC3_QM1_BASE`, `mmNIC4_QM0_BASE`, `mmNIC4_QM1_BASE`, and `mmNIC5_QM0_BASE`. These queue-manager bases are consumed directly by Gaudi2 queue ID tables in `gaudi2.c`.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time inclusion and runtime address consumption:

1. `include/gaudi2/asic_reg/gaudi2_regs.h` includes `gaudi2_blocks_linux_driver.h`.
2. Gaudi2 driver C files include the aggregated generated register namespace.
3. Runtime tables and setup code select a block base macro, such as `mmNIC4_QM1_BASE`, for a queue, event source, or security aperture.
4. MMIO helpers or lower-level security/configuration code combine the block base with per-register offsets, queue offsets, protection-bit offsets, or fixed block sizes.

The chunk's ordering follows the generated hardware address map rather than a hand-authored software control path. For NIC2 through NIC4 the pattern is complete and regular: `UMR0`, `QM0`, `QPC0`, `UMR1`, `QM1`, `QPC1`, timer, RX/TX datapath, master interface, physical layer, port MAC, and MAC channel/statistics regions. NIC1 and NIC5 are partial only because of the requested line boundaries.

## State And Persistence Behavior

The header stores no mutable software state and persists nothing by itself. The constants are compiled into the driver and become a hardware ABI for Gaudi2's Linux-driver-visible register map.

The named MMIO regions represent hardware state:

- UMR doorbell and completion-queue CI windows are part of the NIC queue and completion path. Writes or reads by the driver or device agents affect queue progress and completion visibility.
- QM/QMAN regions hold queue-manager control, debug, AXUSER, and WR64 base-address plumbing used to drive NIC work submission.
- QPC DBFIFO CI update and AXUSER windows affect queue-pair context, doorbell FIFO, event/error FIFO, congestion queue, and WQE routing behavior.
- RX/TX datapath, timer, master-interface, PHY/SERDES, and MAC regions expose live NIC datapath, link, statistics, and debug/control state.

Any state persistence belongs to the device: register contents remain until changed by driver writes, firmware/hardware activity, reset, or reinitialization. The header's role is to ensure callers address the intended hardware state.

## Dependencies

Direct dependencies and related files:

- `include/gaudi2/asic_reg/gaudi2_regs.h` includes this generated block map and makes the macros available to Gaudi2 driver code.
- Per-register generated headers included after `gaudi2_blocks_linux_driver.h` provide offsets inside many of the block bases defined here.
- Gaudi2 driver MMIO helpers consume these constants as register aperture addresses.
- `gaudi2.c` uses NIC queue-manager base macros from this generated namespace to map `GAUDI2_QUEUE_ID_NIC_*` entries to QMAN base addresses.
- `gaudi2_security.c` uses MAC and TX AXUSER base macros to define LBW protection ranges for NIC blocks.
- Common security code depends on the repeated NIC layout and notes the regular offset between adjacent NIC UMR windows.

The file is marked auto-generated with a "DO NOT EDIT BELOW" banner. Changes should come from the ASIC register database/generator rather than manual patching.

## Integration Points

The strongest integration point in this chunk is queue routing. `gaudi2.c` maps groups of four NIC queue IDs to queue-manager bases. For example, queue IDs for NIC2/NIC3/NIC4/NIC5 logical engines use `mmNIC1_QM0_BASE`, `mmNIC1_QM1_BASE`, `mmNIC2_QM0_BASE`, `mmNIC2_QM1_BASE`, `mmNIC3_QM0_BASE`, `mmNIC3_QM1_BASE`, `mmNIC4_QM0_BASE`, `mmNIC4_QM1_BASE`, and `mmNIC5_QM0_BASE` from this chunk. If one of these bases is wrong, command submission, event attribution, or queue-manager error handling can target the wrong NIC engine.

Security range setup is another direct integration point. `gaudi2_security.c` builds LBW register ranges beginning at `mmNIC*_TX_AXUSER_BASE` and ending at `mmNIC*_MAC_CH3_MAC_PCS_BASE + HL_BLOCK_SIZE` for NIC0 through NIC10. For NIC1 through NIC4, both endpoints are covered in this chunk; for NIC5 the lower TX/MAC-side endpoint appears later in the file, while this chunk covers the earlier queue-side windows.

The QPC and UMR definitions integrate with NIC doorbell, completion, and queue-pair handling. The repeated `UNSECURE_DOORBELL*`, `COMPLETION_QUEUE_CI_*`, and `DBFIFO*_CI_UPD_ADDR` windows define the addressable apertures used by NIC hardware and low-level driver paths to signal producer/consumer index and doorbell movement.

The MAC and PHY definitions integrate with link management, diagnostics, and statistics collection. The chunk supplies base regions for PCS, 128-bit MAC, autonegotiation, RS-FEC, global RX/TX statistics, per-port MAC aux/core registers, SERDES, and PHY special regions.

## Risks And Edge Cases

The chunk starts and ends mid-definition group. Line 27894 is only `NIC1_QPC0_AXUSER_QPC_RESP_SECTION`; the matching base and max-offset lines are in the preceding chunk. Lines 32824-32825 define the base and max offset for `NIC5_QPC0_DBFIFO6_CI_UPD_ADDR`, but the section macro is in the following chunk. Chunk-level analysis must not treat either boundary as a complete block.

Generated triplets are hardware contracts. A bad `_BASE`, `_MAX_OFFSET`, or `_SECTION` can silently redirect MMIO to a neighboring NIC sub-block, corrupt queue state, break completion signaling, misreport MAC statistics, or leave security apertures underprotected.

The NIC families are repetitive but not interchangeable. NIC2 through NIC4 are complete in this chunk and share the same shape, while NIC1 lacks its earlier `UMR0/QM0/QPC0` prefix here and NIC5 lacks its later `QPC0/QM1/QPC1/datapath/MAC` tail here. Consumers should use the full generated header, not a chunk-local assumption, when deriving all-NIC coverage.

Some sub-blocks have `MAX_OFFSET` values larger than nearby `SECTION` values or vice versa. This appears to be generated hardware metadata, not a simple validation invariant. Static checks should verify exact generated output against the ASIC source rather than imposing a universal relationship between max offset and section size.

Address constants use `ull` and may exceed 32-bit assumptions in other parts of the file. Code that stores these base addresses in too-small intermediates, or subtracts/adds offsets with the wrong type, can truncate the register address.

Queue-manager base arrays create high blast radius for copy/generation drift. A single wrong `mmNIC*_QM*_BASE` macro can make multiple logical queue IDs share or target the wrong QMAN aperture.

Security code depends on exact range endpoints. Incorrect MAC channel or TX AXUSER bases can exclude sensitive control registers from protection or over-protect unrelated registers needed by firmware or diagnostics.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generator, and hardware bring-up oriented:

- Compile Gaudi2 driver code that includes `include/gaudi2/asic_reg/gaudi2_regs.h`; missing or renamed macros from this chunk should fail at compile time.
- Regenerate the block map from the authoritative ASIC register database and compare this header byte-for-byte, especially the NIC1 through NIC5 ranges covered here.
- Static-check complete triplets inside the chunk: every visible `mm..._BASE` should have matching `_MAX_OFFSET` and `_SECTION` companions, except for the explicit chunk-boundary cases.
- Validate queue-manager tables in `gaudi2.c` by checking that NIC queue IDs map to the expected `mmNIC*_QM[01]_BASE` macros for NIC1 through NIC5.
- Run Gaudi2 NIC queue bring-up or simulator tests that submit through queue IDs backed by `mmNIC2_QM0_BASE`, `mmNIC2_QM1_BASE`, `mmNIC3_QM0_BASE`, `mmNIC3_QM1_BASE`, `mmNIC4_QM0_BASE`, `mmNIC4_QM1_BASE`, and `mmNIC5_QM0_BASE`.
- Exercise completion and doorbell paths for UMR/QPC windows, watching for stalled queues, stale completion indices, missed DBFIFO CI updates, or interrupts associated with the wrong NIC.
- Validate security initialization by reading back or tracing LBW protection entries for NIC1 through NIC4 TX/MAC ranges and for the queue-side regions that overlap this chunk.
- Exercise link/statistics diagnostics for NIC1 through NIC4 MAC/PHY regions, including PCS, autonegotiation, RS-FEC, and global RX/TX statistic windows.
- Use static analysis or targeted assertions to ensure these `ull` base constants are not truncated when passed through MMIO, protection-bit, or queue-base calculations.

Regression indicators include queue submissions hanging only on one NIC index, event reports naming the wrong NIC QMAN, completion queues not advancing, MAC statistics reads returning impossible data, link-management failures isolated to one repeated NIC, or security range programming touching unexpected LBW addresses.
