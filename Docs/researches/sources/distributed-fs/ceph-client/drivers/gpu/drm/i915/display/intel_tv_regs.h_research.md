# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv_regs.h

Purpose: defines the integrated TV encoder register map used by `intel_tv.c`. It covers encoder control, DAC sense/control, color-space conversion, color knobs/levels, horizontal and vertical timing, subcarrier DDA, window placement, scaling filters, closed-caption fields, and filter coefficient tables.

Important definitions: `TV_CTL` contains enable, pipe select, output type, oversample, progressive, PAL burst, test mode, and fuse-state bits. `TV_DAC` contains state-change, sense, DAC voltage, and override bits. `TV_CSC_*`, `TV_CLR_KNOBS`, and `TV_CLR_LEVEL` program color conversion and analog levels. `TV_H_CTL_*`, `TV_V_CTL_*`, and `TV_SC_CTL_*` program timings and subcarrier generation. `TV_WIN_POS`, `TV_WIN_SIZE`, `TV_FILTER_CTL_*`, `TV_CC_*`, and `TV_*_LUMA/CHROMA()` support scaling, captions, and coefficient tables.

Control flow and integration: `intel_tv_pre_enable()` writes most of these registers from a selected `tv_mode`; `intel_tv_get_config()` reads timing/window fields back; `intel_tv_detect_type()` uses TV_CTL test mode plus TV_DAC sense bits; `intel_tv_init()` checks fuse and DAC state-change behavior.

State and persistence: this header defines all persistent TV MMIO state. Some fields are explicitly save/preserve masks (`TV_CTL_SAVE`, `TV_DAC_SAVE`) and must not be clobbered by mode programming or load detection.

Risks and tests: risks include wrong preserve masks, off-by-one timing fields, DAC voltage/sense misuse during load detect, and register-table length mismatches for 60 horizontal and 43 vertical luma/chroma coefficients. Test signals include analog connector detection, mode programming readback, property changes, TV disable/enable cycles, and register state restoration after detection.
