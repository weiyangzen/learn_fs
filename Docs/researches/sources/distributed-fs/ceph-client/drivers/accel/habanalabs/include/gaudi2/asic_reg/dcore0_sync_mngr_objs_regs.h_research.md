# Research: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000980`: lines 1-9404, `Docs/researches/chunks/subset-b-000980_research.md`
- `subset-b-000981`: lines 9405-18572, `Docs/researches/chunks/subset-b-000981_research.md`
- `subset-b-000982`: lines 18573-27140, `Docs/researches/chunks/subset-b-000982_research.md`
- `subset-b-000983`: lines 27141-36256, `Docs/researches/chunks/subset-b-000983_research.md`
- `subset-b-000984`: lines 36257-43543, `Docs/researches/chunks/subset-b-000984_research.md`

## Chunk Research

### subset-b-000980: lines 1-9404

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 1-9404

## Purpose

This chunk is the opening portion of an auto-generated Gaudi2 ASIC register header for the DCORE0 sync-manager objects block. The header identifies the block as `DCORE0_SYNC_MNGR_OBJS`, based on the `SOB_OBJS` prototype, and begins the generated MMIO offset map used by the HabanaLabs driver to address hardware synchronization objects.

Within lines 1-9404, the substantive content is the first contiguous part of the sync object bank: `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0` through `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_4690`. These macros expose 32-bit register offsets from `0x4100000` through `0x4104948`, with one register every 4 bytes. The overall file continues after this chunk with more `SOB_OBJ` entries and later sync-manager object register families.

## Important APIs, Types, And Functions

This chunk does not define C functions, structs, enums, or executable control logic. Its API surface is the generated preprocessor register namespace:

- `ASIC_REG_DCORE0_SYNC_MNGR_OBJS_REGS_H_`: include guard for the generated register header. The guard begins in this chunk; the closing `#endif` is outside this line range.
- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_n`: per-sync-object MMIO offset constants for DCORE0. In this chunk, `n` ranges from `0` to `4690`.
- Addressing rule: `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_n == 0x4100000 + (n * 4)` for every entry covered here.

The register bit fields are not described in this file. Consumers combine these offsets with masks from Gaudi2 mask headers, especially `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_VAL_MASK`, `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_INC_MASK`, and `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_SIGN_MASK`, to construct values written to the SOB registers.

## Control Flow

There is no runtime control flow in this chunk. The C preprocessor makes the symbolic offsets available to any translation unit that includes `gaudi2_regs.h`, which includes this generated header.

Runtime control flow appears in the consuming Gaudi2 driver code:

1. Initialization code uses the first SOB offset as an array base, usually `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0`.
2. Driver paths compute per-object addresses as `base + sob_id * sizeof(u32)` or `base + sob_offset`.
3. MMIO helpers such as `WREG32()` and `RREG32()` read or write those computed offsets.
4. Monitor setup code programs monitor payload addresses to point at SOB registers, allowing hardware monitors to increment, decrement, or test synchronization objects.

Because this header provides literal offsets only, all ordering, bounds checking, and synchronization semantics are imposed by the caller and by the hardware block.

## State And Persistence Behavior

The header itself owns no software state and persists nothing. Its constants name hardware state: each `SOB_OBJ_n` register is a sync object slot in DCORE0's sync-manager object aperture.

Writes to these registers affect device MMIO state. In the observed Gaudi2 consumers, SOB registers are reset by writing zero, incremented with payloads built from the SOB value/increment masks, and used as completion or interrupt synchronization counters. That hardware state persists until overwritten by the driver, modified by hardware monitor activity, or reset by device/firmware initialization.

This chunk covers only a prefix of the SOB array. The full driver-level SOB count is computed elsewhere from `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` and `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0`, so code that assumes the complete 8192-entry array must include the rest of the generated header, not just this chunk.

## Dependencies

- `gaudi2_regs.h` includes this generated register header and provides the normal aggregation point for Gaudi2 register offsets.
- `gaudi2P.h` derives `DCORE_NUM_OF_SOB` from the first and last SOB register macros and defines `SM_OBJS_BLOCK_SIZE` from the sync-manager object block boundaries.
- `gaudi2_masks.h` supplies bit masks and shifts used when writing values to SOB registers. For example, `GAUDI2_SOB_INCREMENT_BY_ONE` combines SOB value and increment fields rather than using raw literal payloads.
- Driver MMIO accessors such as `WREG32()` and `RREG32()` consume these offsets as low-bandwidth register addresses, often adding `CFG_BASE` when a hardware agent must be programmed with a full physical MMIO address.
- The hardware contract is that the generated offsets match the Gaudi2 register map exactly. The source is marked auto-generated and should be regenerated from the ASIC database rather than hand-edited.

## Integration Points

The main integration point is the Gaudi2 sync-manager and monitor infrastructure:

- Queue-manager initialization programs command processor message bases with `CFG_BASE + mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0`, allowing queue managers to target the SOB aperture.
- Completion and interrupt flows compute addresses from `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0 + sob_id * 4` and program monitor payloads or bridge doorbell registers to update those SOBs.
- Device initialization and cleanup paths clear reserved SOB slots with `WREG32(mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0 + sob_offset, 0)`.
- Security setup uses the SOB object range together with monitor/config/security offsets later in the same generated header to configure protection for exposed sync-manager object regions.

For this chunk specifically, the useful integration invariant is the dense 4-byte stride. Consumers rarely reference individual high-numbered macros directly; instead they use the base macro and derive addresses arithmetically.

## Risks And Edge Cases

- Off-by-one or stride errors are high impact. If a caller computes `sob_id * 4` against the wrong base or allows an out-of-range `sob_id`, it can write the wrong sync object or move into the next sync-manager register family.
- The chunk is incomplete by design. It ends at `SOB_OBJ_4690` while the full file continues; per-file research must reconcile later chunks before making claims about all SOBs, monitor registers, config registers, or security registers.
- Generated headers are fragile to manual edits. Renumbering a macro, changing an address literal, or introducing a gap would break driver assumptions such as `DCORE_NUM_OF_SOB` and array-style MMIO indexing.
- Bit interpretation is external. A raw write to a SOB register is not self-documenting without the masks in `gaudi2_masks.h`; consumers must use the correct value, increment, and sign fields for the intended hardware operation.
- Security and user-mapping code depends on exact range endpoints. An incorrect SOB start or end address could expose sync objects incorrectly or fail to protect registers that affect completion signaling.

## Test Signals

- Compile coverage should include translation units that include `include/gaudi2/asic_reg/gaudi2_regs.h`; missing or renamed macros will fail at build time.
- Static checks can verify the generated arithmetic invariant for this chunk: 4691 macros, `SOB_OBJ_0 == 0x4100000`, `SOB_OBJ_4690 == 0x4104948`, and a constant 4-byte stride with no index gaps.
- Driver smoke tests that initialize Gaudi2 queue managers, monitors, decoder interrupts, and completion paths exercise this register family through `WREG32()` and monitor payload programming.
- Runtime diagnostics around SOB reset/readback and completion signaling are useful integration signals, because failures often appear as hung command submissions, missed interrupts, or stale monitor state rather than as direct errors from this header.

### subset-b-000981: lines 9405-18572

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 9405-18572

## Scope

This chunk covers the middle of the auto-generated Gaudi2 DCORE0 sync-manager object register header. The file declares preprocessor constants only; there are no C functions, structs, enums, branches, or storage objects in this slice. Lines 9405-18572 contain 4,584 `#define` entries and no other nonblank content.

The chunk starts inside the sync object array and ends inside the monitor payload low-address array, so the final file-level merge must combine this with adjacent chunks for complete register-family coverage.

## Purpose

The constants in this chunk expose memory-mapped register offsets for the DCORE0 sync-manager object block. Driver code uses these offsets with `RREG32`, `WREG32`, command-packet builders, and LBW memset helpers to program synchronization objects and monitors on Gaudi2 hardware.

The covered register families are:

| Family | Lines | Index range | Address range | Count | Layout |
| --- | ---: | ---: | ---: | ---: | --- |
| `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_n` | 9405-16405 | 4691-8191 | `0x410494C`-`0x4107FFC` | 3501 | contiguous 32-bit words |
| `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_n` | 16407-18571 | 0-1082 | `0x4108000`-`0x41090E8` | 1083 | contiguous 32-bit words |

The `SOB_OBJ` range is the tail of the 8192-entry sync-object array. The `MON_PAY_ADDRL` range is the beginning of the monitor payload low-address array. Both arrays advance by 4 bytes per index, and no gaps were observed inside the assigned line range.

## Important APIs, Types, And Constants

This chunk defines register-address macros, not callable APIs:

- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_4691` through `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` map sync object registers from `0x410494C` through `0x4107FFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` through `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_1082` map monitor payload low-address registers from `0x4108000` through `0x41090E8`.

The most important symbols in this chunk from an integration perspective are the boundary constants:

- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` is used by `gaudi2P.h` to derive `DCORE_NUM_OF_SOB`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` is used by `gaudi2.c` as the base of the monitor payload low-address array and as the end boundary for the SOB-object region.

Most runtime code does not reference the high numbered `SOB_OBJ_n` or `MON_PAY_ADDRL_n` macros directly. It uses the `_0` macro plus `id * sizeof(u32)` / `id * 4`, relying on the generated per-index macros to document and preserve the same contiguous hardware map.

## Control Flow

There is no executable control flow in this chunk. The effective control flow appears in consumers:

- Queue-manager initialization writes `CFG_BASE + mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` and `CFG_BASE + mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0` into QMAN CP/PQC base registers.
- Monitor setup computes `mon_offset = mon_id * sizeof(u32)` and programs `MON_PAY_ADDRL_0 + mon_offset` for monitor message destination addresses.
- SOB reset and restore paths compute `sob_offset = sob_id * sizeof(u32)` and access `SOB_OBJ_0 + sob_offset`.
- Device initialization clears user-available SOBs by using `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0 - (mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0 + offset)` as the byte size of the SOB region to clear.

For this chunk specifically, control-flow relevance is boundary-driven: the transition from `SOB_OBJ_8191` at `0x4107FFC` to `MON_PAY_ADDRL_0` at `0x4108000` is the hardware boundary used by memset sizing and register-array count calculations.

## State And Persistence Behavior

The header itself persists no software state. It names MMIO locations for hardware state:

- `SOB_OBJ` registers hold synchronization object values used by queues, completions, monitor arming, and reset paths.
- `MON_PAY_ADDRL` registers hold the low 32 bits of destination addresses written by monitor-triggered messages.

State is volatile hardware state. The driver initializes, clears, restores, or re-arms these registers during device setup, reset, command submission support, and interrupt/fence programming. Because this chunk only defines DCORE0 offsets, other DCORE instances are reached in consumers by adding `DCORE_OFFSET`.

## Dependencies

Direct dependencies are minimal because this is a generated header:

- The include guard and file context identify the block as `DCORE0_SYNC_MNGR_OBJS` with prototype `SOB_OBJS`.
- Consumers depend on Linux/Habanalabs register helpers such as `RREG32`, `WREG32`, `lower_32_bits`, `upper_32_bits`, `FIELD_PREP`, and device constants such as `CFG_BASE`, `DCORE_OFFSET`, and `sizeof(u32)`.
- Bitfield meaning for SOB and monitor programming is supplied by related generated mask headers, for example `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_*_MASK`, `DCORE0_SYNC_MNGR_OBJS_MON_ARM_*_MASK`, and monitor config/status masks outside this chunk.

The chunk is coupled to generated register maps for the rest of the same block, especially the preceding `SOB_OBJ_0`-`SOB_OBJ_4690` definitions and later `MON_PAY_ADDRL_1083+`, `MON_PAY_ADDRH`, `MON_PAY_DATA`, `MON_ARM`, `MON_CONFIG`, `MON_STATUS`, and security-region definitions.

## Integration Points

Observed Gaudi2 integration points include:

- `drivers/accel/habanalabs/gaudi2/gaudi2P.h` derives `DCORE_NUM_OF_SOB` from `SOB_OBJ_8191 - SOB_OBJ_0`.
- `drivers/accel/habanalabs/gaudi2/gaudi2.c` initializes QMAN completion and monitor bases using `MON_PAY_ADDRL_0` and `SOB_OBJ_0`.
- `gaudi2_arm_monitors_for_virt_msix_db()` programs `MON_PAY_ADDRL_0 + mon_offset` as part of a three-monitor sequence that writes MSI-X doorbells, decrements a SOB, and re-arms the master monitor.
- user-context reset/restore code clears SOBs up to `MON_PAY_ADDRL_0`, making the address boundary in this chunk part of the clearing contract.
- command buffer construction uses `MON_PAY_ADDRL_0` as the monitor message base and computes short message offsets to `MON_PAY_ADDRL`, `MON_PAY_ADDRH`, `MON_PAY_DATA`, and `MON_ARM` arrays.
- security setup references the sync-manager object block and comments on the 8192 SOB objects, matching the `SOB_OBJ_8191` terminal index covered here.

## Risks

- The generated map is a hardware ABI. A wrong address, skipped index, or changed stride would silently redirect MMIO writes and could break queue completion, monitor programming, resets, or security initialization.
- The boundary at `SOB_OBJ_8191` / `MON_PAY_ADDRL_0` is used as both a count and a byte-size delimiter. Off-by-one changes can cause incomplete SOB clearing or writes into monitor payload registers.
- Consumers assume 32-bit spacing and compute offsets manually. Any future hardware generation with non-4-byte stride would require code changes, not just regenerated macro names.
- This chunk starts and ends mid-file; reviewing it alone cannot validate the full monitor array count or later arrays such as `MON_PAY_ADDRH`, `MON_PAY_DATA`, `MON_ARM`, and `MON_STATUS`.
- The file is marked auto-generated. Manual edits should be avoided because they risk divergence from the authoritative ASIC register database.

## Test And Validation Signals

Useful validation signals for this chunk are structural and integration-oriented:

- Build coverage: compile Gaudi2 Habanalabs driver code that includes this header and references `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` and `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0`.
- Static map checks: verify each covered family increments index by 1 and address by 4 bytes. This chunk passed that check for `SOB_OBJ_4691`-`8191` and `MON_PAY_ADDRL_0`-`1082`.
- Boundary checks: confirm `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191 + 4 == mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0`.
- Runtime hardware tests: queue completion, monitor-triggered MSI-X doorbell handling, SOB reset, device reset/restore, and user SOB clearing paths exercise the register bases and the SOB-to-monitor boundary.
- Security/init validation: checks that user-available SOB ranges begin after reserved pending command-submission SOBs and that all DCOREs are cleared through `DCORE_OFFSET`-derived addresses.

## Cross-Chunk Notes

The merge lane should join this with earlier and later chunks to recover whole-file semantics:

- Earlier lines define `SOB_OBJ_0` through `SOB_OBJ_4690`, including the base macro most consumers use.
- Later lines continue `MON_PAY_ADDRL` beyond index 1082 and define additional monitor payload, arm, config, status, and security-region arrays.
- Whole-file research should describe the full sync-manager object layout from SOB objects through all monitor and security regions, while this chunk only proves the mid-file SOB tail and start of low-address monitor payload layout.

### subset-b-000982: lines 18573-27140

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h Research Chunk subset-b-000982

Scope: lines 18573-27140 of `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h`.

## Purpose

This chunk is part of an auto-generated Gaudi2 ASIC register-address header for DCORE0 sync-manager objects. The covered range defines MMIO offsets for monitor payload storage in the DCORE0 sync manager:

- The tail of `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_*`, monitor payload low-address registers, from index 1083 through 2047.
- All `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRH_*`, monitor payload high-address registers, from index 0 through 2047.
- The first part of `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_*`, monitor payload data registers, from index 0 through 1270.

These macros are not executable logic. They encode the hardware register map consumed by Gaudi2 driver code when programming sync-manager monitors. A monitor can be armed against a SOB condition and, when triggered, writes one or more payload words to configured target addresses. The three arrays in this chunk provide the per-monitor write target address low word, target address high word, and payload data word.

## Register Families In This Chunk

The chunk contains 4,284 `#define` entries. All register addresses are 32-bit MMIO offsets and advance by 4 bytes per monitor index.

| Register family | Lines | Indices | Address range | Count | Meaning |
| --- | ---: | ---: | --- | ---: | --- |
| `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_*` | 18573-20501 | 1083-2047 | `0x41090EC`-`0x4109FFC` | 965 | Low 32 bits of each monitor payload write address. Indices 0-1082 are in the previous chunk. |
| `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRH_*` | 20503-24597 | 0-2047 | `0x410A000`-`0x410BFFC` | 2048 | High 32 bits of each monitor payload write address. |
| `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_*` | 24599-27139 | 0-1270 | `0x410C000`-`0x410D3D8` | 1271 | Payload data word written by a monitor. Indices 1271-2047 continue in the next chunk. |

The ranges show a contiguous layout:

- `MON_PAY_ADDRL_0` starts at `0x4108000` outside this chunk; this chunk resumes at `MON_PAY_ADDRL_1083`.
- `MON_PAY_ADDRH_0` starts immediately after the full low-address array, at `0x410A000`.
- `MON_PAY_DATA_0` starts immediately after the full high-address array, at `0x410C000`.

## Important APIs, Types, And Functions

This header slice defines preprocessor constants only. It declares no C functions, structs, enums, inline helpers, or exported symbols. The important API surface is the macro naming contract:

- Consumers refer to a base macro such as `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` and add `mon_id * sizeof(u32)` when the monitor ID is dynamic.
- Generated code and register tooling can also reference explicit indexed macros such as `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRH_2047`.
- Field layout is defined in the sibling mask header `dcore0_sync_mngr_objs_masks.h`: `MON_PAY_ADDRL`, `MON_PAY_ADDRH`, and `MON_PAY_DATA` all expose a full-width 32-bit field.

The key consumers in `drivers/accel/habanalabs/gaudi2/gaudi2.c` include:

- `gaudi2_init_qman_cp()`, which programs QMAN CP message-base registers with `CFG_BASE + mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0`. This lets message-short packets address monitor payload registers by offset.
- Virtual MSI-X doorbell setup, which writes `MON_PAY_ADDRL`, `MON_PAY_ADDRH`, and `MON_PAY_DATA` entries so a monitor can write an interrupt ID, decrement a SOB, and re-arm a master monitor.
- `gaudi2_arm_cq_monitor()`, which uses a monitor payload address/data pair for completion-queue notification when monitor CQ mode is enabled.
- `gaudi2_gen_wait_cb()`, which emits message-short packets targeting offsets from `MON_PAY_ADDRL_0` to configure monitor address low, address high, data, and arm registers from generated command buffers.
- Context and reset paths that clear sync-manager SOB/monitor state around user-context reuse.

## Control Flow

There is no runtime control flow in this chunk. The practical control flow occurs in downstream driver code:

1. The driver chooses a monitor ID and computes `mon_offset = mon_id * 4`.
2. It writes the target low address to `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0 + mon_offset`.
3. It writes the target high address to `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRH_0 + mon_offset`.
4. It writes the payload word to `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_0 + mon_offset`.
5. It configures/arms the corresponding monitor via adjacent monitor config/arm registers, outside this chunk.
6. Hardware later observes the armed SOB condition and performs the programmed payload write.

Because the header exposes a linear, fixed-stride address map, most call sites use the `_0` base macro plus offsets rather than naming every indexed macro directly.

## State And Persistence Behavior

The header itself holds no mutable state and has no persistence behavior. It defines the addresses for persistent hardware-visible state in the DCORE0 sync-manager MMIO aperture.

The hardware state represented by these registers persists until explicitly overwritten, reset, or cleared by driver reset/context cleanup paths. Important state properties:

- Each monitor has independent address-low, address-high, and data payload words.
- The payload target can point at sync objects, monitor arm registers, QMAN fence registers, virtual MSI-X doorbell memory, or completion queue notification targets, depending on monitor configuration.
- Incorrect stale monitor payloads can affect later command submissions if monitor state is reused without reset.
- The driver clears sync-manager user resources on context teardown/reset by memset-style writes over SOB and monitor register ranges, and by reprogramming monitor payloads before arming them.

The chunk covers only DCORE0 register addresses. Other DCOREs use corresponding offsets derived elsewhere, typically by adding a DCORE stride.

## Dependencies

This header depends on the generated Gaudi2 register-map convention and is normally included through broader Gaudi2 ASIC register headers. It is tightly coupled to:

- `dcore0_sync_mngr_objs_masks.h` for bit masks and shifts used to build payload-adjacent monitor configuration values.
- Gaudi2 driver MMIO helpers such as `WREG32`, `RREG32`, `FIELD_PREP`, `lower_32_bits`, and `upper_32_bits`.
- Common hardware constants such as `CFG_BASE`, `DCORE_OFFSET`, monitor counts, SOB layout, and queue-manager message-base offsets.
- The sync-stream and command-buffer generation logic in `gaudi2.c`, which assumes monitor payload arrays are 4-byte indexed and contiguous.

The file is Linux kernel driver code under the Habana Labs accelerator tree, not Ceph filesystem logic despite the repository snapshot path containing `distributed-fs/ceph-client`.

## Integration Points

The covered macros are integration points between generated hardware register descriptions and driver behavior:

- QMAN CP message-short packets use `MON_PAY_ADDRL_0` as a message base, allowing command buffers to program monitor registers through small offsets.
- Sync-stream waits use monitor payload registers to write QMAN fence registers once a SOB reaches the required value.
- Completion handling uses monitors to emit CQ or MSI-X-style notifications after command submission progress.
- Virtual MSI-X doorbell support configures multi-write monitors that can notify, update SOB values, and re-arm related monitors.
- Reset and context restore code treats the sync-manager object address space as a hardware state block that must be cleared before reuse.

## Risks And Edge Cases

- Off-by-one index mistakes are high impact. This chunk starts in the middle of `MON_PAY_ADDRL` at index 1083 and ends in the middle of `MON_PAY_DATA` at index 1270; merge/reconciliation must preserve continuity with adjacent chunks.
- The indexed register layout depends on a strict 4-byte stride. Any call site using `mon_id * 4` assumes the generated addresses stay contiguous.
- Address-family confusion is dangerous. Writing a low address into `MON_PAY_DATA`, or payload data into `MON_PAY_ADDRH`, can redirect monitor writes or corrupt unrelated device state.
- The macros describe DCORE0 only. Applying these addresses to another DCORE without adding the proper DCORE offset would program the wrong sync manager.
- Monitor payload registers are security-sensitive because they can cause hardware writes to configured addresses. Driver validation and context cleanup need to prevent user-controlled monitor state from escaping its intended resource allocation.
- Generated headers are brittle under manual edits. The file banner marks the register map as auto-generated; local changes should come from the register-generation source, not hand edits.

## Test Signals

Useful validation signals for this chunk are mostly structural and integration oriented:

- Compile-time: Gaudi2 driver code builds with references to `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0`, `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRH_0`, and `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_0`.
- Register-map sanity: each family increments by exactly `0x4` per index; `ADDRL_2047` is `0x4109FFC`, `ADDRH_0` is `0x410A000`, `ADDRH_2047` is `0x410BFFC`, and `DATA_0` is `0x410C000`.
- Runtime sync tests: command submissions using sync-stream wait/signal paths complete, CQ monitor notifications arrive, and virtual MSI-X doorbell monitors fire exactly once per programmed condition.
- Reset/context tests: after context teardown or compute reset, reused monitors do not retain old payload address/data values.
- Fault diagnostics: monitor misconfiguration should surface as command submission hangs, missing CQ/MSI-X notifications, unexpected SOB values, or RAZWI/access errors in Gaudi2 event handling.

### subset-b-000983: lines 27141-36256

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 27141-36256

## Scope

This chunk is an auto-generated Gaudi2 ASIC register-address header slice for the DCORE0 sync-manager objects block. It contains only C preprocessor `#define` constants and blank separator lines. There are no functions, types, executable statements, comments, conditionals, or local control flow inside the assigned line range.

The source file itself is guarded by `ASIC_REG_DCORE0_SYNC_MNGR_OBJS_REGS_H_`, carries a GPL-2.0 SPDX tag, and identifies the register block as `DCORE0_SYNC_MNGR_OBJS` with prototype `SOB_OBJS`. The chunk covers register families used by monitor programming:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_1271` through `_2047`, addresses `0x410D3DC` through `0x410DFFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_ARM_0` through `_2047`, addresses `0x410E000` through `0x410FFFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_0` through `_1732`, addresses `0x4110000` through `0x4111B10`.

The assigned range has 4,558 register defines. Every define is a 32-bit MMIO address spaced by 4 bytes from the previous index in the same family. The range begins in the middle of the `MON_PAY_DATA` array because earlier chunk coverage contains `MON_PAY_DATA_0` through `_1270`; it ends in the middle of `MON_CONFIG`, with `_1733` through `_2047` continuing after this chunk.

## Purpose

The header gives the Gaudi2 driver symbolic names for DCORE0 sync-manager monitor MMIO locations. The sync manager is used to connect hardware sync objects (SOBs), monitors, completion queues, and MSI-X signaling. These constants let C code write monitor payload data, arm monitors against SOB groups, and configure monitor behavior without embedding raw offsets.

Within this chunk:

- `MON_PAY_DATA_n` is the 32-bit payload value written by monitor `n` when its trigger condition fires. Consumers use it for values such as SOB decrement payloads, monitor re-arm words, completion queue payloads, fence writes, or interrupt IDs.
- `MON_ARM_n` is the 32-bit arm/control register for monitor `n`. It binds the monitor to a sync-object group, mask, comparison operation, and sync-object data threshold/value.
- `MON_CONFIG_n` is the 32-bit configuration register for monitor `n`. It controls options such as CQ mode, LBW write enablement, number of writes in a multi-message monitor, long-SOB handling, high SID bits, and high-group selection.

The chunk is hardware-description data, not a policy layer. The driver behavior comes from code that combines these base addresses with indexes and field masks from the companion masks header.

## Important APIs, Types, And Register Families

There are no APIs, structs, enums, or functions declared by this chunk. Its public interface is the macro namespace consumed by Gaudi2 driver code and by any generated register/mask tooling.

Important macro families:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_*`: contiguous payload-data MMIO array. In this chunk the visible subset is index `1271..2047`, completing the 2,048-monitor payload-data region that starts at `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_0` on earlier lines. Driver code usually computes `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_0 + mon_id * 4`; individual high-index symbols are mainly generated-map completeness.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_ARM_*`: full contiguous monitor-arm MMIO array for indexes `0..2047`. The companion masks define fields `SID`, `MASK`, `SOP`, and `SOD`. `SID` selects the SOB group, `MASK` selects participating SOBs within the group, `SOP` selects comparison mode, and `SOD` carries comparison data.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_*`: contiguous monitor-config MMIO array. This chunk covers `0..1732`, while the rest of the file continues through `_2047`. The companion masks define `LONG_SOB`, `CQ_EN`, `WR_NUM`, `LBW_EN`, `MSB_SID`, and `LONG_HIGH_GROUP`.

Related constants outside this chunk are part of the same contract:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` and `_ADDRH_0` hold the low/high destination address for monitor writes.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_0` is used by driver code to size and reset monitor state.
- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0` is the sync-object base used with monitor arm fields.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0` bounds the user-accessible sync-manager object block in reset/restore paths.
- `DCORE_NUM_OF_MONITORS` in `gaudi2P.h` computes the monitor count from `MON_STATUS_2047 - MON_STATUS_0`, matching the 2,048-entry monitor arrays represented here.

## Control Flow

This chunk has no direct control flow. Its values enter driver control flow through MMIO reads/writes and generated command buffers.

Primary runtime flows using these register families include:

- Virtual MSI-X doorbell preparation in `gaudi2_arm_monitors_for_virt_msix_db()`: resets a SOB, programs three consecutive monitors, writes `MON_PAY_DATA` entries for a SOB decrement payload, a re-arm payload, and an interrupt ID, writes `MON_CONFIG` with `WR_NUM=2` to request three monitor writes, and finally writes `MON_ARM` to arm the master monitor.
- Sync-manager initialization in `gaudi2_init_sm()`: writes `MON_CONFIG_0 + i * 4` for reserved completion monitors, enabling CQ behavior and, for completion monitors, LBW completion support. The KDMA completion monitor is configured with CQ only.
- Command-submission completion monitoring in `gaudi2_arm_cq_monitor()`: resets a SOB, writes CQ ID and CS-index payload data into monitor payload registers, builds the arm word with `SID`, `MASK`, `SOP`, and `SOD`, and writes it to `MON_ARM`.
- Context/user-state restore paths around `gaudi2_restore_user_sm_registers()`: use `MON_CONFIG_0`, `MON_STATUS_0`, and sync-manager block boundaries to clear and protect user monitor state across DCOREs.
- Generated wait command buffers in `gaudi2_gen_wait_cb()`: compute message-short offsets from a monitor base to `MON_PAY_ADDRL`, `MON_PAY_ADDRH`, `MON_PAY_DATA`, and `MON_ARM` for a selected monitor ID, then emit packets that configure a monitor to write a fence value when the sync condition is met.

Most consumers use the base-plus-offset convention rather than the high-index macro names directly. That makes the contiguous layout and 4-byte stride the critical control-flow contract.

## State And Persistence Behavior

The macros themselves are compile-time constants and do not store state. They map to volatile hardware state in the Gaudi2 sync-manager block.

Hardware state affected through this address range includes:

- Per-monitor payload data, retained in the sync-manager register file until overwritten or reset.
- Per-monitor arm state, which determines whether and how a monitor waits on SOB values and dispatches writes.
- Per-monitor configuration, including CQ/LBW behavior and multi-write sequencing.

This state is runtime device state, not filesystem state. It is generally reset-sensitive and context-sensitive. Driver initialization programs reserved monitors for completion and KDMA paths. Context setup and restore paths clear or protect user-available monitor state. Command-buffer generation and queue submission paths may program monitor entries repeatedly for waits, fences, and interrupt redirection.

Persistence risks are mostly hardware lifetime concerns: stale `MON_ARM` state can leave a monitor armed against the wrong SOB, stale `MON_PAY_DATA` can write an old payload when a monitor fires, and stale `MON_CONFIG` can change whether the write is interpreted as CQ/LBW/multi-write behavior. The driver mitigates this by resetting SOBs, configuring payload/address registers before arm writes, and bulk-clearing user monitor config/status state during context restoration.

## Dependencies

This generated header depends on the Gaudi2 hardware register map. It does not include other files directly in the chunk, but it is normally included alongside:

- `dcore0_sync_mngr_objs_masks.h`, which defines field shifts and masks for the register families named here.
- `gaudi2P.h`, which derives sync-manager counts and block sizes from generated register addresses, including monitor and SOB ranges.
- Gaudi2 implementation code in `gaudi2.c`, which uses `WREG32`, `RREG32`, `FIELD_PREP`, `lower_32_bits`, `upper_32_bits`, queue IDs, SOB IDs, monitor IDs, and completion queue structures.
- Common Habana Labs driver infrastructure for MMIO access, command-buffer submission, contexts, completion queues, firmware interrupt handling, and debug/reset flows.

The address values are DCORE0-specific. Other DCOREs are addressed either through corresponding generated headers/register bases or by adding the architectural `DCORE_OFFSET` where code intentionally walks the same block layout across DCORE instances.

## Integration Points

Key integration points are in `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2.c`:

- `gaudi2_arm_monitors_for_virt_msix_db()` uses `MON_PAY_DATA_0`, `MON_ARM_0`, and `MON_CONFIG_0` to build a three-monitor sequence that redirects LBW sync-object completions into HBW virtual MSI-X doorbell writes.
- `gaudi2_prepare_sm_for_virt_msix_db()` allocates specific reserved SOB and monitor IDs for decoder normal/abnormal interrupts, then delegates the actual programming to the monitor-arm helper.
- `gaudi2_init_sm()` programs reserved completion monitors by writing `MON_CONFIG` entries, then initializes global completion queue base/size registers outside this chunk.
- `gaudi2_arm_cq_monitor()` configures monitor payload and arm state for command-submission completion queue notifications.
- User sync-manager restore logic clears monitor status/config windows based on `first_available_user_mon`, `MON_CONFIG_0`, `MON_STATUS_0`, `SM_SEC_0`, and `DCORE_OFFSET`.
- Wait command-buffer generation computes offsets from a monitor MMIO base to `MON_PAY_DATA` and `MON_ARM`, so packet contents remain independent of absolute BAR placement.

The chunk also integrates with security and mmap policy indirectly. Sync-manager objects are part of the Gaudi2 block map and user-visible hardware resources, but this slice only supplies addresses; access control is enforced in driver setup, security register programming, context state clearing, and user block-mapping code elsewhere.

## Risks And Edge Cases

Register-map correctness is the central risk. A wrong address, missing index, duplicate macro, or broken 4-byte progression would route monitor writes to the wrong hardware register. Because driver code often uses `*_0 + mon_id * 4`, an incorrect base macro can corrupt every indexed access even when individual high-index defines look correct.

The chunk boundaries are easy to misread. `MON_PAY_DATA` starts before this chunk, while `MON_CONFIG` continues after it. Research or tooling that treats this chunk as a complete definition of either array would undercount or misclassify the hardware surface.

Monitor programming order matters in consumers. Payload address/data/config should be valid before `MON_ARM` is written; otherwise a monitor might fire with stale or partially configured state. The header cannot enforce that ordering.

Field width and index limits must match the masks and hardware topology. `MON_ARM_SID` is 8 bits and the local mask selects SOBs within a group, so helper code must keep SOB group and SOB mask derivation aligned with the sync-object layout. `MON_CONFIG_WR_NUM` has a small encoded width; callers such as the virtual MSI-X path rely on `"2"` meaning three writes.

Cross-DCORE reuse must preserve block stride. Code that adds `DCORE_OFFSET` assumes each DCORE sync-manager object block has an identical layout. Any per-DCORE generation drift would invalidate bulk reset/restore loops.

User-context cleanup is sensitive to first-available monitor/SOB boundaries. Clearing too little can leave stale user monitor state; clearing too much can disturb reserved completion, KDMA, decoder interrupt, or firmware-owned monitors.

Because the file is auto-generated and marked "DO NOT EDIT", hand edits are risky. The safer maintenance path is regenerating the register header from the authoritative hardware database and verifying consumers still compile.

## Test Signals

Useful validation signals include:

- Build coverage that includes Gaudi2 headers and verifies all consumed macros and mask names resolve.
- Static checks that `MON_PAY_DATA`, `MON_ARM`, and `MON_CONFIG` addresses are contiguous 4-byte arrays and align with documented counts of 2,048 monitors.
- Probe/init logs showing successful sync-manager initialization and no MMIO faults when programming reserved completion monitors.
- Command submissions completing through CQ monitors, including correct CS index payloads and no SOB timeout in completion paths.
- KDMA jobs completing through the reserved KDMA monitor after `MON_CONFIG` CQ enablement.
- Decoder normal/abnormal interrupts routed through virtual MSI-X doorbell monitor sequences, with the expected interrupt IDs written.
- Wait/fence command buffers completing under workloads that use monitor arm/payload programming.
- Context create/destroy or device-release tests showing user monitor state is cleared and protected without disturbing reserved monitor entries.
- Fault-injection or debug traces confirming monitor IDs near array boundaries, especially high `MON_PAY_DATA` indexes and later `MON_CONFIG` indexes, map to the expected MMIO addresses.

Failure signals include SOB or CQ completion timeouts, missing MSI-X interrupts after decoder/KDMA/completion events, repeated stale fence values, monitor writes to unexpected addresses, off-by-one behavior around monitor `2047`, and regressions after generated-register updates where `*_0 + id * 4` no longer matches the generated per-index macros.

### subset-b-000984: lines 36257-43543

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 36257-43543

## Scope

This chunk is the tail of the auto-generated Gaudi2 `DCORE0_SYNC_MNGR_OBJS` register-address header. It covers four contiguous register families for DCORE0 sync-manager objects:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_1733` through `_2047`, addresses `0x4111B14` to `0x4111FFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_0` through `_2047`, addresses `0x4112000` to `0x4113FFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0` through `_639`, addresses `0x4114000` to `0x41149FC`.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_PRIV_0` through `_639`, addresses `0x4115000` to `0x41159FC`.

The file is generated hardware-description data, not hand-written control logic. The address pattern is a dense 32-bit register table with 4-byte spacing between indexed entries. The chunk ends the header with `#endif /* ASIC_REG_DCORE0_SYNC_MNGR_OBJS_REGS_H_ */`.

## Purpose

The register aliases let Gaudi2 driver code program and inspect DCORE0 sync-manager monitor state without embedding numeric MMIO offsets in C logic. Sync-manager objects are used by the driver and hardware command streams for SOB/monitor based synchronization, completion-queue notification, low-bandwidth writes, and privilege/security partitioning of sync objects.

Within this chunk, the monitor config tail completes the 2048 monitor configuration register space started earlier in the file. The monitor status table provides one status register per monitor. The secure and privileged tables provide 640 per-object permission words that mark sync-manager objects as secure and/or privileged from the hardware access-control point of view.

## Important APIs, Types, And Macros

This chunk defines only preprocessor constants:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_n`: monitor configuration registers. The driver combines these addresses with masks from `dcore0_sync_mngr_objs_masks.h`, including `DCORE0_SYNC_MNGR_OBJS_MON_CONFIG_CQ_EN_MASK`, `LBW_EN_MASK`, `WR_NUM_MASK`, `MSB_SID_MASK`, and long-SOB fields.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_n`: monitor runtime status registers. Related masks include `VALID`, `PENDING`, `PROT`, and `PRIV` fields.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_n`: secure permission metadata for sync-manager objects.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_PRIV_n`: privileged permission metadata for sync-manager objects.

There are no functions, structs, enums, or storage definitions in this range. The public contract is the macro name-to-address mapping consumed by `RREG32()`, `WREG32()`, `gaudi2_memset_device_lbw()`, and packet-generation code elsewhere in the Habana Labs driver.

## Control Flow

The header itself has no runtime control flow. Its constants are pulled into Gaudi2 control paths by inclusion:

- Context/reset cleanup uses `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_0`, `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_0`, and `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0` as range anchors in `gaudi2_restore_user_sm_registers()`. The function computes an offset from `first_available_user_mon[0]`, sets user monitor statuses to the monitor `PROT` value, clears monitor configs, and repeats the same operation for other DCOREs by adding `DCORE_OFFSET`.
- Monitor programming paths write config entries as `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_0 + 4 * monitor_id`, using bit masks to enable CQ or LBW behavior and to describe write count and SOB selection.
- Diagnostic and protection paths derive the monitor-status count and block sizes from endpoint macros such as `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_2047` and `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0`, so the dense 4-byte layout is part of the driver ABI with the generated header.

## State And Persistence Behavior

These macros do not store state in host memory. They identify device MMIO registers whose values persist in Gaudi2 hardware until reset or explicit driver/firmware reprogramming.

Runtime state represented by the address ranges includes:

- Monitor configuration state: whether a monitor sends CQ completions, performs LBW writes, uses long SOB IDs, and how many payload writes are associated with the monitor.
- Monitor status state: valid/pending/protection/privilege bits for each of 2048 monitor slots.
- Secure and privileged access metadata for 640 sync-manager objects.

The state is reset-sensitive and context-sensitive. `gaudi2_restore_user_sm_registers()` deliberately clears user-accessible monitor configuration and re-protects user monitor status during context initialization or release/reset cleanup. Firmware and command submissions can also alter monitor and permission state as part of normal accelerator operation.

## Dependencies And Integration Points

This generated register map depends on the Gaudi2 ASIC register database and must match the hardware layout exactly. It is paired with `dcore0_sync_mngr_objs_masks.h`, which supplies field shifts and masks for the addresses declared here.

Important consumers include:

- `gaudi2.c` monitor setup and command-buffer generation, where monitor config/status registers are used for SOB wait/signal, CQ notification, fences, and LBW payload delivery.
- `gaudi2_restore_user_sm_registers()`, which uses this chunk's monitor status/config and `SM_SEC` boundary macros to compute reset ranges.
- `gaudi2P.h`, which derives monitor counts and sync-manager object block sizes from the first/last register macros.
- Generic Habana Labs MMIO helpers such as `RREG32`, `WREG32`, and LBW memset helpers, which turn these offsets into device register accesses through the PCI BAR/register window.

The file is under a Ceph client source snapshot path, but this content is not Ceph filesystem code. It is Linux kernel accelerator-driver hardware description for Intel/Habana Gaudi2.

## Risks And Edge Cases

The main risk is address drift. Because driver code performs arithmetic from the first macro in each family, a wrong base address, missing index, or unexpected stride would redirect bulk MMIO operations to the wrong hardware registers. This is especially important for ranges that use `SM_SEC_0` as an end boundary for monitor status/config cleanup.

The chunk starts at `MON_CONFIG_1733`, not at the start of the monitor config family. Chunk-level analysis must therefore treat this as a continuation of the earlier `MON_CONFIG_0..1732` range rather than as a separate partial device feature. The full monitor config family is 2048 entries, and this slice only contains the final 315.

Bulk operations assume all indexed entries are 32-bit and densely spaced by 4 bytes. Any future hardware generation with holes, wider registers, or nonuniform security-table layout cannot reuse these arithmetic patterns without changing the generated headers and the C logic that computes ranges.

Permission tables are security-sensitive. Incorrect `SM_SEC` or `SM_PRIV` addresses could accidentally leave sync objects writable by unprivileged contexts or mark legitimate user monitors as protected/private, causing failures in command submission, waits, completion signaling, or firmware security checks.

The monitor status reset path writes the `PROT` bit across a computed range. If `first_available_user_mon[0]` is misconfigured, the driver may either fail to reset user monitors or touch reserved/kernel monitors. The risk is compounded because later DCOREs are addressed by adding `DCORE_OFFSET` rather than by using separate generated headers for each DCORE.

## Test Signals

Useful validation signals include:

- Build coverage that includes this header through Gaudi2 driver compilation, catching missing or renamed generated macros.
- Register-map sanity checks showing `MON_STATUS_2047 - MON_STATUS_0 + 4` equals `2048 * 4`, `SM_SEC_639 - SM_SEC_0 + 4` equals `640 * 4`, and `SM_PRIV_639 - SM_PRIV_0 + 4` equals `640 * 4`.
- Context creation/release paths complete without monitor-reset MMIO faults and leave user monitor statuses protected while monitor configs are zeroed.
- Generated wait/signal command buffers correctly program monitor config entries for CQ and LBW completions and observe expected SOB/monitor completion behavior.
- Security tests confirm privileged and secure sync-manager objects are inaccessible from user contexts while allowed user sync objects remain usable.
- Fault-injection or debug traces show monitor status `VALID`, `PENDING`, `PROT`, and `PRIV` bits changing consistently with armed monitor activity and cleanup.
