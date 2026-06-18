# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 10412-12940

## Scope And Purpose

This chunk is a generated AMD DCN 2.0 register-offset header slice. It contains preprocessor constants only: no functions, structs, enums, variables, allocation, locking, or executable control flow. The constants define MMIO register offsets and their generated `_BASE_IDX` selector values for DCN 2.0 display I/O, hotplug, AUX, stream encoder, DisplayPort, DCIO, GPIO/DDC, panel power/backlight, and the beginning of UNIPHY0 macro-control space.

The source tree path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The requested range contains 2,421 `#define` entries: 1,211 register-offset macros and 1,210 matching `_BASE_IDX` macros. It covers 27 generated `addressBlock` comments. The range starts in the middle of `dce_dc_dio_hpd0_dispdec`, with `mmHPD0_DC_HPD_CONTROL` through `mmHPD0_DC_HPD_TOGGLE_FILT_CNTL`, and ends in the middle of `dce_dc_dcio_dcio_uniphy0_dispdec`, at `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10`.

Major address-block families in this chunk:

- HPD blocks `HPD0` through `HPD5` for display hotplug detect status, interrupt control, HPD line control, fast training, and toggle filtering.
- `DC_PERFMON20` display performance counter control, state, current-value, high, and low registers.
- `DP_AUX0` through `DP_AUX5` for AUX/I2C-over-AUX controller control, arbitration, software and link-service data/status, DPHY TX/RX controls/status, GTC sync, and PHY wake control.
- `DIG0` through `DIG5` stream-encoder front/back-end and HDMI/AFMT register groups for CRC, HDMI packet controls, infoframes, ACR, audio packets, generic metadata packets, 60958 channel-status words, TMDS controls, AFMT CRC/ramp/status, and force-disable controls.
- `DP0` through `DP5` DisplayPort register groups for link control, pixel/MSA configuration, stream timing, training patterns, DPHY/CRC/scrambling, secondary data packets, audio M/N, MST/MSE allocation/status, MSO, DSC, ALPM, metadata, and double-buffer control.
- DCIO global register groups for generic DC registers, UNIPHY A-F link and channel-crossbar controls, write-command delay, pinstraps, LVTMA panel power sequencing, backlight PWM, genlock/swaplock pads, DCIO clock/reset, and AUX impedance calibration.
- DCIO chip/GPIO groups for generic GPIO, DDC1-DDC6, DDCVGA, genlock, HPD, power-sequence GPIOs, pad strength, AUX controls, RX/pullup enables, and AUX/I2C pad power-good.
- The first 11 `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED<N>` offsets, with their base indices.

## Important APIs, Types, And Macros

There are no callable APIs or C type definitions in this chunk. The exported interface is the generated macro namespace:

- `mm<REGISTER>` gives a register offset in the DCN 2.0 address space.
- `mm<REGISTER>_BASE_IDX` gives the generated base-index selector used by AMDGPU/DC register helper macros to add the correct IP block base.
- Repeated instance names such as `HPD3`, `DP_AUX4`, `DIG2`, and `DP5` identify hardware instances, not C objects.

Important macro families:

- `mmHPD<N>_DC_HPD_*` registers are the hotplug-detect interface used for connector plug/unplug and HPD RX style events. `HPD1` through `HPD5` include status and interrupt-control offsets in this range; `HPD0` status/control begins in the previous chunk, while this chunk contains the latter part of its control group.
- `mmDC_PERFMON20_*` gives one display performance-monitor block with counter control, state, current-value interrupt/misc, high, and low registers.
- `mmDP_AUX<N>_AUX_*` registers are per-AUX-channel controller offsets. They include software control/data/status, arbitration and interrupt control, low-speed data/status, DPHY TX/RX programming and readback, global time counter sync controls/status, and PHY wake control.
- `mmDIG<N>_*` registers represent each digital stream encoder's HDMI/AFMT/TMDS-facing register set. The names cover HDMI metadata and generic-packet controls, ACR values and readback, audio packet controls, AFMT infoframes and generic data slots, IEC 60958 words, CRC controls/results, TMDS pattern/balancer controls, DIG version/lane enable, and force-disable.
- `mmDP<N>_DP_*` registers represent each DisplayPort stream/link block. The names cover link framing, pixel format, MSA colorimetry/timing/VBID, video M/N, DPHY lane training, PRBS/scrambling/CRC, secondary data packet and audio timing, MST/MSE allocation and status, MSO, DSC bytes-per-pixel/control, ALPM, metadata transmission, and double-buffer control.
- `mmUNIPHYA_*` through `mmUNIPHYF_*` identify link control and channel crossbar controls for the six physical transmitter blocks.
- `mmLVTMA_PWRSEQ_*` and `mmBL_PWM_*` cover embedded-panel power sequencing and backlight PWM.
- `mmDC_GPIO_*`, `mmPHY_AUX_CNTL`, `mmDC_GPIO_AUX_CTRL_*`, and `mmAUXI2C_PAD_ALL_PWR_OK` are DCIO chip-level GPIO/DDC/AUX pad offsets used by GPIO, DDC/I2C, HPD, power-sequence, and pad-control code.
- `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED<N>` begins a reserved macro-control array for UNIPHY0. This chunk only includes entries 0 through 10; later entries are in the next chunk.

The field names, bit shifts, and masks are not defined here. They live in sibling generated headers such as `dcn_2_0_0_sh_mask.h`, while higher-level enum and IP-base data come from related DCN/Navi10/SOC15 headers.

## Control Flow And Data Flow

This header chunk has no runtime control flow. Data flow is compile-time substitution:

1. A DCN 2.0 consumer includes `dcn_2_0_0_offset.h` and usually the matching `dcn_2_0_0_sh_mask.h`.
2. Helper macros combine a register offset with the base index, for example `BASE(mmREG_BASE_IDX) + mmREG`.
3. The resulting absolute register address is stored in generated register tables or used by `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, IRQ-source tables, AUX/link encoder helpers, and similar AMDGPU/DC register abstractions.
4. The companion mask/shift macros select fields for read-modify-write or status decoding.

Concrete consumers in this tree show that pattern. `display/dc/resource/dcn20/dcn20_resource.c` defines `SR`, `SRI`, `SRIR`, and related macros that expand `mm...` offsets into DCN 2.0 resource register lists. Its resource tables include the AUX, HPD, stream-encoder, DisplayPort, and UNIPHY-style registers represented by this chunk. `display/dc/irq/dcn20/irq_service_dcn20.c` uses `SRI()` to build HPD interrupt enable/status/ack register addresses from `mmHPD<N>_DC_HPD_INT_*` macros. `display/dmub/src/dmub_dcn20.c` and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include the same generated header for DCN 2.0 register-table setup, though their direct references are not limited to this chunk. `amdgpu/gmc_v10_0.c` also includes the DCN 2.0 generated headers as part of SOC15/Navi10 register metadata.

The header does not encode programming order. Correct sequencing is imposed by the display core and hardware specifications: HPD interrupts must be masked/acked with the correct polarity, AUX transactions must arbitrate and poll status in the required order, stream encoder and DP link registers must be programmed around link training and modeset transitions, HDMI/AFMT audio packets must match audio stream state, and GPIO/power/backlight registers must be written in panel-safe sequences.

## State And Persistence Behavior

The macros themselves hold no mutable software state and perform no I/O. The mutable state represented by this chunk lives in hardware registers.

State categories described by these offsets include:

- Connector and interrupt state: HPD status, HPD interrupt enable/ack, HPD RX interrupt enable/ack, fast-training controls, and HPD debounce/toggle filtering.
- AUX/DDC transaction state: controller enable/reset, software command/data/status, arbitration ownership, interrupt control, low-speed data/status, AUX DPHY TX/RX tuning/status, GTC sync status, and PHY wake behavior.
- Stream-encoder state: HDMI metadata and infoframes, generic packets, ACR/audio packet generation, AFMT controls, IEC 60958 channel-status words, CRC/ramp diagnostics, TMDS control, lane enable, and DIG force-disable.
- DisplayPort link/stream state: lane/link configuration, pixel format, MSA timing/colorimetry/VBID, video M/N, training patterns, DPHY symbol/CRC/scrambler state, secondary packet framing, DP audio M/N, MST/MSE bandwidth allocation, MSO, DSC, ALPM, metadata transmission, and double-buffer state.
- Physical link and pad state: UNIPHY link/crossbar routing, DCIO pinstraps, genlock/swaplock pads, DCIO clock/reset, AUX impedance calibration, GPIO/DDC/HPD/power-sequence directions and values, pad strengths, AUX controls, pullups, RX enables, and pad power-good.
- Panel state: LVTMA power-sequence control/state/delays and backlight PWM control/period/locking.
- Diagnostics: display perfmon counters, HDMI/AFMT/DP DPHY CRC registers, status/readback registers, and reserved UNIPHY macro-control offsets.

Persistence is register-specific and not stated in the offset header. Some registers are durable control values that remain programmed until a modeset, link retrain, suspend/resume, reset, power transition, or later driver write. Others are live status bits, sticky interrupt flags, write-one-to-clear acknowledgements, hardware counters, self-clearing commands, read-only capabilities/status, or reserved registers whose semantics are intentionally opaque in this generated file.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 ASIC register database. The numeric offsets and `_BASE_IDX` values are meaningful only with the matching base-address definitions and field metadata:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h` for field masks and shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_offset.h` and `dpcs_2_0_0_sh_mask.h` for paired DPCS register metadata used by DCN 2.0 link resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/soc15/navi10_ip_offset.h` and SOC15 base-address helpers used by `BASE(mm..._BASE_IDX)`.
- Register-helper macros in AMD display code, including `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, and IRQ resource-list builders.

Direct include consumers found in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration surfaces are DRM/KMS connector detection, HPD interrupt handling, AUX/DDC transactions and EDID reads, DP link training, DP MST/MSE bandwidth programming, HDMI and DisplayPort stream encoder setup, HDMI/DP audio packet generation, DSC/MSO/ALPM modes, panel power and backlight control, GPIO/DDC/HPD pad translation, genlock/swaplock pad configuration, DCIO reset/clock control, and low-level debug/CRC/perf-counter workflows.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong offset or base index can compile cleanly while reading or writing the wrong register, causing black screens, missed hotplug, bad AUX/DDC transactions, broken link training, audio failures, interrupt storms, or unintended reset/power effects.
- The chunk begins and ends mid-address-block. `HPD0` status and interrupt-control offsets are in the previous chunk, and most of the `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED<N>` array is in the next chunk. The final per-file synthesis must stitch those boundaries together.
- Instance repetition increases review risk. `AUX0`-`AUX5`, `DIG0`-`DIG5`, `DP0`-`DP5`, and `HPD0`-`HPD5` are nearly regular, but a one-instance offset or base-index error can affect only one connector or stream.
- `_BASE_IDX` values are as important as the visible offsets. Most values in this range are `2`; using the wrong base segment with a numerically correct offset still addresses the wrong IP aperture.
- AUX registers mix command, data, arbitration, interrupt, DPHY tuning, wake, and status surfaces. Incorrect ordering or ack/mask semantics can hang AUX transfers, misread EDID/DPCD, or break HPD RX paths.
- Stream encoder and DP link programming is timing-sensitive. Bad DIG/DP constants can disturb link training, MSA timing, MST allocation, DSC/MSO, ALPM, HDMI infoframes, audio packets, or CRC diagnostics.
- GPIO/DDC/HPD/panel power registers are physical-pad controls. Misprogramming direction, output value, pullups, pad strength, AUX controls, or panel power/backlight sequencing can produce connector detection failures, I2C failures, panel flicker, backlight faults, or unsafe panel transitions.
- Reserved UNIPHY macro controls should not be inferred from names alone. Their offsets may be needed for generated tables or debug paths, but behavior must come from AMD's hardware database, not from the `RESERVED` names.
- Names such as `*_STATUS`, `*_ACK`, `*_INT_CONTROL`, `*_RESET`, `*_WAKE`, `*_LOCK`, `*_CRC_RESULT`, and `*_READBACK` signal possible side effects or volatility, but the offset header does not define access type or write semantics.

## Test Signals

Useful validation is a mix of generated-header comparison, build coverage, and hardware behavior:

- Build AMDGPU/DC configurations that include DCN 2.0/Navi10 paths. Missing or renamed constants should surface in `dcn20_resource.c`, `irq_service_dcn20.c`, `dcn20_clk_mgr.c`, `dmub_dcn20.c`, and `gmc_v10_0.c`.
- Compare all offsets and `_BASE_IDX` values in lines 10412-12940 against AMD's authoritative DCN 2.0 register database or a known-good upstream `dcn_2_0_0_offset.h`.
- Exercise all connector instances, not just connector 0: HPD plug/unplug, HPD RX events, EDID reads, DPCD reads/writes, DP link training, HDMI modes, DP modes, MST where available, suspend/resume, GPU reset, and repeated modeset cycles.
- Validate AUX/DDC behavior through successful EDID/DPCD access, sane AUX timeout/error handling, and no stuck arbitration or interrupt state after failed transactions.
- Validate DP link behavior with lane-count/rate changes, training-pattern transitions, MSA timing, secondary data packets, audio M/N readback, MST/MSE allocation, DSC/MSO/ALPM paths where supported, and DP DPHY CRC/debug readback.
- Validate HDMI/AFMT behavior with infoframes, generic metadata packets, ACR generation, audio packet control, IEC 60958 channel-status programming, audio CRC/status readback, and audio playback across common rates/channel counts.
- Validate GPIO/DDC/HPD/panel paths by checking DDC bus operation on all ports, HPD GPIO state translation, panel power-on/off sequencing, backlight PWM changes, suspend/resume backlight restoration, and pad power-good/pullup behavior.
- Monitor logs and hardware counters for regression signals: absent connectors, missed or repeated HPD interrupts, AUX timeouts, bad EDID, DPCD failures, link-training failure, no HDMI/DP audio, wrong audio format/channel map, underflow/flicker, black screen after resume, panel backlight stuck on/off, or unexpected DCIO reset effects.

## Cross-Chunk Notes

Adjacent chunks are required for a full-file report. This chunk continues an HPD0 block that began before line 10412 and stops partway through the UNIPHY0 reserved macro-control block. During reconciliation, describe this range as the DCN 2.0 DIO/DCIO offset section spanning HPD, perfmon, AUX, DIG, DP, DCIO, GPIO, panel power/backlight, and the beginning of UNIPHY0, not as a standalone complete header.
