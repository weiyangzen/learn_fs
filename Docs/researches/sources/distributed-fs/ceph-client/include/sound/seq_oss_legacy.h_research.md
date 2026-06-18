<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_oss_legacy.h -->
# sources/distributed-fs/ceph-client/include/sound/seq_oss_legacy.h

## Purpose
`seq_oss_legacy.h` provides legacy OSS sequencer compatibility definitions that may be missing from some `linux/soundcard.h` versions.

## Important APIs, types, and functions
It includes `linux/soundcard.h` and conditionally defines `SAMPLE_TYPE_AWE32` as `0x20`.

## Control flow
There is no runtime flow. Consumers include the header to compile against a stable legacy OSS macro surface.

## State and persistence behavior
The header has no state.

## Dependencies and integration points
It integrates ALSA sequencer OSS emulation and legacy sample/patch handling with the kernel soundcard compatibility header.

## Risks and test signals
Risks are minimal but include macro redefinition conflicts or assumptions that other legacy constants are present. Test signals are build coverage with different soundcard header variants and OSS AWE32 patch/sample paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_oss_legacy.h -->
