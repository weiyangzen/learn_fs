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
