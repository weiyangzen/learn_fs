# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_module.c

## Purpose

`audio_module.c` is the Greybus Audio class bundle driver. It discovers management and data CPorts, creates Greybus connections, handles asynchronous audio events, fetches/parses topology, registers the module with the ASoC codec and audio manager, and tears everything down on disconnect.

## Important APIs, Types, and Functions

Important helpers are `gbaudio_request_jack()`, `gbaudio_request_button()`, `gbaudio_request_stream()`, `gbaudio_codec_request_handler()`, `gb_audio_add_mgmt_connection()`, `gb_audio_add_data_connection()`, `gb_audio_probe()`, and `gb_audio_disconnect()`. It also defines runtime PM suspend/resume callbacks for connection disable/enable.

## Control Flow

Probe requires at least two CPorts, allocates `gbaudio_module_info`, initializes lists, creates one management connection with a request handler and one or more offloaded data connections, enables management, fetches topology, parses it, enables data connections, registers the module with the codec, creates an audio-manager entry, and autosuspends the bundle. Incoming management events are dispatched by Greybus operation type to stream, jack, or button handlers. Disconnect resumes the bundle, unregisters the codec module, removes manager entry, releases topology, disables/destroys connections, and frees module state.

## State and Persistence Behavior

Per-module state includes connection lists, topology-derived ASoC objects, jack/button status, manager ID, device masks, and module identity. It is volatile and tied to Greybus bundle lifetime.

## Dependencies and Integration Points

The file integrates with Greybus bundle/connection APIs, offloaded CSD data connections, runtime PM, topology parser, ASoC codec registration, and audio manager registry.

## Risks and Edge Cases

All data connections get `dai->id = 0`, so multiple data CPorts are not distinguished. `gb_pm_runtime_put_autosuspend()` is called after successful probe without an obvious matching get in this function, relying on Greybus probe/runtime conventions. On disconnect, return values from unregister/remove/disable are mostly ignored. Jack/button event handlers trust topology-created jack objects and reject events if no jack is active; button IDs are limited to 1-4.

## Test Signals

Test bundles with missing management, no data, multiple data CPorts, unsupported protocols, topology fetch/parse failures, data enable failures, event delivery before and after jack registration, unplug while streaming, runtime suspend/resume, and manager add failure behavior.
