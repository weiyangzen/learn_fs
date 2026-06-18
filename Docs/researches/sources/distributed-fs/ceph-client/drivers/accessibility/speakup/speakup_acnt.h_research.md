# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_acnt.h

## Purpose
Shared constants for Accent synthesizer drivers.

## Important APIs, Types, And Functions
Defines `DRV_VERSION`, `SYNTH_CLEAR`, and `PROCSPEECH`; declares no functions or structs.

## Control Flow
No executable flow. `speakup_acntpc.c` and `speakup_acntsa.c` consume these constants in synth descriptors and output/flush handling.

## State And Persistence Behavior
No state is stored; constants influence runtime clear and process-speech commands.

## Dependencies, Integration Points, Risks, And Test Signals
Has only an include guard. Changing values impacts both Accent drivers. Test build and device flush/process-speech behavior for Accent PC and Accent SA.
