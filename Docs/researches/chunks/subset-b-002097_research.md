# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 22114-24331

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and bit masks used by AMDGPU display code when programming DCN timing generators, shared OPTC controls, ODM memory power controls, display performance counters, and DC I2C/DDC hardware.

The requested slice begins at the tail of the `OTG1` CRC data masks and static-screen/timing-generator fields, covers a complete `OTG2` field family, covers most of the `OTG3` field family, then moves into shared `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_*`, `DC_PERFMON15_*`, and `DC_I2C_*` field definitions. The range ends inside `DC_I2C_READ_REQUEST_INTERRUPT`: it includes all read-request shift definitions and only the first mask line for DDC1. Adjacent chunks are required for the full register's mask set.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct includes in this chunk. Its public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the right-shift count used to extract or place a field in a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used by `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and related AMD display register helpers.

Major macro families in this slice:

- `OTG1_OTG_*`: tail fields for CRC3, CRC signature masks, static-screen detection, 3D structure control, global sync, master update lock, GSL configuration, double-buffer lock windows, DRR timing/status, DSC start position, pipe update status, and OPTC request/spare fields.
- `OTG2_OTG_*`: a full timing-generator instance field set, including horizontal and vertical timing, triggers, force-count/force-vsync controls, master enable, interlace, pixel readback, status counters, stereo control/status, snapshots, interrupts, update lock, double-buffer status, vertical interrupt positions, CRC controls/windows/data, static screen, global sync/update locks, DRR, M/N DTO, DSC position, and pipe update status.
- `OTG3_OTG_*`: the same timing-generator field pattern for a third instance, starting with horizontal timing and running through DRR/DTO/DSC/update/spare fields before the shared blocks.
- `GSL_SOURCE_SELECT` and `OPTC_CLOCK_CONTROL`: global swap lock source selection and OPTC clock gating/test-clock fields.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`: per-memory-slice power force/disable/status fields plus unassigned and vblank power modes.
- `DC_PERFMON15_*`: display performance monitor fields for counter control, counter state, perfmon state, interrupt/ack/status, high/low compare or read values, counted value type, hardware stop selection, run-enable selection, and counter value storage.
- `DC_I2C_*`: I2C control, arbitration, interrupt, software status, per-DDC hardware status, per-DDC speed/setup, transaction descriptors, data FIFO/index access, EDID detect controls, and read-request interrupt fields.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from generated-token consumers:

1. DCN 3.5.1 resource, IRQ, and DMUB code includes this file together with `dcn_3_5_1_offset.h`.
2. Register-list macros in `dcn351_resource.c` and related headers paste symbolic names into constants such as `OTG2_OTG_CONTROL__OTG_MASTER_EN_MASK` or `DC_I2C_CONTROL__DC_I2C_GO__SHIFT`.
3. Static shift/mask tables such as `optc_shift`, `optc_mask`, I2C shift/mask tables, HW sequencer masks, IRQ source descriptors, and DMUB register masks are initialized from these macros.
4. Runtime code then sequences the hardware through register helpers. Timing-generator code uses the OTG/OPTC masks for modeset, vblank/vupdate handling, CRC capture, dynamic refresh, stereo/interlace, and update locking. I2C/DDC code uses the I2C masks for EDID/DDC transactions. IRQ service code uses interrupt status/clear/enable masks for vblank, vline, vupdate, hotplug, and related display interrupts.

The masks do not encode ordering rules. Consumers must still sequence power, clock enablement, update locks, interrupt acknowledgment, double-buffer commits, timing changes, and I2C arbitration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes fields inside MMIO-backed display hardware registers. The represented state includes:

- Timing-generator state for OTG instances 1-3: master enable, horizontal/vertical totals, blanking/sync windows, counters, frame/vblank/vupdate/vready status, force triggers, stereo/interlace state, snapshots, CRC windows/data, DRR timing, DSC position, and update-pending state.
- Synchronization state: global swap lock source selection, per-OTG GSL enable/master/delay/window configuration, master update locks, and vupdate keepout windows.
- Interrupt state: vertical interrupt positions/status/clear/type fields, global sync status/clear fields, DRR timing interrupt fields, static-screen CPU interrupt fields, I2C hardware-done/read-request interrupt fields, and performance counter interrupt/status/ack fields.
- Power and clock state: OPTC clock gate/test-clock bits and ODM memory force/disable/status fields.
- I2C/DDC transaction state: software/hardware ownership arbitration, transaction descriptors, selected DDC channel, go/reset bits, prescale/threshold/timing, per-DDC enable/setup, EDID detect control/status, data FIFO/indexing, and software status outcomes such as done, timeout, abort, overflow, and stopped-on-NACK.

Register persistence is hardware-defined. Configuration fields generally remain until reprogrammed, power-gated, reset, or lost across suspend/resume. Status, interrupt, clear, ack, pending, busy, and data/FIFO fields may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive; this header only supplies bit positions and cannot distinguish those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match the sibling offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` supplies the MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` includes both generated headers and initializes DCN351 resource tables. Its `optc_shift` and `optc_mask` use `OPTC_COMMON_MASK_SH_LIST_DCN3_5(__SHIFT)` and `_MASK`, which expand into OTG/OPTC/GSL field definitions from this generated namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h` defines the DCN3.5 OPTC mask-list macro and declares timing-generator operations such as CRC configuration, DRR programming, long-vtotal programming, FGCg control, and OTG disable waits.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h` maps `DC_I2C_*` field definitions into `struct dce_i2c_shift` and `struct dce_i2c_mask`; `dce_i2c_hw.c` then uses them to program hardware I2C/DDC transactions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` and `hw_ddc.c` use DDC setup and EDID-detect masks for connector detection flows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` includes this mask header for IRQ register descriptors and maps hardware source IDs to DAL IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` initializes DMUB-visible field masks and shifts through `FD_MASK` and `FD_SHIFT`.

## Risks And Edge Cases

- Field drift is the central risk. These constants are untyped preprocessor values, so an incorrect shift or mask can compile cleanly while corrupting an unrelated register field at runtime.
- Repeated OTG instances are copy-sensitive. `OTG2` and `OTG3` should be structurally parallel, while this chunk only contains the tail of `OTG1`; an instance-specific typo may only appear with particular pipes, multi-display layouts, or timing-generator assignments.
- The chunk boundary is artificial. It starts after the first `OTG1_OTG_CRC3_DATA_B` shift/mask lines and ends before the rest of `DC_I2C_READ_REQUEST_INTERRUPT` masks, so file-level conclusions must be reconciled with adjacent chunks.
- Interrupt and clear/ack fields are side-effect-sensitive. Bad masks in vblank/vline/vupdate/DRR/static-screen/I2C/perfmon fields can cause missed interrupts, interrupt storms, stale pending bits, or lost acknowledgments.
- Update-lock, double-buffer, and keepout masks are timing-sensitive. A wrong field can cause updates to land outside vblank/vupdate windows, leading to tearing, underflow, cursor/plane update stalls, or modeset hangs.
- CRC, pixel readback, and perfmon fields affect diagnostics and validation. Errors may not break normal display output but can invalidate automated CRC tests, debug readbacks, performance telemetry, or interrupt-driven counter collection.
- I2C/DDC masks directly affect EDID and AUX-adjacent connector workflows. Incorrect transaction count, data index, arbitration, timeout, stop-on-NACK, prescale, or DDC setup fields can cause intermittent monitor detection failures that depend on cable, sink behavior, or bus speed.
- Power-management masks such as `OPTC_CLOCK_CONTROL` and `ODM_MEM_PWR_*` interact with clock gating and memory retention; wrong values can manifest only after idle, vblank power transitions, suspend/resume, or runtime power management.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for DCN351 display code with this header included by `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c`; failures often show as missing token-pasted macro names or struct initializer mismatches.
- Display modeset tests across multiple pipes, especially configurations using OTG2 and OTG3, to exercise horizontal/vertical timing, master enable, vblank/vupdate/vready, double-buffer updates, and update-lock paths.
- CRC capture/readback tests, including windowed CRC and multiple CRC slots, to verify OTG CRC field masks.
- Vblank, vline, page-flip, vupdate, static-screen, and DRR interrupt tests to catch incorrect status, clear, mask, or type fields.
- Variable refresh rate / DRR and long-vtotal tests to exercise `OTG_DRR_*`, `OTG_V_TOTAL_*`, and trigger-window fields.
- Multi-display synchronized-update tests to exercise GSL source selection, GSL windows, master update lock, and vupdate keepout behavior.
- EDID/DDC tests over each exposed DDC engine, including NACK, timeout, repeated-start, and read-request cases, to validate `DC_I2C_*` control, transaction, status, setup, speed, and interrupt fields.
- Suspend/resume and runtime power-management tests to exercise OPTC clock gating and ODM memory power fields.
- Perf counter smoke tests, if available, to confirm `DC_PERFMON15_*` control/status/value/interrupt masks match the ASIC register layout.
