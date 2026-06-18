# sources/distributed-fs/ceph-client/sound/usb/fcp.h

## Purpose
Declares the Focusrite Control Protocol integration point for USB mixer setup.

## API and Integration
`snd_fcp_init(struct usb_mixer_interface *mixer)` initializes private protocol state, discovers the Focusrite vendor interface, and registers the hwdep device when applicable. The caller must provide a mixer with a valid `chip`, protocol, and mixer lifetime hooks.

## State, Dependencies, and Risks
State is allocated by `fcp.c` and attached to `mixer->private_data`; this header only exposes the entry point. Risk centers on calling it for unsupported or non-UAC2 mixer contexts, though `fcp.c` exits early for missing protocol and validates the vendor-specific interface.

## Test Signals
Build coverage plus probing Focusrite and non-Focusrite devices validates correct no-op and initialization behavior.
