# sources/distributed-fs/ceph-client/sound/soc/codecs/es83xx-dsm-common.h

## Purpose

This header documents and defines the ACPI DSM argument IDs and returned values used by Everest Semi ES83xx platform firmware, plus prototypes for the shared DSM helper functions.

## Important APIs, types, and functions

The exported function prototypes are `es83xx_dsm()` and `es83xx_dsm_dump()`. The rest of the file defines DSM argument IDs for platform topology, microphone type, speaker type, jack detect polarity, PCM type, codec type, bus slot, ADC/PGA/ALC settings, DAC volumes, automute, GPIO function, and platform clock frequency. It also defines value enums for DMIC/AMIC wiring, speaker topology, jack polarity, codec variants, line-in gain, ADC GUI steps, D2SE PGA gain, ALC targets/min/max/hold/decay/attack/noise gate, DAC HPMIX/HPOUT levels, automute modes, mono/stereo hints, and GPIO levels.

## Control flow

There is no execution flow in the header. Callers use argument IDs with `es83xx_dsm()` and map returned integer values into codec register fields or topology decisions.

## State and persistence behavior

This file does not store state. It encodes the firmware contract that downstream drivers may cache after querying ACPI. Some comments explicitly note values that Linux currently does not use or that are Windows-specific.

## Dependencies and integration points

It depends only on `struct device` being visible to callers. It integrates ACPI firmware descriptions with ES83xx codec drivers and Intel/SOF-style machine drivers that need board-specific microphone, gain, and routing information.

## Risks and test signals

Risks include duplicated argument IDs (`MAIN_CODEC_ADC_GUI_STEP_ARG` and `MAIN_CODEC_ADC_GUI_GAIN_RANGE_ARG` both use `0x2c`), comments that may not match actual firmware units, and Linux drivers treating Windows-specific values as authoritative. Useful validation is a DSM dump on target laptops, range checks before register writes, and comparison with topology/NHLT-derived bus settings.
