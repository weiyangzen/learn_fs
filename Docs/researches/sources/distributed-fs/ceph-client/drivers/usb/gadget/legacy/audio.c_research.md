# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/audio.c

## Purpose

`audio.c` implements the legacy `g_audio` composite gadget. Depending on build options it exposes UAC2, modern UAC1, or legacy UAC1 audio function support with module parameters for channel masks, sample rates, sample sizes, endpoint intervals, or legacy PCM device names and buffers.

## Important APIs, Types, and Functions

Key functions are `audio_bind()`, `audio_do_config()`, and `audio_unbind()`. The driver obtains `"uac2"`, `"uac1"`, or `"uac1_legacy"` function instances, fills their option structures (`f_uac2_opts`, `f_uac1_opts`, or `f_uac1_legacy_opts`), allocates string IDs, creates optional OTG descriptors, and adds a single configuration.

## Control Flow

Module parameters are selected by preprocessor branch. Bind obtains the chosen audio function instance, copies parameter values into the instance options, allocates manufacturer/product string IDs, optionally builds an OTG descriptor, and registers `audio_config_driver`. The config callback gets one concrete audio function and adds it. Unbind releases the concrete function, function instance, and OTG descriptor.

## State and Persistence Behavior

Configuration state is global module-parameter state plus the selected function instance options. Runtime audio streaming state is owned by the lower-level UAC function and ALSA virtual-card helpers. This file persists nothing outside module parameters and kernel memory.

## Dependencies and Integration Points

The file depends on libcomposite, UAC option headers, ALSA/PCM infrastructure selected by Kconfig, USB string assignment, OTG descriptor helpers, and composite overwrite parameters. It integrates with host USB Audio Class drivers and exposes a virtual ALSA path through the function implementation.

## Risks and Test Signals

Risks include invalid sample-rate arrays, branch-specific option drift, failed string/OTG allocation unwinds, and differences between UAC1 legacy and non-legacy descriptor behavior. Tests should build all three mode combinations, enumerate on host audio stacks, validate playback/capture with requested channel/rate/sample-size settings, test HS bInterval parameters for UAC2, and unload after active audio streaming.
