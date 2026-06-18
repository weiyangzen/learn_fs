# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_offset.h

## Purpose

`smuio_13_0_6_offset.h` is a generated AMDGPU SMUIO 13.0.6 register-address header. It exports `reg*` offsets and `*_BASE_IDX` selector values for reset, TSC, software timer, miscellaneous, two CKSVII2C controller instances, power-management, ROM, ROM software-command payload, and GPIO blocks. It contains no executable logic and is intended to be used with `smuio_13_0_6_sh_mask.h`.

The visible hardware base comments place reset at `0x5a300`, TSC at `0x5a8a0`, software timer at `0x5ac70`, misc at `0x5a000`, I2C at `0x5a100`, ROM at `0x5a380`, and GPIO at `0x5a500`.

## Important APIs, Types, And Macros

There are no C functions, types, or variables. The API is the macro set:

- `regNAME`: generated register offset.
- `regNAME_BASE_IDX`: generated base-index selector for SOC15 helpers.

Important groups include:

- Reset and halt: `regSMUIO_MP_RESET_INTR`, `regSMUIO_SOC_HALT`.
- TSC/power-good: `regPWROK_REFCLK_GAP_CYCLES`, `regGOLDEN_TSC_INCREMENT_*`, `regGOLDEN_TSC_COUNT_*`, `regSOC_GOLDEN_TSC_SHADOW_*`, `regSOC_GAP_PWROK`.
- Software timer: display timer control/debug pairs, display timer global control, and `regPWR_IH_CONTROL`. Unlike 13.0.3, this offset header does not list `regPWR_VIRT_RESET_REQ` in the swtimer block.
- Misc: `regSMUIO_MCM_CONFIG`, `regIP_DISCOVERY_VERSION`, and `regSCRATCH_REGISTER0` through `regSCRATCH_REGISTER7`.
- I2C: full CKSVII2C and CKSVII2C1 register sets from control/target/data/timing/interrupt/FIFO/enable/status through component parameter/version/type registers, plus `regSMUIO_PWRMGT`.
- ROM: `regROM_CNTL`, `regPAGE_MIRROR_CNTL`, `regROM_STATUS`, `regCGTT_ROM_CLK_CTRL0`, `regROM_INDEX`, `regROM_DATA`, `regROM_START`, `regROM_SW_CNTL`, `regROM_SW_STATUS`, `regROM_SW_COMMAND`, and `regROM_SW_DATA_1` through `regROM_SW_DATA_64`.
- GPIO: `regSMU_GPIOPAD_*`, `regDFT_PINSTRAPS`, interrupt status/ack/enable/type/polarity, PCC selection, S0/S1/SCHMEN/SCL/SDA, interrupt select/status, `regSMIO_INDEX`, VID SMIO controls, `regOPEN_DRAIN_SELECT`, and `regSMIO_ENABLE`.

Most `*_BASE_IDX` values are `0` for reset, misc MCM, I2C, ROM, and GPIO, while TSC, swtimer, IP discovery, and scratch registers use base index `1`.

## Control Flow And Data Flow

The header has no runtime control flow. Consumers use it as address data:

1. Include this file and `smuio_13_0_6_sh_mask.h`.
2. Select offsets such as `regROM_INDEX`, `regROM_DATA`, or `regSMUIO_MCM_CONFIG`.
3. Pass them to SOC15 helpers such as `SOC15_REG_OFFSET()` or MMIO read/write helpers.
4. Decode or compose field values with the matching mask header.

Direct consumers visible in the tree include `amdgpu/smuio_v13_0_6.c`, which exposes `regROM_INDEX` and `regROM_DATA` through `amdgpu_smuio_funcs`, and `amdgpu/gfx_v11_0.c`, which includes the 13.0.6 SMUIO offset and mask headers alongside GFX 11.0 register headers. The latter makes SMUIO 13.0.6 register addresses available to GFX 11.0 flows that need shared timing or SMUIO state.

## State And Persistence Behavior

The file itself has no state. The addressed registers hold hardware state, including:

- Reset/halt and power-good/TSC state.
- Scratch registers and IP discovery version.
- Two I2C controller instances with timing, FIFO, interrupt, enable, and component-identification state.
- ROM index/data, SPI timing/control, busy status, page mirror, software-command payload and completion state.
- GPIO pad, strap, interrupt, PCC, open-drain, and SMIO state.

Register state persists in hardware across ordinary software reads/writes and may be reinitialized by reset, firmware, strap sampling, or power transitions. Base-index values are part of the persistent addressing contract used by SOC15 helpers.

## Dependencies And Integration Points

This file depends only on the C preprocessor. Practical integration points are:

- `smuio_13_0_6_sh_mask.h` for field masks and shifts.
- `amdgpu/smuio_v13_0_6.c`, which uses `regROM_INDEX` and `regROM_DATA`.
- `amdgpu/gfx_v11_0.c`, which includes the SMUIO 13.0.6 generated headers.
- AMDGPU SOC15 access helpers and the `amdgpu_smuio_funcs` abstraction.

The register set overlaps heavily with 13.0.2 but uses different base-index conventions and has its own generated address list. Consumers should not assume offsets from another SMUIO minor version are interchangeable.

## Risks And Edge Cases

- A wrong offset or base index can make a valid register name access the wrong SMUIO aperture. This is especially relevant because 13.0.3 uses different base-index values for similar blocks.
- The ROM data window contains many sequential software payload registers. Generation drift in the sequence can corrupt ROM command payloads or reads.
- I2C0 and I2C1 blocks are parallel and easy to confuse; using the wrong controller offset may program an inactive or board-specific bus.
- Address headers do not encode access semantics. ROM busy/done, GPIO interrupt ack, timer ack, and reset/halt registers may have side effects on read or write.
- `regPWR_DISP_TIMER_CONTROL` and `regROM_SW_DATA_50` both have numeric offset `0x011d` but belong to different base-index/address blocks. The base index and block context are therefore essential.
- Generated headers are not self-testing; semantic errors require hardware testing or generator/database comparison.

## Test Signals

- Compile AMDGPU configurations that include `smuio_v13_0_6.c` and `gfx_v11_0.c`.
- Verify VBIOS/ROM reads through the SMUIO function table on matching 13.0.6 devices.
- Run GFX 11.0 initialization, suspend/resume, and reset tests that include SMUIO 13.0.6 headers.
- Compare SMUIO register dumps against expected offsets and base indices for reset, TSC, I2C, ROM, and GPIO blocks.
- Exercise I2C and GPIO paths on boards where those SMUIO facilities are routed and enabled.
- Regenerate from AMD register sources and diff offsets/base indices against this header.
