# sources/distributed-fs/ceph-client/sound/usb/endpoint.h

## Purpose
Declares the generic USB-audio endpoint lifecycle and streaming API used by PCM, implicit feedback, and setup code.

## APIs and Integration
The header defines endpoint types `SND_USB_ENDPOINT_TYPE_DATA` and `SND_USB_ENDPOINT_TYPE_SYNC`. It exposes functions to add/find endpoints, open/close them for a selected `audioformat`, set parameters, prepare interface/rate state, link sync endpoints, install data callbacks, start/stop/suspend/release/free endpoints, query shared clock rates, test compatibility, compute packet sizes, and queue pending output URBs. PCM code owns prepare/retire callbacks; endpoint code owns bus submission and feedback.

## State, Dependencies, and Risks
The functions operate on `struct snd_usb_audio`, `struct audioformat`, `struct snd_usb_endpoint`, `struct snd_usb_substream`, and ALSA hw params. Callers must respect lifecycle order: add, open, set params, prepare, set callbacks, start, stop, sync stop, close/release. Misordered calls can leave NULL interface refs, unmatched running refs, or active URBs during teardown.

## Test Signals
Compile-time inclusion by generic PCM code and runtime coverage of hw_params/prepare/trigger/hw_free paths are the main signals. Implicit feedback and shared-clock devices test the more subtle compatibility and sync APIs.
