# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 10416-13053

## Scope And Purpose

This chunk is a generated AMD DCN 2.1 register-offset header slice. It contains no executable C logic; its interface is a large set of preprocessor constants that map display, audio, compression, firmware, writeback, GPIO, legacy VGA, and Azalia/HDA register names to numeric offsets and base-index selectors.

The range contains 2,389 `#define` entries and 63 `addressBlock` comments. It starts in the middle of the `DIG2` display encoder block, then covers the full `DP2`, `DIG3`/`DP3`, and `DIG4`/`DP4` MMIO register families. The middle of the chunk defines DCIO shared registers, DCIO chip-level GPIO/DDC/HPD/AUX/power-sequencer registers, six DSC compressor instances, DMU/DMCUB firmware registers, MCIF writeback instance 2 registers, and DCHVM host-VM control registers. The tail defines indirect legacy VGA index spaces and Azalia audio codec, descriptor, sink-info, CRC, input-endpoint, root/function, and stream-latency offsets.

Although the repository path is under `ceph-client`, this file is AMDGPU display hardware metadata for the Linux kernel DRM driver. It has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, classes, or runtime variables in this chunk. The public API is the generated macro namespace:

- `mmDIG2_*`, `mmDIG3_*`, and `mmDIG4_*` name DIG display encoder registers. The visible `DIG2` lines are a continuation from the previous chunk and include AFMT generic/audio/CRC/ramp/status controls, HDMI ACR/status controls, backend enable controls, TMDS controls, version/lane-enable, and force-disable registers. `DIG3` and `DIG4` repeat the fuller encoder surface for HDMI packet generation, AFMT audio/infoframes, audio CRC/ramp/status, TMDS signaling, output CRC/test patterns, FIFO status, backend controls, lane enable, and force-disable.
- `mmDP2_*`, `mmDP3_*`, and `mmDP4_*` name DisplayPort link/stream registers. They cover link control, pixel format, MSA colorimetry/timing/VBID fields, stream control, DPHY training/8b10b/scrambling/CRC/fast-training/test patterns, secondary-data/audio M/N/timestamp/packet controls, MST/MSE rate and slot allocation tables, MSO, DSC transport controls, Display Stream Metadata, Dynamic Backlight (`DP_DB_CNTL`), and ALPM.
- `mmDC_*`, `mmUNIPHY*`, `mmLVTMA_*`, `mmBL_PWM_*`, `mmDCIO_*`, `mmPHY_AUX_CNTL`, `mmAUXI2C_*`, and `mmDC_GPIO_*` define shared DCIO and chip-level GPIO surfaces. These include reference clock control, PHY link and channel crossbar controls, write-command delay, pinstraps, panel power sequencing, backlight PWM, genlock/swaplock pads, soft reset, DDC GPIO groups, HPD, generic GPIO, power-sequencer GPIO, AUX pad controls, pullups, RX enable, and pad strength.
- `mmDSC_TOP<N>_*`, `mmDSCCIF<N>_*`, `mmDSCC<N>_*`, and `mmDSC<N>_DC_PERFMON_*` define six DSC instances. Each compressor instance has top/debug control, DSC CIF configuration, DSCC configuration/status/interrupt, PPS configuration words, picture/slice geometry, bits-per-pixel and rate-control parameters, chunk/slice byte counts, RC range parameters, debug/status, clock-gating, memory power, FEC-ready shadow, and a local perfmon block.
- `mmDMCUB_*` defines the DMU/DMCUB firmware interface: instruction/data/region/cache windows, inbox/outbox base/size/read/write pointers, timer triggers/current value, scratch registers, control/reset/enable, GPINT data in/out, interrupt enable/ack/status, memory power, processor ID, and undefined-address fault reporting.
- `mmMCIF_WB2_*` defines MCIF writeback instance 2 registers for buffer-manager control/status, pitch, four Y/C buffer address pairs with high/offset words, buffer sizes/resolutions, arbitration, SCLK and NB P-state watermarks, QoS, warm-up, self-refresh, clock gating, and debug index/data.
- `mmDCHVM_*` defines display host-VM and RIOMMU control/status registers. Unlike most MMIO entries in this range, these use base index `3`.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` define legacy VGA sequencer, CRT controller, graphics controller, and attribute-controller indirect indexes.
- `ixAZALIA_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, and `ixAZF0STREAM*` define indirect HDA/Azalia audio register indexes for function group 2 endpoints, descriptor and sink-info tables, input/output CRC result channels, input endpoints, codec root/function controls, and stream FIFO/latency counters.

For `mm...` macros, each register has a companion `*_BASE_IDX` macro. Most display/DCIO/DMCUB/DSC/writeback entries in this chunk use base index `2`; the DCHVM block uses base index `3`. For `ix...` macros, the constants are indirect indexes and do not have `*_BASE_IDX` companions.

## Control Flow

This header has no local runtime control flow. Every line is declarative metadata consumed by AMDGPU display code through register-access macros and generated register tables.

The implied consumer flow for `mm...` entries is:

1. Select a DCN 2.1 register block or hardware instance, such as DIG3, DP4, DSC2, DMCUB, or MCIF_WB2.
2. Pass the symbolic register name to a helper such as `REG_OFFSET`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, or generated constructor macros.
3. Use the paired `*_BASE_IDX` to select the correct MMIO base segment.
4. Use the companion `dcn_2_1_0_sh_mask.h` definitions to encode or decode fields inside the register value.

The implied consumer flow for `ix...` entries is indirect: select the relevant VGA or Azalia index/data aperture, write or address the index value, then read or write the data register using the hardware-specific path. This chunk does not define the index/data mechanism or field semantics.

Programming order is external to this file. For example, DP link training, HDMI audio clock regeneration, DSC PPS setup, DMCUB boot/inbox setup, MCIF writeback buffer rotation, HPD/DDC GPIO handling, and Azalia stream routing all have sequencing rules enforced by higher-level driver code and hardware documentation, not by this offset header.

## State And Persistence Behavior

The macros themselves are immutable compile-time constants. They allocate no memory, hold no references, perform no locking, and persist no software state.

The hardware registers identified by these offsets are stateful and vary by block:

- DIG/DP registers hold encoder mode, packet/audio/metadata state, link-training state, MST allocation, DSC transport state, CRC/test state, and live status bits.
- DCIO and GPIO registers hold PHY routing, panel power sequencing, backlight PWM, HPD/DDC/AUX pad configuration, and soft-reset state.
- DSC registers hold compressor configuration and PPS/rate-control state, while perfmon registers expose counter/filter/snapshot behavior.
- DMCUB registers expose firmware boot windows, scratch mailboxes, GPINT signaling, inbox/outbox ring pointers, timers, interrupt state, fault state, and memory power controls.
- MCIF_WB2 registers hold writeback buffer addresses, sizes, pitch, arbitration, QoS/watermark, and buffer-manager state.
- DCHVM registers control and report display host-VM/RIOMMU state.
- VGA and Azalia `ix...` indexes address legacy display state, audio endpoint capabilities and controls, sink descriptors, CRC results, input status, power/reset controls, and stream FIFO/latency counters.

Volatility is register-specific and not encoded here. Some registers are read-only capabilities or status, some are sticky or write-one-to-clear interrupt/status bits, some are self-clearing controls, and some retain programmed values until modeset, hotplug, suspend/resume, GPU reset, or firmware reinitialization.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 2.1 ASIC register database. The numeric offsets must match the DCN 2.1 hardware map and the companion mask/shift header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h`.

In this tree, `dcn_2_1_0_offset.h` is included by DCN 2.1 display modules such as `dmub_dcn21.c`, `irq_service_dcn21.c`, `hw_factory_dcn21.c`, `hw_translate_dcn21.c`, and `dcn21_resource.c`. Those users integrate the constants with register helper macros, IRQ-source tables, GPIO construction/translation, resource initialization, and DMUB service register tables.

Major integration surfaces represented by this chunk include:

- DisplayPort and HDMI encoder bring-up for multiple link instances.
- DP MST, MSO, DSC-over-DP, secondary-data packets, audio transport, metadata, and ALPM.
- HDMI/TMDS packet and audio configuration.
- GPIO, HPD, DDC, AUX, panel power sequencing, and backlight control.
- DSC compressor programming for up to six instances and associated performance monitoring.
- DMCUB firmware boot, mailbox, GPINT, scratch, timer, and interrupt handling.
- Display writeback through MCIF writeback instance 2.
- Host-VM/IOMMU interaction for display memory access.
- Legacy VGA and HDA/Azalia audio endpoint compatibility paths.

## Risks And Edge Cases

The primary risk is silent hardware misaddressing. A wrong offset or base index compiles successfully but can read or write a different register, causing failures that look like link-training flakiness, absent display output, broken HDMI/DP audio, bad DSC compression, missed HPD/DDC events, invalid GPIO polarity, DMCUB boot or mailbox failures, writeback corruption, or VM/IOMMU faults.

The chunk is highly repetitive across instances. DIG3 and DIG4 are parallel layouts; DP2, DP3, and DP4 are parallel layouts; DSC0 through DSC5 are parallel compressor layouts with regular base-address spacing. Instance-local generator mistakes can affect only one connector, stream, compressor, or writeback path, so tests that exercise only the first instance may miss defects in higher-numbered blocks.

The range starts mid `DIG2` and ends mid `AZF0STREAM15`. Whole-file reconciliation should treat both ends as continuations owned jointly with neighboring chunks. In particular, this chunk should not be described as the complete DIG2 or Azalia stream namespace.

Names expose intent but not access semantics. Registers named `*_INTERRUPT_*`, `*_STATUS`, `*_ACK`, `*_RESET`, `*_SOFT_RESET`, `*_POWER_*`, `*_LPIB_SNAPSHOT_*`, and `*_FORMAT_CHANGED` still require companion field definitions and hardware documentation for polarity, clear behavior, ordering, and side effects.

The `mm...` and `ix...` namespaces must not be mixed. `mm...` values are MMIO offsets plus base indexes; `ix...` values are indirect indexes for VGA or Azalia mechanisms. Treating an `ix...` value as a flat MMIO address, or ignoring `*_BASE_IDX` on `mm...` values, would target the wrong hardware path.

DCHVM uses a different base index than the surrounding display blocks. Generic code that assumes base index `2` for every macro in this range would misaddress DCHVM control/status registers.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build DCN 2.1 AMDGPU display code and ensure `dmub_dcn21.c`, DCN 2.1 IRQ service, GPIO factory/translator, and resource code compile with this offset header and the matching mask/shift header.
- Compare all constants in this line range against AMD's source register database and against adjacent DCN/DCE generation headers where repeated block layouts should match.
- Exercise DP2, DP3, and DP4 links independently with link training, video modes, MST slot allocation, MSO where supported, DSC transport, secondary-data packets, audio, metadata, CRC, and hotplug.
- Exercise DIG3 and DIG4 HDMI/TMDS modes, including infoframes, generic packets, audio ACR, AFMT status/CRC, lane enable, backend enable, and force-disable paths.
- Validate DCIO GPIO behavior with HPD interrupts, DDC/AUX transactions, panel power sequencing, backlight PWM changes, genlock/swaplock pads, and suspend/resume.
- Program each DSC instance used by the platform and verify compressed display output, PPS/rate-control settings, interrupt/status handling, clock/memory power behavior, and perfmon counters.
- Boot and communicate with DMCUB on DCN 2.1 hardware, covering inbox/outbox ring pointers, GPINT interrupts, scratch/status registers, timer reads, reset transitions, and fault reporting.
- Run writeback tests that specifically use MCIF_WB2, checking buffer address high/low programming, Y/C offsets, pitch, resolution, watermarks, arbitration, buffer-manager status, and QoS behavior.
- Exercise Azalia audio enumeration and playback/capture-visible paths, including endpoint capabilities, sink descriptors, HBR/multichannel settings, stream latency counters, CRC channels, LPIB snapshots, codec reset/power state, and input endpoint infoframes.
- Include suspend/resume, GPU reset, repeated modesets, connector unplug/replug, audio format changes, and multi-connector scenarios to catch stale register state and instance-specific offset errors.

Regression symptoms from bad constants include black screens on specific connectors, DP link-training failures, MST bandwidth or slot allocation errors, DSC corruption, missing or unstable HDMI/DP audio, broken backlight or HPD/DDC/AUX behavior, DMCUB command timeouts, writeback frame corruption, impossible latency/CRC counters, and failures isolated to DIG3/DIG4, DP3/DP4, DSC instances above 0, or stream indexes above the first few.

## Cross-Chunk Notes

Neighboring chunks own the beginning of the `DIG2` block before line 10416 and the remainder of `AZF0STREAM15` and later offset definitions after line 13053. The final merge lane should describe this source file as generated DCN 2.1 register-offset metadata, with this chunk specifically covering the mid-file display-output, compression, firmware, writeback, host-VM, VGA, and Azalia indirect-register ranges.
