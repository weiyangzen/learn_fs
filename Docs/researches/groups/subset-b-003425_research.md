# subset-b-003425 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_sh_mask.h

### Purpose
`smuio_13_0_6_sh_mask.h` is the generated bitfield description header for SMUIO IP version 13.0.6. It exposes register-field shift constants and masks for the AMDGPU SMUIO register block so driver code can extract, compose, and update fields through common register helpers such as `REG_GET_FIELD()` and related SOC15 access macros.

### Important APIs, Types, And Functions
This header defines no C functions or data types; its API is the macro namespace. The file is protected by `_smuio_13_0_6_SH_MASK_HEADER` and contains pairs of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. Major covered register groups are reset and halt controls, TSC/golden counter fields, display timer and power interrupt-handler fields, MCM/package configuration, scratch registers, two CKSVII2C controller instances, ROM access/control fields, GPIO pad and interrupt fields, SMIO selection/control fields, and power-management clock-gating fields.

### Control Flow
There is no runtime control flow in the header. Its logical flow is source-generation order by address block: reset, TSC, software timer, miscellaneous SMUIO, I2C, ROM, GPIO, and SMIO. Runtime control appears only in consumers: for example `amdgpu/smuio_v13_0_6.c` includes this header with the matching offset header and returns `SOC15_REG_OFFSET(SMUIO, 0, regROM_INDEX)` and `regROM_DATA` through `amdgpu_smuio_funcs`; `amdgpu/gfx_v11_0.c` includes the same SMUIO 13.0.6 register descriptions alongside GFX 11 register tables.

### State, Persistence, And Dependencies
The header has no mutable software state and persists nothing. It describes hardware state encoded in SMUIO registers. Correct use depends on the matching `smuio_13_0_6_offset.h` offset definitions, AMDGPU register access helpers in the SOC15 path, and the field-extraction/update macros that assume the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention. The mask values use 32-bit register layouts, typically with `L` suffixes that are consumed as integer constants by kernel C code.

### Integration Points
The most direct integration points are `amdgpu/smuio_v13_0_6.c` and `amdgpu/gfx_v11_0.c`. The exported names line up with generated offset names such as `regROM_INDEX`, `regROM_DATA`, `regSMUIO_MCM_CONFIG`, CKSVII2C registers, GPIO registers, and ROM software-command/data registers. The MCM fields match driver topology reads in nearby SMUIO implementations: fields such as `DIE_ID`, `SOCKET_ID`, `PKG_TYPE`, `PKG_SUBTYPE`, `CONSOLE_K`, and `CONSOLE_A` are intended for package/topology identification. The ROM fields are consumed indirectly by the SMUIO function table for VBIOS/ROM access. I2C and GPIO fields are available to low-level SMUIO or platform code that needs to configure sideband controllers and pad interrupts.

### Risks
The main risk is register-schema drift. If a mask or shift does not match the 13.0.6 hardware table, generic helpers will silently read or write the wrong bits. Cross-version similarity raises copy/paste risk: the file resembles other SMUIO versions but has version-specific details such as `SMUIO_MCM_CONFIG` bit positions, CKSVII2C stuck-recovery fields, ROM data-register span, and GPIO interrupt mask width. Some register comments have no field macros, indicating read-clear or whole-register accesses may be intended elsewhere; adding consumers must not invent field semantics from names alone. Because these macros can influence reset, watchdog, ROM, I2C, and GPIO behavior, bad definitions can cause boot failures, incorrect topology reporting, lost interrupts, or inaccessible ROM reads.

### Test Signals
Useful validation signals are successful kernel compilation with the matching offset header, no macro redefinition warnings when included with other generated headers, working `smuio_v13_0_6_funcs` ROM index/data offset callbacks, correct VBIOS/ROM reads on 13.0.6 hardware, and topology/package values matching expected board data when consumers use `REG_GET_FIELD()` on `SMUIO_MCM_CONFIG`. Hardware smoke tests should include display-timer interrupt behavior if enabled, CKSVII2C status/interrupt handling, GPIO interrupt acknowledge paths, and watchdog/reset paths only in controlled environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_14_0_2_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_14_0_2_offset.h

### Purpose
`smuio_14_0_2_offset.h` is the generated register-offset map for SMUIO IP version 14.0.2. It gives AMDGPU code the per-register numeric offsets and base-index selectors needed by `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, and related SOC15 register-access helpers.

### Important APIs, Types, And Functions
This header defines no functions or C types. Its API consists of `reg<REGISTER>` and `reg<REGISTER>_BASE_IDX` macros under the `_smuio_14_0_2_OFFSET_HEADER` include guard. The file maps address blocks for TSC (`regGOLDEN_TSC_*`, `regSOC_GAP_PWROK`), software timers and virtual reset (`regPWR_VIRT_RESET_REQ`, display timers, `regPWR_IH_CONTROL`), miscellaneous SMUIO (`regSMUIO_MCM_CONFIG`, scratch registers), two CKSVII2C controllers, `regSMUIO_PWRMGT`, ROM access/control (`regROM_INDEX`, `regROM_DATA`, `regROM_SW_DATA_1` through `regROM_SW_DATA_64`), GPIO pad/interrupt registers, and SMIO control registers.

### Control Flow
There is no executable control flow. Consumers supply the macros to register-access helpers. In `amdgpu/smuio_v14_0_2.c`, `smuio_v14_0_2_get_rom_index_offset()` and `smuio_v14_0_2_get_rom_data_offset()` return `SOC15_REG_OFFSET(SMUIO, 0, regROM_INDEX)` and `regROM_DATA`. The same C file reads `regGOLDEN_TSC_COUNT_UPPER` and `regGOLDEN_TSC_COUNT_LOWER` with `RREG32_SOC15()` inside a preemption-disabled double-read sequence to construct a coherent 64-bit GPU clock counter.

### State, Persistence, And Dependencies
The header has no software state. It is a static description of persistent hardware register locations for the 14.0.2 SMUIO block. It depends on the matching `smuio_14_0_2_sh_mask.h` field definitions for field-level operations and on SOC15 base-address logic to interpret each `_BASE_IDX`. The address-block comments document hardware base addresses, while the macros store register-relative offsets and base-index selectors. Base-index differences matter: for example `regSMUIO_MCM_CONFIG` uses base index `0`, TSC counters use base index `1`, and the I2C/ROM/GPIO blocks mostly use base index `0`.

### Integration Points
The direct integration point is `amdgpu/smuio_v14_0_2.c`, whose function table exposes ROM offset callbacks and `get_gpu_clock_counter`. The golden TSC offsets support driver timing/profiling paths that call the SMUIO clock-counter hook. ROM offsets support VBIOS/ROM access through common AMDGPU SMUIO infrastructure. The virtual reset, I2C, GPIO, and power-management offsets are available to other SMUIO or platform code when this IP version is selected. The register names are intentionally parallel to adjacent generated headers such as 14.0.2 shift/mask and 15.x offset files, allowing version-specific files to plug into common AMDGPU source patterns.

### Risks
The primary risk is an incorrect offset or base index. A wrong `regGOLDEN_TSC_COUNT_*` value can make clock-counter reads non-monotonic or read unrelated registers. Wrong ROM offsets can break VBIOS access. Wrong base indices are especially subtle because the offset number may look plausible while resolving through the wrong SOC15 aperture. The file also includes dense repeated ranges, especially CKSVII2C0/1 and `regROM_SW_DATA_1` through `regROM_SW_DATA_64`, where an off-by-one generation error would be easy to miss in code review. Because this is a generated hardware contract, manual edits should be avoided unless verified against the authoritative register database.

### Test Signals
Useful signals include successful AMDGPU build with `smuio_v14_0_2.c`, correct expansion of `SOC15_REG_OFFSET()` for `regROM_INDEX` and `regROM_DATA`, successful VBIOS/ROM reads on 14.0.2 hardware, and a monotonic `get_gpu_clock_counter` across rollover of the lower 32 bits. Additional hardware validation should check that `regSMUIO_MCM_CONFIG` reports expected package fields when used with the matching shift/mask header, that CKSVII2C register blocks are spaced as expected (`0x0040` and `0x0080` starts), and that GPIO interrupt/status registers behave at the documented offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_14_0_2_offset.h -->
