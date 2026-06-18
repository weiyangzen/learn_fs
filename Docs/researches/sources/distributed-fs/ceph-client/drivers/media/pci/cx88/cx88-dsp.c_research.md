# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-dsp.c

## Purpose
Provides software stereo/SAP detection for cx88 analog TV audio by sampling the audio RDS FIFO and applying fixed-point frequency detection. It supplements the TV audio code by identifying mono, stereo, and dual-language subchannels for A2/A2M/EIAJ-style systems, with BTSC stubs present but not implemented.

## Important APIs, Types, And Data
The exported API is `cx88_dsp_detect_stereo_sap(struct cx88_core *core)`. Internal helpers include `int_cos()` for fixed-point cosine approximation, `int_goertzel()` for tone power, `freq_magnitude()`, `noise_magnitude()`, `detect_a2_a2m_eiaj()`, `detect_btsc()`, and `read_rds_samples()`. Constants define baseband frequencies for A2, A2M, EIAJ, BTSC dual/SAP reference tones, and a noise band. Module parameter `dsp_debug` controls logging.

## Control Flow
Detection first checks that the audio RDS FIFO is enabled in `MO_AUD_DMACNTRL`, that RDS input is enabled in `AUD_CTL`, and that at least 500 ms have passed since the last audio standard change. It then reads a circular set of 16-bit samples from `SRAM_CH27` based on the current FIFO pointer, using all but one FIFO line. Depending on `core->tvaudio`, it runs A2/A2M/EIAJ detection or BTSC detection. A2-style detection computes carrier, stereo, dual, and noise magnitudes using Goertzel filters, compares thresholds, and returns V4L2 tuner subchannel flags or mono. BTSC currently returns `UNSET`.

## State And Persistence
The file keeps no persistent private state. It reads volatile samples from the hardware SRAM audio RDS FIFO and relies on `core->tvaudio` and `core->last_change`. Temporary sample buffers are allocated with `kmalloc_objs()` and freed before returning. Detection results are returned to callers and are not stored here.

## Dependencies And Integration Points
It depends on cx88 core/register definitions, `cx88_sram_channels[SRAM_CH27]`, audio DMA setup from `cx88_start_audio_dma()`, and TV audio mode selection from `cx88_set_tvnorm()`/`cx88-tvaudio.c`. Results integrate with V4L2 tuner reporting through flags such as `V4L2_TUNER_SUB_STEREO`, `V4L2_TUNER_SUB_LANG1`, `V4L2_TUNER_SUB_LANG2`, and `V4L2_TUNER_SUB_MONO`.

## Risks And Test Signals
Risks include unvalidated frequency constants, integer approximation error, FIFO sampling assumptions, false positives from noise thresholds, unsupported BTSC SAP/stereo, and dependence on RDS FIFO enablement. Comments note several frequencies are from a reference driver and probably need testing/adjustment. Test signals are correct stereo/dual/mono detection on known PAL BG/DK, A2M, and EIAJ broadcasts, stable results after the 500 ms settling period, no allocation failures under polling, and no regressions in unsupported modes where `UNSET` is expected.
