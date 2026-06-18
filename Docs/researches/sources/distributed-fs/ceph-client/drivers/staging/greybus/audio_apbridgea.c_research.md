# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.c

## Purpose

`audio_apbridgea.c` is a helper library for the special APBridgeA audio-control protocol. It sends APBridgeA-specific host-device requests for I2S configuration, CPort registration, data-size setup, TX/RX prepare/start/stop/shutdown.

## Important APIs, Types, and Functions

Exported functions include `gb_audio_apbridgea_set_config()`, register/unregister CPort, set TX/RX data size, prepare/start/stop/shutdown TX, and prepare/start/stop/shutdown RX. Each function fills a packed request from `audio_apbridgea.h` and sends it through `gb_hd_output()` with `GB_APB_REQUEST_AUDIO_CONTROL`.

## Control Flow

Callers pass a Greybus data connection and I2S port. The helper converts multi-byte fields to little endian, sets the APBridgeA request type, and performs a synchronous host-device output. Registering a CPort first takes a runtime PM reference on the bundle; unregistering releases it with autosuspend after the request.

## State and Persistence Behavior

The file stores no state. APBridgeA and runtime PM state live in the Greybus core, APBridgeA firmware, and caller-owned stream state arrays.

## Dependencies and Integration Points

It depends on Greybus host-device output, runtime PM helpers, APBridgeA request definitions, and audio codec/module callers that sequence it during ASoC PCM and DAPM events.

## Risks and Edge Cases

Runtime PM get/put is asymmetric by design across register/unregister; any error after register but before unregister can leave a PM reference unless higher layers clean up. The helpers do not validate port, format, rate, or size values. `gb_audio_apbridgea_register_cport()` returns immediately on PM get failure without a put, which is correct only if failed gets do not acquire references.

## Test Signals

Mock `gb_hd_output()` to verify request type, endian conversion, direction, timestamp, and size. Exercise register/unregister failure paths, PM autosuspend balance, and full TX/RX stream sequences from the codec.
