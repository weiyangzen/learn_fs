# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_offset.h

Purpose: generated AMDGPU ASIC register-offset header for the PWR 10.0 block. It gives C preprocessor names to the PWR_MISC_CNTL_STATUS register address metadata so driver code can access power-management status without embedding the raw register index.

Important APIs/types/functions: this header has no C functions or types. Its public interface is two macros: `mmPWR_MISC_CNTL_STATUS` with register index `0x0183`, and `mmPWR_MISC_CNTL_STATUS_BASE_IDX` with value `0`. The include guard is `_pwr_10_0_OFFSET_HEADER`. In AMDGPU register code, the `mm*` symbol is normally paired with SOC15-style helpers and the `_BASE_IDX` value supplies the register aperture/base selector expected by generated register-access tables.

Control flow: none is implemented in this file. Compile-time inclusion only makes the register address macro available. Runtime control flow occurs in consumers that read `mmPWR_MISC_CNTL_STATUS`, usually together with the bit definitions from `pwr_10_0_sh_mask.h`, to inspect graphics power-gating and GFXOFF status.

State and persistence behavior: the header itself is stateless and has no persistence. The named register is hardware state owned by the GPU power block. Its value may change as firmware, the runlist controller, or power-management logic enters and exits clock/power-gated graphics states, so callers must treat reads as snapshots rather than cached software state.

Dependencies: depends only on the C preprocessor. It is semantically coupled to `pwr_10_0_sh_mask.h`, which describes the fields inside the register named here, and to the AMDGPU generated register-access conventions (`mm*`, `_BASE_IDX`, and `REG_GET_FIELD`/`SOC15_REG_OFFSET` style consumers). It intentionally carries no Linux kernel includes.

Integration points: this file sits under `drivers/gpu/drm/amd/include/asic_reg/pwr/` and is included by AMDGPU ASIC support code that needs PWR 10.0 status registers. The single offset is meaningful only when matched to the correct ASIC generation and block instance; including it from the wrong generation would silently point status reads at the wrong hardware address.

Risks: incorrect offset or base-index values can break GFXOFF/CGPG status detection, causing the driver to report the wrong power state, make bad power-transition decisions, or misdiagnose firmware behavior. Because the file is generated-style and tiny, manual edits are high risk relative to their apparent simplicity.

Test signals: compile coverage should catch missing macro names. Useful runtime signals include successful AMDGPU initialization on PWR 10.0 hardware, sane reads from `PWR_MISC_CNTL_STATUS`, correct GFXOFF enter/exit reporting, and absence of timeouts or false status transitions in power-management debug and suspend/resume paths.
