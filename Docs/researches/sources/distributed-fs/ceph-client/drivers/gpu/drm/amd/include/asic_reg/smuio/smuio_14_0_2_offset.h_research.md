# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_14_0_2_offset.h

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
