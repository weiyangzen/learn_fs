# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.c

## Purpose
This file implements the HD-audio side-codec component manager used by HDA codec drivers to bind external amplifier component devices. It centralizes component matching, bind/unbind orchestration, playback hook fanout, and optional ACPI notification fanout.

## Important APIs, types, and functions
Exported APIs are `hda_component_acpi_device_notify()`, `hda_component_manager_bind_acpi_notifications()`, `hda_component_manager_unbind_acpi_notifications()`, `hda_component_manager_playback_hook()`, `hda_component_manager_bind()`, `hda_component_manager_init()`, and `hda_component_manager_free()`. `struct hda_scodec_match` carries bus/HID/match format/index data for component matching. `hda_comp_match_dev_name()` performs relaxed device-name matching by bus prefix, optional bus number, and formatted HID/index suffix.

## Control flow
`hda_component_manager_init()` initializes the parent, creates one match object per expected component, registers match callbacks with the component framework, and adds a component master on the HDA codec device. `hda_component_manager_bind()` clears component slots and calls `component_bind_all()` under the parent mutex. Playback hooks are fanned out in three ordered passes: all pre hooks, then all main hooks, then all post hooks. ACPI notification setup checks whether any component requests notifications and, if so, installs one handler on the first component ACPI device; notification dispatch loops over components and calls their per-device callback.

## State and persistence
State lives in caller-owned `struct hda_component_parent`: a mutex, codec pointer, and fixed array of component slots. Component drivers fill slots during their component bind callbacks. The manager owns no heap state except devm-allocated match data tied to the HDA codec device. `hda_component_manager_free()` removes the component master and clears `parent->codec`.

## Dependencies and integration points
It depends on Linux component framework, ACPI, HDA codec APIs, mutex cleanup guards, and local `hda_component.h`/`hda_local.h`. Side-codec drivers such as CS35L56 and TAS2781 fill `struct hda_component` fields with device pointers, names, playback hooks, and ACPI notification handlers.

## Risks and edge cases
Device-name matching is intentionally relaxed but still string-format dependent; bus naming changes can prevent component bind. ACPI notification install failures are logged as warnings but return success, so callers must tolerate missing notifications. Playback fanout holds the mutex while invoking callbacks, so callbacks should avoid re-entering manager operations or blocking indefinitely. The fixed `HDA_MAX_COMPONENTS` limit requires callers to keep count within array size.

## Test signals
Test component master init/bind/free for 1-4 amps, correct relaxed matching for I2C/SPI names, ordered playback hook calls, ACPI notification install/remove and dispatch, duplicate bind rejection in component drivers, and clean unbind when side-codec devices disappear.
