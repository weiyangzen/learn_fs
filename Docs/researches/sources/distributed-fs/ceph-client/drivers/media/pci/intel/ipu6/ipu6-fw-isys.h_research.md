# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.h

## Purpose
This header defines the IPU6 ISYS firmware ABI: queue layout, stream sources, command/response types, frame formats, pin descriptors, stream configuration, frame buffer payloads, error records, and command/response queue tokens.

## Important APIs, types, and definitions
Constants define maximum input/output pins, stream IDs for IPU6/IPU6SE, queue bases and counts, retry/timeouts, sensor-type ranges, and pin-plane limits. Enums define response types, send command types, queue types, stream sources, CSI-2 virtual channels, firmware frame formats, pin types, MIPI store/capture/sensor modes, and firmware/proxy errors. ABI structs include `ipu6_fw_isys_fw_config`, input/output pin info, stream config, frame buffer set, response info, proxy response, and send/receive/proxy queue tokens. Public functions initialize/close/cleanup ISYS firmware communication, send simple/complex/proxy commands, get/put responses, and dump configs.

## Control flow and integration points
`ipu6-fw-isys.c` fills and sends these structures. ISYS queue/video code builds stream and frame-buffer payloads from V4L2 media graph state and capture buffers. Firmware responses identified by `ipu6_fw_isys_resp_type` drive buffer completion, SOF/EOF events, stream command acknowledgements, and error reporting.

## State, persistence, and dependencies
The header encodes shared memory layout between host and firmware, so field order and sizes are persistent ABI. It depends only on Linux types and forward declarations, but consumers depend on these definitions being identical to firmware.

## Risks and test signals
Risks include ABI drift, wrong queue base calculations, unsupported frame-format mapping, stream ID overflow, bad pin counts, and mismatched response interpretation. Test signals are firmware open/start/capture/stop across IPU6 and IPU6SE variants, response decoding for all expected types, multi-stream queue routing, and negative tests for firmware-reported errors.
