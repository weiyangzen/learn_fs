# sources/distributed-fs/ceph-client/drivers/s390/cio/device_id.c

Purpose: performs CCW device SENSE ID discovery and normalizes returned control-unit/device identity data for the device FSM.

Important APIs/types/functions: `ccw_device_sense_id_start()` builds a SENSE ID CCW in the device DMA area and starts it through the internal `ccw_request` engine. `snsid_init()`, `snsid_check()`, and `snsid_callback()` validate response length, `reserved == 0xff`, CU type, and extended CIW availability. On z/VM, `diag210_get_dev_info()` and `diag210_to_senseid()` provide a fallback mapping for older virtual devices.

Control flow: SENSE ID setup clears the DMA `senseid` buffer, places `0xffff` as an incomplete sentinel, configures timeout/retry/path mask, and calls `ccw_request_start()`. The request check restarts incomplete responses with `-EAGAIN`, marks extended sense ID when CIWs are present, or rejects incompatible payloads. The callback may retry via DIAG 0x210 on VM and then completes through `ccw_device_sense_id_done()`.

State and persistence behavior: state is transient in `cdev->private->dma_area->senseid`, `flags.esid`, and the internal request. `ccw_device_update_sense_data()` in the FSM later copies it into persistent in-memory `cdev->id` for driver matching. No persistent storage is written.

Dependencies and integration points: relies on `io_sch.h` DMA layout, `ccw_request_start()`, SENSE ID command definitions, `machine_is_vm()`, `diag210()`, CIO tracing, and FSM completion.

Risks and test signals: incomplete or malformed SENSE ID can loop until retry exhaustion; VM fallback mappings must stay accurate for common virtual devices such as OSA and printers. Test real and VM paths, SSID nonzero rejection for DIAG 0x210, extended CIW detection, incompatible `reserved` values, timeout to boxed state, and retry behavior for short responses.
