# sources/distributed-fs/ceph-client/sound/usb/line6/capture.h

## Purpose
Declares Line 6 capture callbacks and helper functions.

## APIs and Integration
Exposes `snd_line6_capture_ops` for PCM registration, capture copy/period helpers for capture processing, and URB creation/submission functions used by `pcm.c` stream startup and initialization.

## State, Dependencies, and Risks
All APIs operate on `struct snd_line6_pcm`, whose stream fields must already be initialized. Callers must hold `line6pcm->in.lock` for submission paths as documented in the implementation.

## Test Signals
Build coverage and capture stream start/stop tests validate header contracts.
