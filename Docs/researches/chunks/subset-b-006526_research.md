# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-reg.h lines 8768-10773

## Scope

This chunk covers the tail of the MT8189 AFE register-definition header. It is macro-only C preprocessor content: bit shifts, unshifted masks, shifted masks, MMIO register offsets, and final range/status constants. There are no functions, structs, or executable control-flow blocks in this slice, but the definitions are consumed by the MT8189 ALSA SoC AFE driver through regmap reads, writes, update masks, volatile-register classification, IRQ dispatch, and hardware capability bounds.

## Purpose

The chunk defines several hardware-facing groups:

- Secure SRAM and secure/non-secure audio interconnect permission fields.
- Secure and normal input mask windows and secure output select windows for the AFE interconnect fabric.
- Mask-monitor registers for selected interfaces such as PCM0, CONNSYS I2S, MTKAIF, and ADDA uplink paths.
- GASRC0 asynchronous sample-rate-converter control, frequency calibration, coefficient SRAM, debug, and IP-version fields.
- The main AFE register offset map from top-level clock/control blocks through gain, ADDA, ETDM, TDM/HDMI, connection matrix, memory interface, secure control, ASRC/GASRC, SoundWire phase, and IRQ blocks.
- Final driver constants: `AFE_MAX_REGISTER`, `AFE_IRQ_STATUS_BITS`, `AFE_IRQ_CNT_SHIFT`, and `AFE_IRQ_CNT_MASK`.

This file is the source of truth for numeric offsets and bit layouts. Driver code should use these names instead of hard-coded offsets so the register map remains auditable and regmap can enforce the right address bounds.

## Important Definitions

The secure SRAM definitions at the start of the chunk finish non-secure SRAM write/read enable bits and then define `AFE_SECURE_SRAM_CON1` secure bits. Each SRAM slot has paired write/read enables, numbered 0 through 15, packed as alternating bits. For the secure register, `SRAM_WRITE_EN0_S_SFT` starts at bit 0 and `SRAM_READ_EN15_S_SFT` ends at bit 31. These macros are likely used with `regmap_update_bits()` style operations where the `_MASK_SFT` value provides the shifted one-bit mask and `_SFT` provides the bit position for composed values.

The secure interconnect input masks are expressed as 32-bit windows:

- `SECURE_INTRCONN_I0_I31_S_*` through `SECURE_INTRCONN_I224_I256_S_*`.
- `NORMAL_INTRCONN_I0_I31_S_*` through `NORMAL_INTRCONN_I224_I256_S_*`.

Each mask macro covers a full 32-bit register. The labels show that the connection fabric has secure and non-secure classification windows for AFE inputs. The last range name uses `I224_I256`, but the mask is still `0xffffffff`; callers should treat the name as a hardware naming convention rather than proof that bit 32 exists in that specific register.

Secure output selection registers mirror the input-window pattern with `SECURE_INTRCONN_O0_O31_S_*` through `SECURE_INTRCONN_O224_O256_S_*`. These define full-width security selection masks for output endpoints.

The mask-monitor fields, such as `AFE_PCM0_INTF_CON1_MASK_MON_*`, `AFE_CONNSYS_I2S_CON_MASK_MON_*`, `AFE_MTKAIF0_CFG0_MASK_MON_*`, and `AFE_ADDA_UL0_SRC_CON0_MASK_MON_*`, are full-width monitor fields. They expose hardware-observed mask state rather than narrow configuration fields.

The `AFE_GASRC0_NEW_CON*` fields describe one generic ASRC instance in detail:

- `AFE_GASRC0_NEW_CON0` controls ASRC enable, channel-set enable, stream clear, coefficient SRAM control, mono/16-bit format, input/output frequency selectors, IIR enable/stage, and special clocking/heart-beat behavior.
- `AFE_GASRC0_NEW_CON1` through `CON4` provide four 24-bit `ASM_FREQ_*` fields.
- `AFE_GASRC0_NEW_CON5` selects input/output sample-rate domains, calibration clock/LRCK sources, calibration result source, and soft reset.
- `AFE_GASRC0_NEW_CON6` controls frequency calibration enable, auto restart, debounce/glitch filtering, max gate width, calibration source, result compensation, auto-tune controls, running status, and autorst detection.
- `AFE_GASRC0_NEW_CON7` through `CON9` expose 24-bit denominator/result/record values.
- `AFE_GASRC0_NEW_CON10` and `CON11` are coefficient SRAM data/address fields.
- `AFE_GASRC0_NEW_CON12` is ring-debug read data.
- `AFE_GASRC0_NEW_CON13` and `CON14` define high/low thresholds for frequency-calibration auto reset.
- `AFE_GASRC0_NEW_IP_VERSION` is a full-width version register.

The offset map begins at `AUDIO_TOP_CON0` and continues to `AFE_CUSTOM_IRQ_MCU_DSP_WLA_EN`. It includes repeated register families for gains, ADDA downlink/uplink, digital microphones, MTKAIF, ETDM/TDM, connection matrix, memory interfaces, secure controls, ASRC/GASRC instances, SoundWire uplink-source phase control, and common/custom IRQ blocks. `AFE_MAX_REGISTER` aliases the last defined offset so the regmap configuration can reject addresses beyond the known hardware map.

## Register-Map Integration

The chunk is integrated through `mt8189-afe-pcm.c`. The regmap configuration uses `AFE_MAX_REGISTER` as `.max_register` and `.num_reg_defaults_raw`, with 32-bit registers, 4-byte stride, 32-bit values, and flat caching. This makes the final offset in this chunk part of the driver's addressability contract.

Several registers from this chunk are explicitly classified as volatile in the PCM driver. The volatile set includes monitor registers, ASRC/GASRC status/result registers, IRQ enable/config registers, and selected memory-interface controls. For GASRC0, the driver marks `AFE_GASRC0_NEW_CON0`, `CON6`, `CON8`, `CON9`, `CON10`, `CON11`, `CON12`, and `IP_VERSION` as volatile. This matters because stale regcache values would be unsafe for live calibration, coefficient-SRAM, debug, and IP-version state.

The IRQ handler uses the final `AFE_IRQ_STATUS_BITS` mask when intersecting status and enable registers:

- `AFE_IRQ_MCU_STATUS & AFE_IRQ_MCU_EN & AFE_IRQ_STATUS_BITS`.
- `AFE_CUSTOM_IRQ_MCU_STATUS & AFE_CUSTOM_IRQ_MCU_EN & AFE_IRQ_STATUS_BITS`.

Only enabled and in-range interrupt bits are allowed to drive `snd_pcm_period_elapsed()` and IRQ clearing. The `0x7ffffff` mask means bits 0 through 26 are accepted for the common status path, matching the `AFE_IRQ0_MCU_CFG*` through `AFE_IRQ26_MCU_CFG*` offsets in this chunk.

## Control Flow

This header chunk has no runtime control flow by itself. It enables control flow in the driver in three main ways:

- Register writes and updates use the offset macros to route operations to hardware blocks.
- Bitfield macros let callers set, clear, or test packed control fields without manual shifts.
- Volatile-register and IRQ-handler switch/loop logic in the PCM driver depends on these numeric constants to decide which values must be read from hardware and which interrupts require ALSA period callbacks.

For secure routing and memory protection, higher-level driver code is expected to program sideband, secure connection, secure SRAM, and secure/non-secure input/output masks in a sequence consistent with the SoC's power and trust-domain state. This chunk only names the controls; ordering requirements live in the consuming driver or firmware contract.

## State And Persistence

All definitions in this chunk represent either hardware register addresses or hardware bitfields. The persistent state is the AFE hardware state behind those addresses, not any C object in the header. Some registers are ordinary cached configuration state under regmap, while monitors, counters, calibration outputs, current pointers, and IRQ status fields are live hardware state and must be treated as volatile by consuming code.

Memory-interface offsets define base/current/end pointer registers for downlink (`AFE_DL*`), uplink (`AFE_VUL*`), ETDM input, and HDMI output paths. These values persist in hardware while a stream is configured and running, and the current-pointer/monitor registers change as DMA progresses. Secure controls and connection masks persist as hardware security/routing state until reset or reprogrammed.

IRQ configuration and count registers persist interrupt period, enable, delay, and count state. The final `AFE_IRQ_CNT_SHIFT` and `AFE_IRQ_CNT_MASK` constants describe a 24-bit count field used by IRQ counter/config handling.

## Dependencies

The chunk depends on Linux kernel conventions rather than local helper functions:

- C preprocessor macro expansion.
- Linux `BIT()` and regmap-style update/read APIs in consuming C files.
- ALSA SoC MediaTek AFE driver data structures that map memory interfaces, IRQ IDs, and register addresses to runtime stream behavior.
- Hardware documentation or generated register descriptions for MT8189 AFE; the naming and repeated pattern strongly indicate an auto-generated or register-database-derived header.

No include-time dependencies are introduced in this chunk beyond the surrounding header guard ending at line 10773.

## Risks And Edge Cases

Register offset drift is the largest risk. If any offset in this chunk diverges from the SoC register map, the driver can write to the wrong hardware block. This is especially risky in the secure-control, memory-interface, and IRQ regions because a wrong write can break access control, DMA buffer bounds, or interrupt delivery.

Mask/shift misuse is another common risk. Many fields provide both `_MASK` and `_MASK_SFT`; callers must use `_MASK_SFT` when passing a shifted mask to `regmap_update_bits()` and use `_SFT` when constructing shifted values. Accidentally shifting `_MASK_SFT` again or passing unshifted `_MASK` for nonzero fields can silently configure the wrong bits.

The full-width secure/non-secure interconnect mask definitions and monitor definitions use `0xffffffff`. Callers need to avoid C signedness pitfalls when storing or printing these values; they should remain unsigned 32-bit register values.

The repeated GASRC register blocks define five instances in the offset map (`GASRC0` through `GASRC4`), but detailed bitfield definitions in this chunk are only named for `GASRC0`. If the hardware layout is shared across instances, consumers may reuse the `GASRC0` field masks with other GASRC instance offsets, but that coupling is implicit and should be verified before adding new code.

`AFE_MAX_REGISTER` is tied to the last listed custom IRQ enable register. Adding later hardware registers requires updating this macro; otherwise regmap may reject valid accesses or fail to allocate enough flat-cache space.

IRQ masking with `AFE_IRQ_STATUS_BITS` intentionally ignores bits above 26 in common/custom status handling. If future IRQ definitions use higher bits, this mask must be updated together with IRQ data tables and clear logic.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage for macro names referenced by MT8189 AFE sources.
- Regmap probe success with `.max_register = AFE_MAX_REGISTER`; failures or invalid-register warnings indicate offset/bounds issues.
- Playback and capture smoke tests that exercise `AFE_DL*`, `AFE_VUL*`, ETDM, HDMI, and IRQ period callbacks.
- Interrupt tests confirming only enabled bits within `AFE_IRQ_STATUS_BITS` cause `snd_pcm_period_elapsed()` and that IRQ clear registers are updated correctly.
- Suspend/resume or power-domain tests verifying secure routing, SRAM access enables, and volatile monitor/calibration registers are not restored from stale cache incorrectly.
- Hardware register dumps comparing key offsets in this header against the MT8189 register manual, especially secure-control, GASRC, memory-interface, and IRQ ranges.
