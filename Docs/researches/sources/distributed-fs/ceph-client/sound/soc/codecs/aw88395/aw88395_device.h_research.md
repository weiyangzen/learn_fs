# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.h

## Purpose
`aw88395_device.h` is the shared device-engine header for AW88395 and, partly, AW88399. It declares runtime state structures, firmware/calibration constants, enums for power/DSP/profile states, and exported device APIs.

## Important APIs And Types
The central type is `struct aw_device`, holding Linux handles, profile state, firmware status, DSP status, volume/fade state, profile information, DSP memory descriptors, VMAX, and calibration data. Helper descriptors include `aw_volume_desc`, `aw_dsp_mem_desc`, `aw_cali_desc`, and `aw_container`. Public prototypes cover initialization, start/stop, firmware update, profile access, ACF checking/loading, mute, and DSP read/write. Constants define calibration ranges, conversion macros between displayed and DSP Re values, ACF filename, DSP transfer size, and retry/timing values.

## Control Flow And State
The header reflects a two-phase lifecycle: Linux probe creates `aw_device`, then firmware parsing populates profiles and marks firmware OK. Runtime code transitions `status` between `AW88395_DEV_PW_OFF` and `AW88395_DEV_PW_ON`, transitions firmware between failed/OK, and uses `prof_index` versus `prof_cur` to decide whether a profile reload is needed. `dsp_lock` serializes mailbox operations independently from the top-level codec mutex.

## Dependencies And Integration Points
It includes `aw88395.h`, `aw88395_data_type.h`, and `aw88395_lib.h`, and is included by AW88395 implementation plus AW88399 for common profile/ACF/DSP data structures. This shared use makes the AW88395 data-type definitions an integration dependency for other Awinic chips.

## Risks And Test Signals
The generic `aw_device` contains both chip-neutral and AW88395-specific assumptions, so reuse by AW88399 requires careful interpretation of fields such as `dsp_cfg`, calibration descriptor, and profile data slots. Test signals include successful compilation of both AW88395 and AW88399 consumers, correct profile counts, guarded invalid profile indices, and serialized DSP access under concurrent control changes.
