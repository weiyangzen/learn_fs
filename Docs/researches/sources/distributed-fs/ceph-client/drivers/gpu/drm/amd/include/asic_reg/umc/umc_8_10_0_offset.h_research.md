# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_offset.h

## Purpose

`umc_8_10_0_offset.h` is a generated AMDGPU register-offset header for the UMC 8.10.0 memory-controller block. It exports symbolic offsets and base-index selectors for a small set of GPU memory error reporting registers. It contains no executable code, types, or storage; its public surface is the `reg*` macro namespace.

## Important APIs, Types, And Macros

The header defines `regUMCCH0_0_GeccErrCntSel`, `regUMCCH0_0_GeccErrCnt`, `regMCA_UMC_UMC0_MCUMC_STATUST0`, `regMCA_UMC_UMC0_MCUMC_ADDRT0`, and `regUMCCH0_0_GeccCtrl`, with matching `_BASE_IDX` macros. The offsets identify the GECC error counter selector, GECC error counter, MCA-style UMC status/address registers, and a GECC control register. All base indexes are `2`, unlike older UMC 8.7.0 and newer UMC 8.14.0 headers in this work item, so consumers must not assume the same register aperture across generations.

## Control Flow And Data Flow

There is no local control flow. Driver logic includes this file, combines one of these offsets with a register access helper, and uses matching masks from `umc_8_10_0_sh_mask.h` to select counters, read corrected/uncorrected error counts, decode MCA status, read the fault address, or enable fatal handling for uncorrectable errors.

## State And Persistence Behavior

The macros store no software state. They name persistent hardware registers whose values are maintained by the UMC/MCA hardware until read, cleared, reprogrammed, or reset. The represented state includes ECC/poison counter configuration, accumulated error counts, MCA status validity/overflow bits, error-address state, and fatal-error enablement.

## Dependencies And Integration Points

The file depends only on the C preprocessor. It is intended to be paired with `umc_8_10_0_sh_mask.h` and with AMDGPU RAS, UMC, memory-controller, and GPU reset paths that poll or clear memory error state.

## Risks And Test Signals

Risks are ABI-style: using these offsets with another UMC generation can read the wrong aperture, corrupt GECC control, or misreport RAS errors. The key tests are compile coverage for ASIC code that includes UMC 8.10.0 headers, RAS injection or fault-reporting tests that verify corrected/uncorrected counts and MCA address decoding, and reset/suspend-resume tests that confirm error registers are not decoded through the wrong base index.
