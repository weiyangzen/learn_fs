# Research: subset-b-002862

Grouped research for AMD MP register definition headers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/`. These files are generated-style C preprocessor headers: they export register offsets, base-index selectors, field shifts, and field masks for ASIC-specific MP/SMU register blocks. They do not contain executable code, runtime control flow, allocation, or persistence logic.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_sh_mask.h

### Purpose

`mp_12_0_0_sh_mask.h` defines shift and mask macros for MP 12.0.0 SMU/MP message, interrupt, and firmware flag registers. It complements an offset header for the same ASIC generation: callers use register address macros from an offset header and these `__SHIFT`/`_MASK` macros to pack or extract fields in 32-bit MMIO/SMN register values.

The header covers four documented address blocks: `mp_SmuMp0_SmnDec`, `mp_SmuMp1_SmnDec`, `mp_SmuMp0Pub_CruDec`, and `mp_SmuMp1Pub_CruDec`. Most mailbox registers are full-width payload words, while interrupt and firmware-control registers expose smaller bitfields.

### Important APIs, Types, And Macros

This file exports only preprocessor constants; there are no C types, functions, inline helpers, or storage definitions.

Important macro families:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`: each has `__CONTENT__SHIFT` set to `0x0` and `__CONTENT_MASK` set to `0xFFFFFFFFL`.
- `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_103`: same full-width `CONTENT` field pattern for the MP1 SMN block.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT`: define `CREDIT_VALUE` in bits 1:0 (`0x00000003L`) and `CLIENT_ID` at shift `0x10` with mask `0x00FF0000L`.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT`: define an 8-bit software interrupt `ID` at shift `0x0` and a `VALID` bit at shift `0x8`.
- Public CRU interrupt macros `MP0_IH_CREDIT`, `MP0_IH_SW_INT`, `MP0_IH_SW_INT_CTRL`, `MP1_IH_CREDIT`, `MP1_IH_SW_INT`, and `MP1_IH_SW_INT_CTRL`: mirror credit/software-interrupt layouts and add control fields `INT_MASK` bit 0 and `INT_ACK` bit 8.
- `MP1_SMN_FPS_CNT` and `MP1_FPS_CNT`: expose a full-width `COUNT` field.
- `MP1_FIRMWARE_FLAGS`: defines `INTERRUPTS_ENABLED` in bit 0 and the remaining bits as `RESERVED`.
- `MP1_C2PMSG_0` through `MP1_C2PMSG_103`, plus `MP1_P2CMSG_0` through `MP1_P2CMSG_3`: public MP1 message registers with full-width `CONTENT`.
- `MP1_P2CMSG_INTEN` and `MP1_P2CMSG_INTSTS`: expose four low interrupt enable/status bits.

### Control Flow

There is no executable control flow. The only compile-time flow is the include guard `_mp_12_0_0_SH_MASK_HEADER`, which prevents duplicate macro definitions within one translation unit.

Operational control flow is supplied by AMDGPU/SMU code that includes this header. Typical use is:

1. Read or construct a 32-bit register value.
2. Use a field `MASK` and `SHIFT` macro to isolate or position a value.
3. Write the value through the driver register access path for the matching MP 12.0.0 register offset.

### State And Persistence Behavior

The header owns no runtime state and performs no persistence. It describes hardware-backed register state: mailbox registers can carry host-to-firmware (`C2PMSG`) and firmware-to-host (`P2CMSG`) payloads, interrupt registers carry pending/valid/ack bits, and firmware flags expose interrupt enable state. Any persistence or volatility is entirely in the device registers and firmware protocol, not in this file.

### Dependencies And Integration Points

The file depends only on the C preprocessor. Its integration contract is naming consistency with AMD register access code and the matching MP 12.0.0 offset definitions. It is consumed by AMDGPU power-management, SMU, interrupt, and firmware message paths that need stable field encodings for MP registers.

Important integration points include:

- Register offset headers in the same `asic_reg/mp/` family.
- AMDGPU SMN/MMIO helpers that combine offset, base index, mask, and shift macros.
- Firmware mailbox protocols that assign semantic meanings to individual `C2PMSG` and `P2CMSG` registers.
- Interrupt handling code that uses `IH_SW_INT`, `IH_SW_INT_CTRL`, and credit fields.

### Risks And Maintenance Notes

The highest risk is ASIC-generation mismatch. MP 12.0.0 field macros should not be mixed with MP 13.x offsets unless the consuming code deliberately proves layout compatibility. Full-width `CONTENT` masks are easy to use, but interrupt control and firmware flag fields are small and can corrupt adjacent bits if a caller shifts or masks incorrectly.

The `L` suffix on masks means the literal type can vary with C data model; driver code should continue to use fixed-width register value types when combining these constants. Generated formatting also makes broad manual edits risky: a single off-by-one register name or copied mask can silently direct firmware traffic to the wrong mailbox.

### Test Signals

Useful validation is mostly compile-time and hardware/driver level:

- Build coverage for AMDGPU code paths that include MP 12.0.0 register headers.
- Preprocessor or static checks that each `__SHIFT` has the expected companion `_MASK`.
- Driver tests or bring-up logs showing SMU mailbox commands complete on MP 12.0.0 hardware.
- Interrupt-path tests that verify software interrupt `VALID`, `INT_ACK`, and credit handling still works.
- Register-dump comparisons against AMD-generated reference headers or ASIC documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_offset.h

### Purpose

`mp_13_0_0_offset.h` defines MP 13.0.0 register offset macros and matching `_BASE_IDX` selectors. It is the address-side companion to MP 13.0.0 shift/mask headers: callers use these `reg...` constants to identify hardware registers and use separate field macros to interpret or construct register values.

The header maps MP0 and MP1 SMN-decoded mailbox/interrupt registers, MP1 public firmware flag registers, and MPIO public firmware flags for ASIC generation 13.0.0.

### Important APIs, Types, And Macros

This file exports preprocessor constants only; it has no functions, structs, enums, or data objects.

Important macro families:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_103`: contiguous MP0 SMN offsets from `0x0060` through `0x00a7`.
- `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL`: MP0 SMN interrupt helper registers at `0x00c1` through `0x00c3`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_127`: contiguous MP1 SMN offsets from `0x0260` through `0x02bf`, giving MP1 a larger mailbox range than MP0 in this header.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_PUB_CTRL`: MP1 SMN interrupt/count/control registers from `0x02c1` through `0x02c5`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31`, with no `EXT_SCRATCH9` definition visible in the sequence: scratch offsets run from `0x0340` through `0x035f` with that documented gap.
- `regMP1_FIRMWARE_FLAGS` and `regMPIO_FIRMWARE_FLAGS`: public CRU firmware flag registers, both at address `0xbee009` but in different address blocks.
- Every `reg...` offset has a corresponding `reg..._BASE_IDX` macro set to `0`.

### Control Flow

There is no runtime control flow. The only structural flow is the `_mp_13_0_0_OFFSET_HEADER` include guard.

At runtime, consuming code supplies control flow by selecting a register macro, resolving its base index through AMDGPU register access helpers, and reading or writing the mapped hardware register.

### State And Persistence Behavior

The header is stateless. It names device register locations whose contents are maintained by the GPU, SMU firmware, and interrupt hardware. Scratch registers and firmware flags may persist for the lifetime of a device/firmware session, but the header does not allocate, cache, or synchronize that state.

### Dependencies And Integration Points

The only direct dependency is the C preprocessor. Integration depends on consistency with:

- `mp_13_0_0_sh_mask.h` for field definitions.
- AMDGPU SMU/MP register access macros that expect `reg...` and `reg..._BASE_IDX` naming.
- Firmware command paths using `C2PMSG` mailboxes.
- Interrupt handlers using `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL`.
- Firmware status/control code using `FIRMWARE_FLAGS`, `MP1_SMN_PUB_CTRL`, and extended scratch registers.

The `regMP1_FIRMWARE_FLAGS` and `regMPIO_FIRMWARE_FLAGS` address reuse at `0xbee009` is safe only because the address blocks differ. Code that flattens register addresses without preserving address block context could confuse them.

### Risks And Maintenance Notes

Register offsets are ABI-like hardware constants. A wrong value can cause MMIO/SMN accesses to hit an unrelated register, hang firmware communication, lose interrupts, or corrupt scratch/control state. The most important variant-specific risk is confusing MP 13.0.0 with MP 13.0.2: this header includes `regMP1_SMN_PUB_CTRL`, extended scratch registers through `EXT_SCRATCH31`, and `regMPIO_FIRMWARE_FLAGS`, while the MP 13.0.2 offset header in this work item is narrower.

Because all `_BASE_IDX` values are `0`, any future multi-base variant would require careful generator and consumer updates. The absent `EXT_SCRATCH9` macro should be treated as intentional unless confirmed against upstream generation inputs.

### Test Signals

Useful signals include:

- Successful AMDGPU compilation for MP 13.0.0 targets.
- Static comparison of generated offsets against upstream AMD headers.
- SMU mailbox command tests that exercise MP0 and MP1 `C2PMSG` ranges.
- Runtime register access traces confirming MP1 scratch and firmware flag reads use the correct address block.
- Interrupt smoke tests validating `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL` offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_sh_mask.h

### Purpose

`mp_13_0_0_sh_mask.h` defines field shifts and masks for MP 13.0.0 registers. It is used with `mp_13_0_0_offset.h` so AMDGPU code can address a register and then safely isolate, set, or preserve individual fields in that register value.

The header covers MP0 and MP1 SMN-decoded mailbox/interrupt registers, MP1 SMN scratch/control registers, MP1 public firmware flags, and MPIO public firmware flags.

### Important APIs, Types, And Macros

This header exports preprocessor constants only.

Important macro families:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`: full-width `CONTENT` fields with shift `0x0` and mask `0xFFFFFFFFL`.
- `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_127`: full-width MP1 SMN mailbox payload fields.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT`: `CREDIT_VALUE` in low two bits and `CLIENT_ID` in bits 23:16.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT`: 8-bit `ID` plus `VALID` bit at bit 8.
- `MP0_SMN_IH_SW_INT_CTRL` and `MP1_SMN_IH_SW_INT_CTRL`: `INT_MASK` bit 0 and `INT_ACK` bit 8.
- `MP1_SMN_FPS_CNT`: full-width `COUNT`.
- `MP1_SMN_PUB_CTRL`: `LX3_RESET` bit 0, a sensitive control field for MP1 public control.
- `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH31`, with no scratch 9 macro: full-width `DATA` fields.
- `MP1_FIRMWARE_FLAGS` and `MPIO_FIRMWARE_FLAGS`: `INTERRUPTS_ENABLED` bit 0 and `RESERVED` bits 31:1.

### Control Flow

There is no executable flow. The include guard `_mp_13_0_0_SH_MASK_HEADER` is the only compile-time control structure. Runtime sequencing is owned by caller code that performs read-modify-write operations or extracts fields after reading hardware registers.

### State And Persistence Behavior

The header does not store state. It describes bit layouts of hardware state held by MP/SMU registers. Mailbox `CONTENT` fields carry transient protocol payloads, interrupt fields reflect interrupt routing/status, scratch registers provide firmware/driver communication storage, and firmware flags report or control firmware interrupt state. Durability is limited to the device/firmware behavior of those registers.

### Dependencies And Integration Points

The file depends on the C preprocessor and on consumers following AMD's register macro naming convention. It integrates with:

- `mp_13_0_0_offset.h`, whose register names match these field-prefix names.
- AMDGPU SMU mailbox routines that consume `C2PMSG` content fields.
- Interrupt handling paths that manipulate `IH_SW_INT`, `IH_SW_INT_CTRL`, and credit fields.
- Firmware initialization/reset code that may use `MP1_SMN_PUB_CTRL__LX3_RESET_MASK`.
- Diagnostics or firmware protocol code that reads/writes MP1 extended scratch registers.
- MPIO firmware code that distinguishes `MPIO_FIRMWARE_FLAGS` from `MP1_FIRMWARE_FLAGS`.

### Risks And Maintenance Notes

The main correctness risk is using the correct field set for the correct ASIC offset set. The MP 13.0.0 mask header includes `MP1_SMN_PUB_CTRL`, scratch registers through `EXT_SCRATCH31`, and `MPIO_FIRMWARE_FLAGS`; those fields should not be assumed present on every MP 13 variant.

Read-modify-write callers must use masks to preserve reserved bits, especially in `FIRMWARE_FLAGS` and `PUB_CTRL`. `LX3_RESET` is particularly risky because an unintended write could reset MP1 microcontroller state. Full-width `CONTENT` and `DATA` fields do not protect callers from protocol-level mistakes: writing the wrong mailbox or scratch register can still break SMU firmware sequencing.

### Test Signals

Relevant test signals include:

- Compile coverage for all MP 13.0.0 consumers.
- Static generated-header comparison confirming every offset register has matching field macros.
- Hardware mailbox tests that validate `C2PMSG` command/response behavior.
- Interrupt tests covering `VALID`, `INT_ACK`, and credit handling.
- Firmware reset/scratch diagnostics that verify `MP1_SMN_PUB_CTRL` and extended scratch fields are accessed only on supported ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_2_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_2_offset.h

### Purpose

`mp_13_0_2_offset.h` defines register offsets and `_BASE_IDX` selectors for MP 13.0.2. It is an address map for AMDGPU MP/SMU code and is intended to be paired with generation-compatible field mask headers.

The file covers MP0 SMN mailboxes and interrupts, MP1 public firmware flags, MP1 SMN mailboxes and interrupts, MP1 FPS count, and a small MP1 extended scratch range.

### Important APIs, Types, And Macros

This file exports only preprocessor constants.

Important macro families:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_127`: contiguous MP0 SMN mailbox offsets from `0x0060` through `0x00bf`.
- `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL`: MP0 SMN interrupt helper offsets at `0x00c1` through `0x00c3`.
- `regMP1_FIRMWARE_FLAGS`: public MP1 firmware flag register at `0xbee009`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_103`: MP1 SMN mailbox offsets from `0x0260` through `0x02a7`.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, and `regMP1_SMN_FPS_CNT`: MP1 SMN interrupt/count offsets from `0x02c1` through `0x02c4`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH7`: eight MP1 scratch offsets from `0x0340` through `0x0347`.
- Every register offset has a matching `_BASE_IDX` macro set to `0`.

Compared with `mp_13_0_0_offset.h`, MP 13.0.2 has a wider MP0 mailbox range through `C2PMSG_127`, a narrower MP1 mailbox range through `C2PMSG_103`, only scratch registers 0-7, no `regMP1_SMN_PUB_CTRL`, and no `regMPIO_FIRMWARE_FLAGS`.

### Control Flow

There is no runtime control flow. The include guard `_mp_13_0_2_OFFSET_HEADER` only prevents duplicate inclusion. Runtime behavior is controlled by callers that use these constants in register read/write operations.

### State And Persistence Behavior

The header is stateless and persistent only as source code. It names hardware registers whose contents are volatile or firmware-owned. Mailbox offsets identify command/status payload registers, interrupt offsets identify hardware interrupt coordination state, and scratch offsets identify firmware/driver communication storage. This file does not cache or synchronize any of that state.

### Dependencies And Integration Points

The file has no include dependencies. It integrates with:

- MP 13.0.2-compatible field mask headers and AMDGPU register access helpers.
- SMU command submission paths that choose MP0 or MP1 `C2PMSG` registers.
- Interrupt handling paths using `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL`.
- Firmware status code reading `regMP1_FIRMWARE_FLAGS`.
- Firmware/diagnostic code using the limited `EXT_SCRATCH0` to `EXT_SCRATCH7` range.

The register block comments are part of the integration contract: `regMP1_FIRMWARE_FLAGS` uses a public CRU block address, while `regMP1_SMN_*` names use SMN-decoded offsets.

### Risks And Maintenance Notes

The largest risk is copying assumptions from MP 13.0.0. Code using `regMP1_SMN_PUB_CTRL`, `regMPIO_FIRMWARE_FLAGS`, MP1 `C2PMSG_104`-`127`, or scratch registers above 7 must not be enabled merely because a GPU is MP 13.x. Conversely, MP0 mailboxes extend to `C2PMSG_127` in this file, unlike the MP0 range in `mp_13_0_0_offset.h`.

All `_BASE_IDX` values are currently zero, so consumers may have implicit single-base assumptions. If generated data changes, those paths need explicit review. As with all register maps, mistakes are high impact because bad offsets can hit unrelated hardware registers.

### Test Signals

Useful validation includes:

- Compile coverage for MP 13.0.2 ASIC support.
- Static comparison against AMD-generated MP 13.0.2 register references.
- Runtime SMU mailbox tests that cover the MP0 `C2PMSG_127` upper range and the MP1 `C2PMSG_103` boundary.
- Firmware flag reads from the MP1 public CRU block.
- Negative or guarded tests ensuring unavailable MP 13.0.0-only registers are not referenced for MP 13.0.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_2_offset.h -->
