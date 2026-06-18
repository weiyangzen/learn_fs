# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_sh_mask.h

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
